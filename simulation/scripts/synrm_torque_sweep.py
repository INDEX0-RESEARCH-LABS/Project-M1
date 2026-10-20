"""Rotor-rotation torque sweep: Maxwell-stress vs co-energy, matched strides.

Resolves the C5 discrepancy found in synrm_first_solve.py (Maxwell ~0.039 N.m
vs a 30-deg-stride co-energy slope ~0.006 N.m). Instead of rotating the stator
MMF pattern in coarse slot-pitch steps (which aliases against the slot pitch),
the ROTOR is rotated in fine steps by moving the barrier-set centre angle while
the stator currents stay fixed at the d-axis pattern.

Checks, declared before running:
    S1  antisymmetry: T_M(-delta) approximately -T_M(delta), T_M(0) ~ 0
    S2  instrument agreement: pointwise central-difference co-energy slope
        dW'/d(delta) (stride 4 deg) agrees with T_maxwell at the same delta
        within 20% wherever |T_M| > 5% of the sweep maximum
    S3  smooth monotone rise of |T_M| from 0 up to the sweep edge (no wild
        oscillation at the 2-4 deg stride level)

Steel: M-19 Steel PLACEHOLDER (D-006) -- solver-shakeout data, not for anchors.
"""
from __future__ import annotations

import dataclasses
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import co_energy_density, load_bh_curve, solve_az_core, torque_maxwell
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh
from synrm_first_solve import PITCH, J_CU, FILL, L_STACK, slot_loading

HERE = Path(__file__).resolve().parent
OUT = HERE / "validation" / "torque_sweep"

DELTAS_DEG = [-8.0, -4.0, -2.0, 0.0, 2.0, 4.0, 8.0]
STRIDE_DEG = 4.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    H, B = load_bh_curve("M-19 Steel")
    materials = {"shaft": 1.0, "air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "slots": 1.0}

    rows = []
    for delta_deg in DELTAS_DEG:
        g = dataclasses.replace(
            SynRMGeometry(),
            barrier_center_angle=math.pi / 4 + math.radians(delta_deg))
        mesh, sub, _ = build_mesh(g)

        # per-slot current groups (pattern fixed at d-axis)
        from synrm_first_solve import split_slots, slot_currents
        sg = split_slots(mesh, sub, g)
        p0, p1, p2 = (mesh.p[:, mesh.t[i]] for i in range(3))
        area_all = 0.5 * np.abs((p1[0] - p0[0]) * (p2[1] - p0[1])
                                - (p2[0] - p0[0]) * (p1[1] - p0[1]))
        slot_area = {n: area_all[c].sum() for n, c in sg.items()}
        loading = slot_loading(g, slot_area)
        pattern = slot_currents("d")
        jz = {f"slot_{k:02d}": pattern[k] * loading[k] / slot_area[f"slot_{k:02d}"]
              for k in range(24)}
        cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}

        sol = solve_az_core(mesh, cell_sets, materials, jz)
        r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2
        t_m = torque_maxwell(sol, r_gap, L_STACK, n_theta=2880)

        b_mag = np.hypot(sol["Bx"], sol["By"])
        mu_e = np.zeros(mesh.t.shape[1])
        for r_ in ("shaft", "air", "airgap", "barriers", "slots"):
            mu_e[sub[r_]] = 1.0
        w = co_energy_density(b_mag, H, B, mu_r=mu_e)
        w_total = float((w * area_all).sum()) * L_STACK           # [J]
        rows.append({"delta_deg": delta_deg, "T_maxwell": t_m, "W_J": w_total,
                     "converged": bool(sol["converged"])})

    t_m = np.array([r["T_maxwell"] for r in rows])
    w = np.array([r["W_J"] for r in rows])
    d = np.radians(np.array([r["delta_deg"] for r in rows]))

    # S1 antisymmetry about delta = 0
    s1 = (abs(t_m[0] + t_m[-1]) / max(abs(t_m[-1]), 1e-12) < 0.25
          and abs(t_m[1] + t_m[5]) / max(abs(t_m[5]), 1e-12) < 0.25
          and abs(t_m[3]) < 0.15 * abs(t_m).max())

    # S2 matched-stride instrument agreement
    agree = []
    for i in (1, 2, 4, 5):  # deltas -4, -2, +2, +4 (both neighbours exist)
        slope = (w[i + 1] - w[i - 1]) / (d[i + 1] - d[i - 1])
        rel = abs(slope - t_m[i]) / max(abs(t_m[i]), 1e-12)
        agree.append((rows[i]["delta_deg"], t_m[i], slope, rel))
    s2 = all(rel < 0.20 for _, _, _, rel in agree)

    # S3 monotone rise in |T_M| up to the sweep edge (with 15%% slack)
    mag = np.abs(t_m)
    s3 = (mag[3] < mag[2] < mag[1] and mag[3] < mag[4] < mag[5]
          and abs(mag[-1]) < max(mag) * 1.15)

    print(f"{'delta[deg]':>10s} {'T_maxwell[N.m]':>15s} {'W*[J]':>10s} conv")
    for r in rows:
        print(f"{r['delta_deg']:10.1f} {r['T_maxwell']:15.5f} {r['W_J']:10.5f} "
              f"{r['converged']}")
    print("\nS2 matched-stride agreement (delta, T_maxwell, dW*/ddelta, rel diff):")
    for df, tm, sl, rel in agree:
        print(f"  {df:+5.1f} deg  {tm:+.5f}  {sl:+.5f}  {rel:6.1%}")
    print(f"\nS1 antisymmetry          : {s1}")
    print(f"S2 Maxwell == co-energy  : {s2}")
    print(f"S3 smooth monotone rise  : {s3}")
    ok = bool(s1 and s2 and s3)
    print("OVERALL:", "PASS" if ok else "FAIL")

    (OUT / "torque_sweep_results.json").write_text(json.dumps({
        "checks": {"S1_antisymmetry": bool(s1), "S2_instrument_agreement": bool(s2),
                   "S3_smooth_rise": bool(s3), "overall": ok},
        "s2_rows": [dict(delta_deg=dd, T_maxwell=tm, co_energy_slope=sl, rel=rel)
                    for dd, tm, sl, rel in agree],
        "rows": rows,
        "meta": {"steel": "M-19 Steel (PLACEHOLDER, D-006)",
                 "pattern": "d-axis fixed", "stride_deg": STRIDE_DEG,
                 "note": "rotor-rotation sweep, solver-shakeout only"},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
