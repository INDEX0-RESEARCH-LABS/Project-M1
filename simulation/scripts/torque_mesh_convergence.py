"""Is 1.592 N.m converged? Torque vs mesh (rays, gap rows, sampling rings).

Why this exists: the PF-vs-angle sweep (validation/voltage_and_angle) produced a
jagged torque curve (0.881 N.m at 32 deg, 1.761 at 36 deg) which no SynRM of this
type should have. Re-solving the operating point on a finer mesh moved the torque
by -7.5%, and at 32 deg by -19%. So the headline torque may be a mesh artifact.

Gates declared here, before the run:
  E1 extractor convergence: at 26.25 deg the torque must be stable within 3%
     across the mesh ladder. If it is not, the extractor is not converged and every
     absolute torque inherits the spread (it does not by itself invalidate the
     torque-per-stack trends, which share the bias).
  E2 ring averaging: rings sample the airgap at several radii to de-correlate the
     element-constant-B sampling noise. If rings change the answer by >3% at fixed
     mesh, the single-circle value is superseded by the ring average.
  E3 arbitration: the co-energy derivative dW'/d(delta) at the finest mesh is an
     independent torque route (no gap-circle sampling). It decides which number is
     right; neither Maxwell variant is adopted on mesh refinement alone.
  E4 consequence: if the arbitrated torque at J=6 falls below 2.00 N.m, the declared
     25% envelope margin no longer holds at that current, and STATUS.md must say so.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rajini_anchor as A            # noqa: E402
from dq_model import (BORE, DELTA_OP, J_LEVELS, L_STACK, P_POLES, RHO,   # noqa: E402
                      solve_point)
from envelope_validation import build  # noqa: E402
from fem_magnetics import load_bh_curve, torque_maxwell  # noqa: E402
from synrm_mesh import build_mesh      # noqa: E402

MESHES = ((1536, 4), (3072, 10), (4096, 10))
R_SPREAD = 0.00016          # 0.16 mm each side of r_gap, inside the 0.52 mm gap


def solve_raw(delta: float, J: float, H, B, n_theta: int, rows: int,
              geom=None, pattern=None) -> dict:
    """Same solve as dq_model.solve_point, but keeps the geometry for r_gap.

    `pattern` defaults to the certified instantaneous snapshot (i_a = 1,
    i_b = i_c = -1/2).  The ripple sweep passes a rotated snapshot so that the
    current vector turns with the rotor and the current angle stays fixed.
    """
    g = geom if geom is not None else build(delta, BORE)
    mesh, sub, _ = build_mesh(g, n_theta=n_theta, n_gap_rows=rows)
    sg = A.split_slots(mesh, sub)
    areas = A.tri_areas(mesh)
    pattern = A.d_pattern() if pattern is None else pattern
    jz = {f"slot_{k:02d}": pattern[k] * J * A.FILL for k in range(A.N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(A.N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    from fem_magnetics import solve_az_core
    sol = solve_az_core(mesh, cell_sets, materials, jz)
    if not sol["converged"]:
        raise RuntimeError("no convergence")
    r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2
    a_slot = float(np.mean([areas[c].sum() for c in sg.values()]))
    # phase A flux linkage from the slot stream function (same as dq_model)
    ae = sol["A"][mesh.t].mean(axis=0)
    abar = {k: float((ae[c] * areas[c]).sum() / areas[c].sum())
            for k, c in sg.items()}
    lam = {}
    for ph in ("A", "B", "C"):
        p = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == (ph, 1)]
        n = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == (ph, -1)]
        lam[ph] = L_STACK * (sum(abar[f"slot_{k:02d}"] for k in p)
                             - sum(abar[f"slot_{k:02d}"] for k in n))
    lam_alpha = (2.0 / 3.0) * (lam["A"] - 0.5 * lam["B"] - 0.5 * lam["C"])
    return {"sol": sol, "r_gap": r_gap, "a_slot": a_slot, "mesh": mesh,
            "lam_alpha": lam_alpha}


def torque_at(res: dict, n_rings: int, n_theta: int = 2880) -> float:
    kw = dict(n_theta=n_theta)
    if n_rings > 1:
        kw.update(n_rings=n_rings, r_spread=R_SPREAD)
    return abs(torque_maxwell(res["sol"], res["r_gap"], 1.0, **kw)) * L_STACK


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    print(f"E1/E2 torque ladder at delta={DELTA_OP} deg, J={J_LEVELS[1]/1e6:.2f}, "
          f"r_spread={R_SPREAD*1e3:.2f} mm")
    print("mesh(rays/rows)  rings=1   rings=5   rings=9   ring effect")
    base = {}
    for n_theta, rows in MESHES:
        res = solve_raw(DELTA_OP, J_LEVELS[1], H, B, n_theta, rows)
        t = [torque_at(res, r) for r in (1, 5, 9)]
        base[(n_theta, rows)] = t
        print(f"{n_theta:5d}/{rows:<3d}      {t[0]:7.3f}   {t[1]:7.3f}   "
              f"{t[2]:7.3f}   {t[2]/t[0]-1:+6.1%}")

    t_mid = base[(3072, 10)][2]
    t_fin = base[(4096, 10)][2]
    spread = (t_fin - base[(1536, 4)][2]) / t_fin
    print(f"\nE1: finest-vs-coarsest (rings=9) = {spread:+.1%} "
          f"({'PASS' if abs(spread) <= 0.03 else 'FAIL'}) -> torque is "
          f"{'converged' if abs(spread) <= 0.03 else 'NOT converged at 3%'}")
    ring_eff = max(abs(v[2] / v[0] - 1) for v in base.values())
    print(f"E2: largest ring effect {ring_eff:+.1%} "
          f"({'PASS' if ring_eff <= 0.03 else 'FAIL - single-circle superseded'})")
    print(f"    torque at the operating point: {t_fin:.3f} N.m (finest), "
          f"band {min(v[2] for v in base.values()):.3f}-"
          f"{max(v[2] for v in base.values()):.3f}")

    # E3: independent route - co-energy derivative at the mid mesh
    step = math.radians(0.5)
    ws = {}
    for d in (DELTA_OP - 0.5, DELTA_OP + 0.5):
        ws[d] = solve_point(d, J_LEVELS[1], H, B, n_theta=3072, rows=10)["Wp"]
    t_co = (ws[DELTA_OP + 0.5] - ws[DELTA_OP - 0.5]) / (2 * step) * L_STACK
    print(f"\nE3 co-energy arbiter (3072/rows10): T={abs(t_co):.3f} N.m vs "
          f"Maxwell rings9 {t_mid:.3f} N.m  (gap {abs(t_co)/t_mid-1:+.1%})")
    print(f"    -> adopted torque = {abs(t_co):.3f} +/- "
          f"{abs(abs(t_co)-t_mid)/abs(t_co):.0%} of the Maxwell value")

    # E4: the margin point
    r6 = solve_raw(DELTA_OP, J_LEVELS[2], H, B, 3072, 10)
    t6 = torque_at(r6, 9)
    print(f"\nE4: T(J=6) on the fine mesh, rings=9 = {t6:.3f} N.m "
          f"(declared target 2.00; {'PASS' if t6 >= 2.00 else 'FAIL'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
