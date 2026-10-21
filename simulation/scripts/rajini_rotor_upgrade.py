"""Anchor rotor-geometry upgrade sweep -- torque ceiling of OUR declared topology.

Per PLAN: simulation/validation/anchor_rotor_upgrade/PLAN.md (declared before running).
Question: the declared barrier layout (arc frac 0.62, span 8.4 mm, 3 barriers/pole)
delivers 8.12 N.m/m -- 13x below the anchor's implied 108 N.m/m. Is the deficit OUR
layout? Sweep barrier_angle_frac x span x n_barriers at fixed envelope/excitation,
report T/m + iron fraction + Bmax + the excitation multiplier to reach the target.

Gates (frozen in PLAN): U1 all converge; U2 areas <= 1%; U3 refinement <= 10% for
the best configs; U4 monotonicity observation (|T| rises toward iron-rich layouts).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve
from rajini_anchor import (AIRGAP, ANGLE_MESH, BORE, FILL, J_CU, L_STACK, N_SLOTS,
                           SHAFT_OD, STATOR_OD, T_TARGET, prep, solve_case)
from synrm_geometry import SynRMGeometry
from synrm_mesh import expected_areas

OUT = Path(__file__).parent / "validation" / "anchor_rotor_upgrade"

ANGLE_FRACS = (0.62, 0.50, 0.40, 0.30)   # 0.62 = committed anchor layout
SPANS = (0.0084, 0.006, 0.012)           # 8.4 = committed
N_BARRIERS = (3, 2)
DELTAS = (22.5, 26.25, 30.0)             # committed MTPA neighborhood
TARGET_T_PER_M = T_TARGET / L_STACK      # 108.1 N.m/m

SMOKE = "SMOKE" in __import__("os").environ     # plumbing test: 2 tiny solves
if SMOKE:
    ANGLE_FRACS, SPANS, N_BARRIERS, DELTAS = (0.62, 0.30), (0.0084,), (3,), (26.25,)
    import rajini_anchor as _ra
    _ra.ANGLE_MESH = dict(n_theta=768, n_gap_rows=2)
    _ra.FINE_MESH = None


def iron_frac(g: SynRMGeometry) -> float:
    r_sh, r_ro = SHAFT_OD / 2, g.rotor_od / 2
    disk = math.pi * (r_ro**2 - r_sh**2)
    return 1.0 - expected_areas(g)["barriers"] / disk


def run_config(angle_frac: float, span: float, n_bar: int, H, B) -> dict:
    rows = {}
    for deg in DELTAS:
        gg = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE,
                           n_slots=N_SLOTS, airgap=AIRGAP, shaft_od=SHAFT_OD,
                           barrier_radial_span=span, n_barriers=n_bar,
                           barrier_angle_frac=angle_frac,
                           barrier_center_angle=math.pi / 4 + math.radians(deg))
        p = prep(gg, H, B)
        u2 = max(p["err"].values()) <= 0.01
        c = solve_case(gg, p["mesh"], p["sub"], p["sg"], p["slot_area"], H, B)
        rows[deg] = {**c, "area_err": max(p["err"].values())}
        print(f"  frac={angle_frac:.2f} span={span*1e3:.1f}mm nb={n_bar} "
              f"delta={deg:5.2f}  T/m={c['T_per_m']:+.4f}  Bmax={c['Bmax_T']:.2f}T"
              f"  it={c['iters']} conv={c['converged']} U2={u2}", flush=True)
    return {"rows": rows, "T_best": max(abs(r["T_per_m"]) for r in rows.values()),
            "iron_frac": iron_frac(gg), "U2_max_err": max(r["area_err"] for r in rows.values())}


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")   # primary bracket only (declared in PLAN)
    results = {}
    print(f"target T/m for 8 N.m @74 mm = {TARGET_T_PER_M:.1f} N.m/m\n", flush=True)
    for frac in ANGLE_FRACS:
        for span in SPANS:
            for n_bar in N_BARRIERS:
                key = f"frac{frac:.2f}_span{span*1e3:.1f}_nb{n_bar}"
                results[key] = run_config(frac, span, n_bar, H, B)
                r = results[key]
                print(f"  -> best |T|={r['T_best']:.4f} N.m/m  "
                      f"iron={r['iron_frac']:.1%}\n", flush=True)

    # U3 refinement: 3072 rays at the two best configs' best delta
    ranked = sorted(results, key=lambda k: -results[k]["T_best"])[:2]
    if SMOKE:
        print("[SMOKE] skip refinement", flush=True)
    else:
        for key in ranked:
            frac, span_s, nb_s = key.split("_")
            frac = float(frac[4:])
            span = float(span_s[4:-2]) * 1e-3
            n_bar = int(nb_s[2])
            best_deg = max(results[key]["rows"],
                           key=lambda d: abs(results[key]["rows"][d]["T_per_m"]))
            gg = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                               airgap=AIRGAP, shaft_od=SHAFT_OD,
                               barrier_radial_span=span, n_barriers=n_bar,
                               barrier_angle_frac=frac,
                               barrier_center_angle=math.pi / 4 + math.radians(best_deg))
            import rajini_anchor as ra
            # prep uses module-level ANGLE_MESH; temporarily switch to FINE_MESH
            old = ra.ANGLE_MESH
            ra.ANGLE_MESH = ra.FINE_MESH
            try:
                p = ra.prep(gg, H, B)
            finally:
                ra.ANGLE_MESH = old
            c = solve_case(gg, p["mesh"], p["sub"], p["sg"], p["slot_area"], H, B)
            t_c = results[key]["rows"][best_deg]["T_per_m"]
            u3 = abs(c["T_per_m"] - t_c) / abs(t_c) <= 0.10
            results[key]["refine"] = {"T_per_m": c["T_per_m"], "u3": u3,
                                      "delta": best_deg}
            print(f"REFINE {key} delta={best_deg}: T(1536)={t_c:.4f} "
                  f"T(3072)={c['T_per_m']:.4f} -> U3={u3}", flush=True)

    best_key = ranked[0]
    best = results[best_key].get("refine", {"T_per_m": None, "u3": None})
    gates = {
        "U1_converged": all(c["converged"] for r in results.values()
                            for c in r["rows"].values()),
        "U2_areas<=1%": all(r["U2_max_err"] <= 0.01 for r in results.values()),
        "U3_refine<=10%": {k: results[k].get("refine", {}).get("u3") for k in ranked},
    }
    print("\nGATES:", gates, flush=True)
    if best["T_per_m"] is None:      # smoke mode: nothing to compare to target
        print("[SMOKE] plumbing ok", flush=True)
    else:
        mult = TARGET_T_PER_M / abs(best["T_per_m"])
        print(f"BEST: {best_key} |T|={abs(best['T_per_m']):.4f} N.m/m  "
              f"iron={results[best_key]['iron_frac']:.1%} "
              f"-> excitation multiplier to reach target: x{mult:.1f} "
              f" (J would be {6.0*mult:.1f} A/mm^2)", flush=True)
    flags = [v if isinstance(v, dict) else v for v in gates.values()]
    ok = all(((isinstance(v, dict) and all(v.values())) or v is True) for v in flags)
    print("OVERALL:", "PASS" if ok else "FAIL", flush=True)

    def _py(o):
        if isinstance(o, np.generic):
            return o.item()
        raise TypeError(repr(o))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rotor_sweep.json").write_text(json.dumps(
        {"gates": gates, "target_T_per_m": TARGET_T_PER_M,
         "excitation_multiplier": (None if best["T_per_m"] is None
                                   else TARGET_T_PER_M / abs(best["T_per_m"])),
         "best_key": best_key,
         "results": results}, indent=1, default=_py))
    print(f"wrote {OUT / 'rotor_sweep.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
