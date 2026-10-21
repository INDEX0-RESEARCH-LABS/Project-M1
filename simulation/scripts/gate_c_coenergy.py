"""Co-energy torque arbiter — settles the single vs multi-ring extractor question.

Per validation/gate_c_search/RESULT.md follow-up and D-011: the single-ring and
9-ring Maxwell extractors disagree by 25-30% at deep saturation on the SAME solution.
This script computes the torque independently as the co-energy derivative,

    T = -dW'/dδ     (constant-current, finite difference over δ +/- 1 deg, per metre)

with W' = integral of magnetic energy density w(|B|) over the whole cross-section,
w from the same B-H table the solver uses (air: B^2/(2 mu0); iron: integral of H dB).

Verdict rule (declared before running): whichever Maxwell extractor agrees with the
co-energy value within 15% becomes the campaign standard; if neither does, absolute
torque keeps a +/-25-30% label until a better extractor exists.

Run:  .venv/bin/python simulation/scripts/gate_c_coenergy.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from rajini_anchor import (AIRGAP, BORE, FILL, J_CU, L_STACK, N_SLOTS, SHAFT_OD,
                           STATOR_OD, d_pattern, split_slots, tri_areas)
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh

MU0 = 4e-7 * math.pi
DELTA_DEG = 1.0                     # FD step
CONFIG = dict(span=0.012, frac=0.62, bridge=0.0006, deg=26.25)   # the D-010 baseline


def w_table(H: np.ndarray, B: np.ndarray) -> dict:
    """Energy density table w(B): w = ∫0^B H(b) db over the tabulated range,
    with H(b) extended linearly beyond using the last table segment's slope."""
    order = np.argsort(B)
    Bs, Hs = B[order].astype(float), H[order].astype(float)
    # prepend the origin (H(0)=0 for our curves); guard for rows already at 0
    if Bs[0] > 0:
        Bs = np.concatenate(([0.0], Bs))
        Hs = np.concatenate(([0.0], Hs))
    bs = Bs
    w_tab = np.concatenate(([0.0], np.cumsum(0.5 * (Hs[1:] + Hs[:-1]) * np.diff(bs))))
    slope = (Hs[-1] - Hs[-2]) / max(Bs[-1] - Bs[-2], 1e-12)
    return {"bs": bs, "w": w_tab, "b_end": Bs[-1], "w_end": w_tab[-1],
            "h_end": Hs[-1], "slope": slope}


def w_of_arr(bmag: np.ndarray, table: dict) -> np.ndarray:
    """Vectorised w(|B|): table lookup + linear-H extension beyond the table end."""
    w = np.interp(bmag, table["bs"], table["w"])
    over = bmag > table["b_end"]
    if over.any():
        b = bmag[over] - table["b_end"]
        w[over] = table["w_end"] + (table["h_end"] * b
                                    + 0.5 * table["slope"] * b**2)
    return w


def solve_and_energy(g: SynRMGeometry, mesh_kw: dict, table: dict) -> dict:
    H, B = load_bh_curve("M-43 Steel")
    mesh, sub, _ = build_mesh(g, **mesh_kw)
    sg = split_slots(mesh, sub)
    areas = tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    pat = d_pattern()
    jz = {f"slot_{k:02d}": pat[k] * J_CU * FILL for k in range(N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cs = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    sol = solve_az_core(mesh, cs, materials, jz)

    tri = mesh.t
    bx = sol["Bx"][tri].mean(axis=0)
    by = sol["By"][tri].mean(axis=0)
    bmag = np.hypot(bx, by)
    iron_names = ("stator_iron", "rotor_iron", "shaft")
    mask = np.zeros(tri.shape[1], dtype=bool)
    for name in iron_names:
        c = sub.get(name)
        if c is not None and c.size:
            mask[c] = True
    w = np.where(mask, w_of_arr(bmag, table), bmag**2 / (2 * MU0))
    W = float((w * areas).sum())          # J per metre of stack
    r_gap = (BORE / 2 + g.rotor_od / 2) / 2
    hg = BORE / 2 - g.rotor_od / 2
    t1 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    t9 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880, n_rings=9, r_spread=0.5 * hg)
    return {"W": W, "T_single": t1, "T_multi": t9,
            "conv": bool(sol["converged"]),
            "Bmax": float(bmag.max())}


def main() -> None:
    H, B = load_bh_curve("M-43 Steel")
    table = w_table(H, B)
    span, frac, bridge, deg0 = (CONFIG["span"], CONFIG["frac"],
                                CONFIG["bridge"], CONFIG["deg"])
    out = {}
    for sgn, tag in ((-1, "minus"), (+1, "plus")):
        deg = deg0 + sgn * DELTA_DEG
        g = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                          airgap=AIRGAP, shaft_od=SHAFT_OD,
                          barrier_radial_span=span, n_barriers=2,
                          barrier_angle_frac=frac, bridge=bridge,
                          barrier_center_angle=math.pi / 4 + math.radians(deg))
        out[tag] = solve_and_energy(g, dict(n_theta=3072, n_gap_rows=4), table)
        o = out[tag]
        print(f"delta={deg:5.2f}: W'={o['W']:.3f} J/m  T_single={o['T_single']:+.4f}  "
              f"T_multi={o['T_multi']:+.4f}  conv={o['conv']}", flush=True)

    dw = out["plus"]["W"] - out["minus"]["W"]
    t_co = -dw / (2 * math.radians(DELTA_DEG))          # N.m per metre
    t_single = 0.5 * (abs(out["plus"]["T_single"]) + abs(out["minus"]["T_single"]))
    t_multi = 0.5 * (abs(out["plus"]["T_multi"]) + abs(out["minus"]["T_multi"]))
    print(f"\nco-energy torque T = {t_co:+.4f} N.m/m   (|T| = {abs(t_co):.4f})")
    print(f"  vs single-ring  {t_single:+.4f}  -> diff {(t_co-t_single)/abs(t_co):+.1%}")
    print(f"  vs multi9-ring  {t_multi:+.4f}  -> diff {(t_co-t_multi)/abs(t_co):+.1%}")
    ok_s = abs(t_co - t_single) / abs(t_co) <= 0.15
    ok_m = abs(t_co - t_multi) / abs(t_co) <= 0.15
    print("VERDICT:", "single-ring" if ok_s and not ok_m else
          "multi9-ring" if ok_m and not ok_s else
          "both" if ok_s and ok_m else "NEITHER (abs torque keeps +/-25-30% label)")
    # midpoint sanity: W' should rise with |excitation| but must be smooth in delta
    print(f"sanity: |W'(plus)-W'(minus)|/mean = "
          f"{abs(dw) / (0.5*(out['plus']['W']+out['minus']['W'])):.2%} "
          f"(small = symmetric-point smoothness ok)")


if __name__ == "__main__":
    main()
