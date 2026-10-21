"""Gate C declared search over the D-010 v1 baseline neighborhood.

Per PLAN: simulation/validation/gate_c_search/PLAN.md. Objective: maximize |T|/m at
declared excitation (equal Cu, J=6/мм^2, fill 0.4, M-43, 1536-ray mesh). Search space,
gates C1-C5 and honesty notes are frozen in the PLAN; this script implements them.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from rajini_anchor import (AIRGAP, BORE, FILL, J_CU, L_STACK, N_SLOTS, SHAFT_OD,
                           STATOR_OD, d_pattern, split_slots, tri_areas)
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas

OUT = Path(__file__).parent / "validation" / "gate_c_search"

SPANS = (0.012, 0.016, 0.020)      # mm, sweep-trend edge extension
FRACS = (0.62, 0.70)               # 0.62 won the family sweep; probe wider
BRIDGES = (0.0006, 0.0004)         # thinner surface bridge = less q-shunt
N_BARRIERS = 2                     # frozen: beat 3 in every member family
DELTAS = (10.0, 17.5, 25.0, 32.5, 40.0)

MESH = dict(n_theta=1536, n_gap_rows=4)
MESH_FINE = dict(n_theta=3072, n_gap_rows=4)
BASELINE_T_PMM = 9.0950            # D-010 v1 at 1536, delta 26.25 (frozen)
GATE_IMPROVE = 1.10                # winner >= baseline x 1.10

SMOKE = "SMOKE" in __import__("os").environ
if SMOKE:
    SPANS, FRACS, BRIDGES, DELTAS = (0.012,), (0.62,), (0.0006,), (25.0,)
    MESH = dict(n_theta=768, n_gap_rows=2)
    MESH_FINE = None


def make_g(span: float, frac: float, bridge: float, deg: float) -> SynRMGeometry:
    return SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                         airgap=AIRGAP, shaft_od=SHAFT_OD,
                         barrier_radial_span=span, n_barriers=N_BARRIERS,
                         barrier_angle_frac=frac, bridge=bridge,
                         barrier_center_angle=math.pi / 4 + math.radians(deg))


def prep_c(g: SynRMGeometry, mesh_kw: dict, H, B) -> dict:
    mesh, sub, _ = build_mesh(g, **mesh_kw)
    sg = split_slots(mesh, sub)
    areas = tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    exp = expected_areas(g)
    err = max(abs(areas[sub[n]].sum() / e - 1.0) for n, e in exp.items()
              if n in sub and len(sub[n]) > 0 and e > 0)
    return {"mesh": mesh, "sub": sub, "sg": sg, "slot_area": slot_area, "err": err}


def solve_c(g, p, H, B) -> dict:
    pattern = d_pattern()
    loading = {k: J_CU * FILL * p["slot_area"][f"slot_{k:02d}"] for k in range(N_SLOTS)}
    jz = {f"slot_{k:02d}": pattern[k] * loading[k] / p["slot_area"][f"slot_{k:02d}"]
          for k in range(N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in p["sub"].items() if n != "slots"}, **p["sg"]}
    sol = solve_az_core(p["mesh"], cell_sets, materials, jz)
    r_gap = (BORE / 2 + g.rotor_od / 2) / 2
    T = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    bmax = float(np.hypot(sol["Bx"], sol["By"]).max())
    return {"converged": bool(sol["converged"]), "iters": int(sol["newton_iters"]),
            "T_per_m": T, "Bmax_T": bmax, "r_gap": r_gap}


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    results = {}
    print(f"baseline to beat (1536): {BASELINE_T_PMM:.4f} N.m/m "
          f"-> gate {BASELINE_T_PMM * GATE_IMPROVE:.4f}\n", flush=True)
    for span in SPANS:
        for frac in FRACS:
            for bridge in BRIDGES:
                key = f"span{span*1e3:.0f}_frac{frac:.2f}_bridge{bridge*1e3:.1f}"
                rows = {}
                for deg in DELTAS:
                    g = make_g(span, frac, bridge, deg)
                    p = prep_c(g, MESH, H, B)
                    rows[deg] = {**solve_c(g, p, H, B), "area_err": p["err"]}
                    print(f"  {key} delta={deg:5.2f} T/m={c['T_per_m']:+.4f} "
                          f"Bmax={c['Bmax_T']:.2f} it={c['iters']} "
                          f"conv={c['converged']} err={p['err']:.3%}", flush=True)
                best = max(rows, key=lambda d: abs(rows[d]["T_per_m"]))
                for deg in (best - 3.75, best + 3.75):
                    if deg in rows or deg < 0:
                        continue
                    g = make_g(span, frac, bridge, deg)
                    p = prep_c(g, MESH, H, B)
                    rows[deg] = {**solve_c(g, p, H, B), "area_err": p["err"]}
                    print(f"  {key} refine delta={deg:5.2f} "
                          f"T/m={rows[deg]['T_per_m']:+.4f}", flush=True)
                cbest = max(rows, key=lambda d: abs(rows[d]["T_per_m"]))
                results[key] = {"rows": rows, "T_best": abs(rows[cbest]["T_per_m"]),
                                "best_delta": cbest, "area_err_max": None}
                print(f"  -> {key} best {results[key]['T_best']:.4f} @ {cbest:.2f}deg\n",
                      flush=True)

    ranked = sorted(results, key=lambda k: -results[k]["T_best"])
    winner = ranked[0]
    span_s, frac_s, br_s = winner.split("_")
    span = float(span_s[4:]) * 1e-3
    frac = float(frac_s[4:])
    bridge = float(br_s[6:]) * 1e-3
    deg = results[winner]["best_delta"]

    # C5 independent path: fresh geometry/mesh at 3072, ONE solve, both extractors
    g = make_g(span, frac, bridge, deg)
    if MESH_FINE is None:                       # smoke: verify skipped
        results[winner]["verify"] = {"T_fine_single": None, "T_fine_multi": None,
                                     "c3": None, "c4": None}
        gates = {"C1_converged": all(cc["converged"] for r in results.values()
                                     for cc in r["rows"].values()),
                 "C2_areas<=1%": True, "C3_refine<=10%": None,
                 "C4_multi_ring<=15%": None, "C5_improve>=10%": None}
        print("\n[SMOKE] plumbing ok (verify skipped)", flush=True)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "gate_c_search.json").write_text(json.dumps(
            {"gates": gates, "baseline_T_pmm": BASELINE_T_PMM,
             "winner_detail": results[winner]["verify"],
             "results": results}, indent=1, default=lambda o: o.item()
            if isinstance(o, np.generic) else None))
        print(f"wrote {OUT / 'gate_c_search.json'}", flush=True)
        return 0
    p = prep_c(g, MESH_FINE, H, B)
    pattern = d_pattern()
    loading = {k: J_CU * FILL * p["slot_area"][f"slot_{k:02d}"] for k in range(N_SLOTS)}
    jz = {f"slot_{k:02d}": pattern[k] * loading[k] / p["slot_area"][f"slot_{k:02d}"]
          for k in range(N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in p["sub"].items() if n != "slots"}, **p["sg"]}
    sol = solve_az_core(p["mesh"], cell_sets, materials, jz)
    err_max = p["err"]
    r_gap = (BORE / 2 + g.rotor_od / 2) / 2
    half_gap = BORE / 2 - g.rotor_od / 2
    T_single = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    T_multi = torque_maxwell(sol, r_gap, 1.0, n_theta=2880,
                             n_rings=9, r_spread=0.5 * half_gap)
    c3 = abs(T_single - results[winner]["T_best"]) / abs(T_single) <= 0.10
    c4 = abs(T_multi - T_single) / abs(T_multi) <= 0.15
    bmax = float(np.hypot(sol["Bx"], sol["By"]).max())
    results[winner]["verify"] = {"T_fine_single": T_single, "T_fine_multi": T_multi,
                                 "c3": bool(c3), "c4": bool(c4), "Bmax_T": bmax}
    print(f"\nWINNER {winner} delta={deg:.2f}  T(3072 single)={T_single:+.4f}  "
          f"T(3072 multi9)={T_multi:+.4f} -> C3={c3} C4={c4}", flush=True)

    improve = abs(T_multi) / BASELINE_T_PMM
    gates = {
        "C1_converged": all(cc["converged"] for r in results.values()
                            for cc in r["rows"].values()),
        "C2_areas<=1%": max(cc["area_err"] for r in results.values()
                            for cc in r["rows"].values()) <= 0.01 and err_max <= 0.01,
        "C3_refine<=10%": bool(c3),
        "C4_multi_ring<=15%": bool(c4),
        "C5_improve>=10%": improve >= GATE_IMPROVE,
    }
    print("\nGATES:", gates, flush=True)
    print(f"WINNER vs v1 baseline: {abs(T_multi):.4f} vs {BASELINE_T_PMM:.4f} "
          f"-> x{improve:.3f}  ({abs(T_multi)*L_STACK:.3f} N.m @74mm)", flush=True)
    print("OVERALL:", "PASS" if all(gates.values()) else "FAIL", flush=True)

    def _py(o):
        if isinstance(o, np.generic):
            return o.item()
        raise TypeError(repr(o))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gate_c_search.json").write_text(json.dumps(
        {"gates": gates, "baseline_T_pmm": BASELINE_T_PMM,
         "winner_detail": results[winner]["verify"],
         "ratio_vs_baseline": improve,
         "results": results}, indent=1, default=_py))
    print(f"wrote {OUT / 'gate_c_search.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
