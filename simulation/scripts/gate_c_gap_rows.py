"""Extractor-convergence study per validation/extractor_convergence/PLAN.md.

D-011 open question: single-ring vs 9-ring Maxwell torque disagree +25-30% on the SAME
solution in the saturated SynRM gap. This study solves the D-010 baseline config at
3072 rays with n_gap_rows in {4, 10, 20} and extracts BOTH ways per solution, to test
whether the spread is an airgap-discretization artifact and whether it converges.

Run:  .venv/bin/python simulation/scripts/gate_c_gap_rows.py
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from rajini_anchor import (AIRGAP, BORE, FILL, J_CU, N_SLOTS, SHAFT_OD, STATOR_OD,
                           d_pattern, split_slots, tri_areas)
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas

ROWS = (4, 10, 20)


def solve_at(rows: int, span: float, frac: float, bridge: float, deg: float,
             label: str) -> dict:
    H, B = load_bh_curve("M-43 Steel")
    t0 = time.time()
    g = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                      airgap=AIRGAP, shaft_od=SHAFT_OD, barrier_radial_span=span,
                      n_barriers=2, barrier_angle_frac=frac, bridge=bridge,
                      barrier_center_angle=math.pi / 4 + math.radians(deg))
    mesh, sub, _ = build_mesh(g, n_theta=3072, n_gap_rows=rows)
    sg = split_slots(mesh, sub)
    areas = tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    exp = expected_areas(g)
    err = max(abs(areas[sub[n]].sum() / e - 1.0) for n, e in exp.items()
              if n in sub and len(sub[n]) > 0 and e > 0)
    pat = d_pattern()
    jz = {f"slot_{k:02d}": pat[k] * J_CU * FILL for k in range(N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cs = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    sol = solve_az_core(mesh, cs, materials, jz)
    r_gap = (BORE / 2 + g.rotor_od / 2) / 2
    hg = BORE / 2 - g.rotor_od / 2
    t1 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    t9 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880, n_rings=9,
                        r_spread=0.5 * hg)
    out = {"rows": rows, "single": t1, "multi": t9,
           "conv": bool(sol["converged"]), "err": float(err),
           "n_elems": mesh.t.shape[1], "secs": time.time() - t0}
    print(f"{label} rows={rows:2d}: single={t1:+.4f} multi9={t9:+.4f} "
          f"spread={(t9-t1)/abs(t9):+.1%} conv={out['conv']} "
          f"err={out['err']:.3%} elems={out['n_elems']} t={out['secs']:.0f}s",
          flush=True)
    return out


def main() -> int:
    extra = [int(a) for a in sys.argv[1:]]   # amendment-1 extra baseline levels
    if extra:
        for rows in extra:
            solve_at(rows, 0.012, 0.62, 0.0006, 26.25, "baseline")
        return 0
    results = {"baseline": [], "winner": None}
    for rows in ROWS:
        run = solve_at(rows, 0.012, 0.62, 0.0006, 26.25, "baseline")
        results["baseline"].append(run)
        if not run["conv"] or abs(run["err"]) > 0.01:
            print(f"E1/E2 FAIL at rows={rows} — stopping per PLAN", flush=True)
            break
    else:
        # winner config only if the baseline sweep completed cleanly
        hi = results["baseline"][-1]["rows"]
        results["winner"] = solve_at(hi, 0.020, 0.70, 0.0004, 32.50, "winner")

    base = results["baseline"]
    if len(base) >= 2:
        lo, hi = base[0], base[-1]
        spread_hi = (hi["multi"] - hi["single"]) / abs(hi["multi"])
        print(f"\nper-extractor drift, rows {lo['rows']}->{hi['rows']}:")
        print(f"  single: {lo['single']:+.4f} -> {hi['single']:+.4f} "
              f"({(hi['single']-lo['single'])/abs(lo['single']):+.1%})")
        print(f"  multi9: {lo['multi']:+.4f} -> {hi['multi']:+.4f} "
              f"({(hi['multi']-lo['multi'])/abs(lo['multi']):+.1%})")
        verdict = ("PASS: spread %.1f%% <= 15%% at rows=%d -> converged absolute "
                   "torque = %.4f +-%.4f N.m/m (mean +- spread/2), winner-level "
                   "config ran at same rows"
                   if abs(spread_hi) <= 0.15 else
                   "FAIL per E3: spread %.1f%% > 15%% at rows=%d — trend only")
        print("E3: " + (verdict % (abs(spread_hi) * 100, hi["rows"],
                                    0.5 * (hi['single'] + hi['multi']),
                                    abs(spread_hi) * 0.5 * abs(hi['multi']))
                         if abs(spread_hi) <= 0.15 else
                         (verdict % (abs(spread_hi) * 100, hi['rows']))))
        if results["winner"] is not None:
            w = results["winner"]
            ws = (w["multi"] - w["single"]) / abs(w["multi"])
            print(f"winner@rows={w['rows']}: spread={ws:+.1%} "
                  f"single={w['single']:+.4f} multi9={w['multi']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
