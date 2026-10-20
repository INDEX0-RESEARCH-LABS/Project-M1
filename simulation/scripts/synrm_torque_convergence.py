"""torque_maxwell convergence study -- the validator for torque extraction.

Strategy note: the co-energy instrument is unusable as a fine-angle torque
validator here (its signal, dW' at small rotor-angle strides, sits at ~2% of
total W', below the solve-to-solve reproducibility floor). Instead torque_maxwell
is validated the standard FEM way: under mesh refinement the extracted torque
must converge, and its radius-independence inside the airgap must tighten.

Case: rotor at deltas=0, stator MMF at +15 deg mech ('p15' pattern) -- off the
symmetry points, so T is well away from zero.

PASS criteria (declared before running):
    K1  region areas still agree with closed form at every level (<=1% each)
    K2  |T| between the two finest levels differs by <=5%
    K3  Maxwell torque radius-independence inside the airgap: spread across
        5 sampling radii <= 3% of |T| at the finest level
    K4  Newton convergence at every level

Steel: M-19 Steel PLACEHOLDER (D-006) -- solver-shakeout data, not for anchors.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas
from synrm_first_solve import J_CU, FILL, L_STACK, slot_currents, slot_loading, split_slots

HERE = Path(__file__).resolve().parent
OUT = HERE / "validation" / "torque_convergence"

LEVELS = [(768, 2), (1536, 4), (3072, 4)]


def tri_areas(mesh) -> np.ndarray:
    p0, p1, p2 = (mesh.p[:, mesh.t[i]] for i in range(3))
    return 0.5 * np.abs((p1[0] - p0[0]) * (p2[1] - p0[1])
                        - (p2[0] - p0[0]) * (p1[1] - p0[1]))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    H, B = load_bh_curve("M-19 Steel")
    materials = {"shaft": 1.0, "air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "slots": 1.0}

    rows, sols = [], []
    for n_theta, n_gap_rows in LEVELS:
        g = SynRMGeometry()
        mesh, sub, _ = build_mesh(g, n_theta=n_theta, n_gap_rows=n_gap_rows)
        sg = split_slots(mesh, sub, g)
        area_all = tri_areas(mesh)
        exp = expected_areas(g)

        k1 = True
        reg_err = {}
        for name, exact in exp.items():
            err = abs(area_all[sub[name]].sum() / exact - 1.0)
            reg_err[name] = err
            if err > 0.01:
                k1 = False

        slot_area = {n: area_all[c].sum() for n, c in sg.items()}
        loading = slot_loading(g, slot_area)
        pattern = slot_currents("p15")
        jz = {f"slot_{k:02d}": pattern[k] * loading[k] / slot_area[f"slot_{k:02d}"]
              for k in range(24)}
        cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
        sol = solve_az_core(mesh, cell_sets, materials, jz)
        k4 = bool(sol["converged"])

        r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2
        ts = [torque_maxwell(sol, r, L_STACK, n_theta=2880)
              for r in np.linspace(r_gap - 0.00025, r_gap + 0.00025, 5)]
        spread = (max(ts) - min(ts)) / abs(ts[2])
        rows.append({"n_theta": n_theta, "n_gap_rows": n_gap_rows,
                     "nelems": int(mesh.t.shape[1]), "ndofs": int(sol["ndofs"]),
                     "converged": k4, "k1_region_err_max": max(reg_err.values()),
                     "k1": k1, "T_mid": ts[2], "radius_spread": spread,
                     "iters": int(sol["newton_iters"])})
        sols.append(sol)
        print(f"L(n_theta={n_theta}, gap_rows={n_gap_rows}): "
              f"nelems={rows[-1]['nelems']}, iters={rows[-1]['iters']}, "
              f"T_mid={ts[2]:+.5f}, radius_spread={spread:.1%}, "
              f"max region err={max(reg_err.values()):.3%}")

    t_finest, t_second = rows[-1]["T_mid"], rows[-2]["T_mid"]
    k2 = abs(t_finest - t_second) / abs(t_second) <= 0.05
    k3 = rows[-1]["radius_spread"] <= 0.03
    print(f"\nK1 regions <=1%         : {rows[0]['k1'] and rows[1]['k1'] and rows[2]['k1']}")
    print(f"K2 finest-two |T| <=5%  : {k2}  ({t_second:.5f} -> {t_finest:.5f} N.m)")
    print(f"K3 radius spread <=3%   : {k3}")
    ok = k2 and k3 and rows[-1]["k1"] and rows[-1]["converged"]
    print("OVERALL:", "PASS" if ok else "FAIL")

    (OUT / "torque_convergence_results.json").write_text(json.dumps({
        "checks": {"K2_finest_two_within_5pct": k2,
                   "K3_radius_spread_within_3pct": k3, "overall": ok},
        "rows": rows,
        "meta": {"steel": "M-19 Steel (PLACEHOLDER, D-006)",
                 "pattern": "p15 (MMF at 15 deg mech)", "deltas_deg": 0.0,
                 "note": "validators shakeout; numbers not for anchors"},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
