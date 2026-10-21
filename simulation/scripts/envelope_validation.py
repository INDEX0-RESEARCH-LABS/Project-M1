"""Envelope validation: 150 mm-bore 4-pole frame at the declared J (see PLAN.md).

Reuses the certified anchor machinery unchanged (pattern, slot split, steel bracket,
single-ring torque extractor at depth 1). Only the geometry scales.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rajini_anchor as A  # noqa: E402
from fem_magnetics import load_bh_curve  # noqa: E402
from synrm_geometry import SynRMGeometry, sanity_checks  # noqa: E402
from synrm_mesh import build_mesh  # noqa: E402

BORE = 0.150
STATOR_OD = 0.217
SHAFT_OD = 0.039
SPAN = 0.012
DELTAS = (22.5, 26.25, 30.0)
TARGET_T_PER_M = 1.6 / 0.074          # 21.6 N.m/m


def build(delta_deg: float, bore: float = BORE) -> SynRMGeometry:
    """Self-similar frame: the 150 mm proportions scale with the bore."""
    k = bore / BORE
    return SynRMGeometry(
        stator_od=STATOR_OD * k, stator_bore=bore, n_slots=A.N_SLOTS,
        airgap=A.AIRGAP, shaft_od=SHAFT_OD * k,
        barrier_radial_span=SPAN * k,
        barrier_angle_frac=0.62, bridge=0.0006,
        barrier_center_angle=math.pi / 4 + math.radians(delta_deg),
    )


def run(delta_deg: float, n_theta: int, rows: int, H, B,
        bore: float = BORE) -> dict:
    g = build(delta_deg, bore)
    mesh, sub, _ = build_mesh(g, n_theta=n_theta, n_gap_rows=rows)
    sg = A.split_slots(mesh, sub)
    areas = A.tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    from synrm_mesh import expected_areas
    err = {}
    exp = expected_areas(g)
    for n, e in exp.items():
        if n in sub and len(sub[n]) > 0 and e > 0:
            err[n] = abs(areas[sub[n]].sum() / e - 1.0)
    c = A.solve_case(g, mesh, sub, sg, slot_area, H, B)
    return {"delta": delta_deg, "bore": bore, "T_per_m": abs(c["T_per_m"]),
            "Bmax": c["Bmax_T"], "iters": c["iters"],
            "conv": c["converged"], "area_err": max(err.values()),
            "slot_area_mm2": float(np.mean(list(slot_area.values())) * 1e6)}


def main() -> int:
    g = build(26.25)
    sc = sanity_checks(g)
    print(f"geometry: bore={BORE*1000:.0f} mm stator_od={STATOR_OD*1000:.0f} mm "
          f"rotor_od={g.rotor_od*1000:.1f} mm span={SPAN*1000:.0f} mm")
    print("sanity:", sc)
    if not sc["all_pass"]:
        return 2
    H, B = load_bh_curve("M-43 Steel")

    coarse = {}
    for d in DELTAS:
        r = run(d, 1536, 4, H, B)
        coarse[d] = r
        print(f"  1536/rows4 delta={d:5.2f}  T/m={r['T_per_m']:7.3f}  "
              f"Bmax={r['Bmax']:.2f}T  area_err={r['area_err']:.2%}  "
              f"conv={r['conv']}  iters={r['iters']}")
        assert r["conv"], f"solve did not converge at delta={d}"
        assert r["area_err"] <= 0.01, f"area check failed at delta={d}"

    best = max(coarse, key=lambda d: coarse[d]["T_per_m"])
    fine = run(best, 3072, 4, H, B)
    print(f"\n  3072/rows4 delta={best:5.2f}  T/m={fine['T_per_m']:.3f}  "
          f"Bmax={fine['Bmax']:.2f}T  area_err={fine['area_err']:.2%}  "
          f"conv={fine['conv']}")
    assert fine["conv"] and fine["area_err"] <= 0.01

    t_per_m = fine["T_per_m"]
    t74 = t_per_m * 0.074
    verdict = ("E1 PASS" if t_per_m >= TARGET_T_PER_M else
               "E2 CLOSE" if t_per_m >= 15.0 else "E3 FAIL")
    print(f"\nsingle-ring rows4: T/m={t_per_m:.3f}  T@74mm={t74:.3f} N.m  "
          f"target T/m={TARGET_T_PER_M:.1f}")
    print(f"verdict: {verdict}")
    print(f"measured scaling exponent vs anchor 92.1mm (approx, D^a): "
          f"a = ln({t_per_m:.2f}/8.53)/ln({BORE*1e3:.1f}/92.1) = "
          f"{math.log(t_per_m/8.5265)/math.log(BORE*1e3/92.075):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
