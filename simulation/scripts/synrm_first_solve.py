"""First full SynRM machine solve: winding currents + nonlinear solve + torque.

Checks run here (declared before solving):
    C1  nonlinear Newton iteration converges on the full machine mesh
    C2  d-axis alignment (MMF on the pole axis at 0 deg mech): |T| small
    C3  q-axis alignment (MMF at 45 deg mech): |T| small (mirror check of C2)
    C4  mid-angle (15 deg / 30 deg mech): T nonzero, T(15) = -T(30) by symmetry
    C5  Maxwell torque vs energy method at 15 deg:
            T_maxwell(15) ~= -[W(30) - W(0)] / (30 deg in rad)
        with T(0) ~= T(45) ~= 0 also consistent with dW/dtheta.

Steel is M-19 Steel from the FEMM library: a PLACEHOLDER (D-006/D-007 forbid
using M-19 for any anchor comparison). Loading: 6 A/mm^2 copper at 40% slot
fill (Rajini 2024's stated fill factor), stack length 64 mm (Rajini's stated
stack). Numbers from this script are solver-shakeout results, not anchor data.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import (MU0, co_energy_density, load_bh_curve, solve_az_core,
                           torque_maxwell)
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh

HERE = Path(__file__).resolve().parent
OUT = HERE / "validation" / "first_solve"

N_SLOTS = 24
PITCH = 2 * math.pi / N_SLOTS           # 15 deg mech
L_STACK = 0.064                          # stack length [m]
J_CU = 6.0e6                             # copper current density [A/m^2]
FILL = 0.40                              # slot fill factor (Rajini 2024)

# phase belt layout for 24 slots / 4 poles / 3 phases, belts of 2 slots.
# shifted by one slot so the A-belt axis sits at 0 deg mech (= rotor pole axis,
# since synrm_geometry puts pole axes at 0/90/180/270).
PHASE_OF_SLOT = "AACCBB" * 2             # phase letter for slots 0..11 (repeats)
SIGN_OF_SLOT = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]

# slot k centre angle = k*PITCH + PITCH/2.  To put the A-axis (centre of an
# A+ belt) at 0 deg, slots 23 and 0 must be A+, so phase index = (k+1) mod 12.
def slot_phase(k: int) -> tuple[str, int]:
    idx = (k + 1) % 12
    return PHASE_OF_SLOT[idx], SIGN_OF_SLOT[idx]


def slot_currents(kind: str) -> dict[int, float]:
    """Per-slot MMF pattern values (dimensionless) for a stator MMF at the
    given mechanical angle.

    Values are in units of the A-phase slot ampere-turns I_A:
        'd'   (0 deg mech): i_a = I_A, i_b = i_c = -I_A/2
        'q'   (45 deg mech): phase order shifted by 3 slots
        'p15' (15 deg mech): shift by 1 slot
        'm15' (-15 deg mech): shift by -1 slot

    The caller scales by I_A = J_cu * fill * slot_area per slot.
    """
    shift = {"d": 0, "p15": 1, "m15": -1, "q": 3}[kind]
    ia = 1.0
    out: dict[int, float] = {}
    for k in range(N_SLOTS):
        ph, sign = slot_phase(k)
        i_ph = ia if ph == "A" else -ia / 2.0
        out[k] = sign * i_ph
    # rotate the pattern by `shift` slots = shift*15 deg mech
    return {k: out[(k + shift) % N_SLOTS] for k in range(N_SLOTS)}


def slot_loading(g: SynRMGeometry, slot_area: dict[str, float]) -> dict[int, float]:
    """Ampere-turns [A] per slot so every slot's copper sits at J_cu with 'fill'."""
    out = {}
    for k in range(N_SLOTS):
        a = slot_area[f"slot_{k:02d}"]
        out[k] = J_CU * FILL * a
    return out


def split_slots(mesh, subdomains, g: SynRMGeometry) -> dict[str, np.ndarray]:
    """Split the 'slots' element group into per-slot groups by centroid angle."""
    cells = subdomains["slots"]
    ct = mesh.p[:, mesh.t].mean(axis=1)
    th = np.mod(np.arctan2(ct[1][cells], ct[0][cells]), 2 * math.pi)
    k = np.mod(np.floor(th / PITCH).astype(int), N_SLOTS)
    out = {}
    for i in range(N_SLOTS):
        sel = cells[k == i]
        if len(sel):
            out[f"slot_{i:02d}"] = sel
    return out


def magnetic_energy(sol: dict, co_energy: np.ndarray, area: np.ndarray) -> float:
    """W' = sum_e w'_e * area_e  [J/m] (2D, per m depth), from per-element
    co-energy densities (see fem_magnetics.co_energy_density)."""
    return float(np.sum(co_energy * area))


def _tri_area(tri, verts) -> np.ndarray:
    p0, p1, p2 = (verts[:, tri[i]] for i in range(3))
    return 0.5 * np.abs((p1[0] - p0[0]) * (p2[1] - p0[1])
                        - (p2[0] - p0[0]) * (p1[1] - p0[1]))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    g = SynRMGeometry()
    mesh, subdomains, _ = build_mesh(g)
    slot_groups = split_slots(mesh, subdomains, g)
    assert len(slot_groups) == N_SLOTS, f"slot split found {len(slot_groups)} slots"

    # per-slot copper area from the mesh, then J = i / (fill * area)
    area_all = _tri_area(mesh.t, mesh.p)
    slot_area = {n: area_all[cells].sum() for n, cells in slot_groups.items()}

    H, B = load_bh_curve("M-19 Steel")                 # placeholder (D-006)
    materials = {"shaft": 1.0, "air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B),
                 "slots": 1.0}

    results = {}
    sols = {}
    for kind in ("d", "p15", "m15", "q"):
        pattern = slot_currents(kind)
        loading = slot_loading(g, slot_area)
        current_density = {"slot_%02d" % k: (pattern[k] * loading[k])
                           / slot_area[f"slot_{k:02d}"]
                           for k in range(N_SLOTS)}
        # cell_sets for the solver = all regions incl. per-slot splits
        cell_sets = {**{n: c for n, c in subdomains.items() if n != "slots"},
                     **slot_groups}
        sol = solve_az_core(mesh, cell_sets, materials, current_density)
        r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2   # mid-airgap radius
        T = torque_maxwell(sol, r_gap, L_STACK, n_theta=1440)
        bmax = float(np.hypot(sol["Bx"], sol["By"]).max())
        results[kind] = {
            "converged": bool(sol["converged"]),
            "iters": int(sol["newton_iters"]),
            "torque_Nm": T,
            "Bmax_T": bmax,
        }
        sols[kind] = sol

        # W' for the co-energy cross-check: iron along the curve, air linear
        b_mag = np.hypot(sol["Bx"], sol["By"])
        mu_e = np.zeros(mesh.t.shape[1])           # 0 marks "curve-based"
        for air_region in ("shaft", "air", "airgap", "barriers", "slots"):
            mu_e[subdomains[air_region]] = 1.0
        w = co_energy_density(b_mag, H, B, mu_r=mu_e)
        results[kind]["W_J_per_m"] = magnetic_energy(sol, w, area_all)

    c1 = all(r["converged"] for r in results.values())
    scale = max(abs(results["p15"]["torque_Nm"]), 1e-12)
    c2 = abs(results["d"]["torque_Nm"]) < scale * 0.25
    c3 = abs(results["q"]["torque_Nm"]) < scale * 0.25
    t15, t30 = results["p15"]["torque_Nm"], results["m15"]["torque_Nm"]
    c4 = t15 > 0 and t30 < 0 and abs(t15 + t30) / max(abs(t15), 1e-12) < 0.10
    dth = math.radians(30)
    # co-energy cross-check at 15 deg mech: T = dW'/d|_i. W'(psi) = W(-psi) by
    # symmetry, so the central difference around 15 deg uses W(30 deg) (= m15
    # case) and W(0 deg) (= d case). With imposed currents the magnetostatic
    # co-energy numerically equals the field energy 1/2 B^2/nu per element.
    t_energy = ((results["m15"]["W_J_per_m"] - results["d"]["W_J_per_m"])
                * L_STACK) / dth
    rel = abs(t_energy - t15) / max(abs(t15), 1e-12)
    c5 = rel < 0.25

    print(f"{'case':5s} {'conv':5s} {'iters':6s} {'T [N.m]':>10s} {'Bmax [T]':>9s}")
    for kind, r in results.items():
        print(f"{kind:5s} {str(r['converged']):5s} {r['iters']:6d} "
              f"{r['torque_Nm']:10.4f} {r['Bmax_T']:9.3f}")
    print()
    print(f"energy-method T(15deg) = {t_energy:.4f} N.m  vs Maxwell {t15:.4f} "
          f"({rel:.1%} diff)")
    print(f"C1 converged          : {c1}")
    print(f"C2 d-axis |T| small   : {c2}")
    print(f"C3 q-axis |T| small   : {c3}")
    print(f"C4 T(15)=-T(30)       : {c4}  (T15={t15:.4f}, T30={t30:.4f})")
    print(f"C5 Maxwell vs energy  : {c5}")
    ok = c1 and c2 and c3 and c4 and c5
    print("OVERALL:", "PASS" if ok else "FAIL")

    (OUT / "first_solve_results.json").write_text(json.dumps({
        "checks": {"C1_converged": c1, "C2_d_axis_small": c2,
                   "C3_q_axis_small": c3, "C4_antisymmetry": c4,
                   "C5_energy_cross_check": c5, "overall": ok},
        "energy_vs_maxwell": {"t_energy_Nm": t_energy, "rel_diff": rel},
        "per_case": results,
        "meta": {"steel": "M-19 Steel (PLACEHOLDER, D-006)", "J_cu_A_per_mm2": 6.0,
                 "fill": FILL, "stack_m": L_STACK,
                 "note": "solver shakeout only, NOT anchor-comparison data"},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
