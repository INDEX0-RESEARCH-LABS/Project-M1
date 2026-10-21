"""Extractor A/B arbiter — same solution, single-ring vs 9-ring Maxwell torque.

Written after gate_c_search C4/C5 failed: the winner's multi-ring torque (+25–30% over
single-ring) exceeded the declared 15% consistency gate, and comparing a multi-ring
winner against a single-ring baseline mixes estimators. This script solves the BASELINE
(D-010 v1) and the search WINNER once each at 3072 rays and extracts both ways, so the
improvement verdict is computed under ONE extractor at a time.

Run:  .venv/bin/python simulation/scripts/gate_c_extractor_ab.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from rajini_anchor import (AIRGAP, BORE, FILL, J_CU, N_SLOTS, SHAFT_OD, STATOR_OD,
                           d_pattern, split_slots, tri_areas)
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh


def run(span: float, frac: float, bridge: float, deg: float, label: str) -> dict:
    H, B = load_bh_curve("M-43 Steel")
    g = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                      airgap=AIRGAP, shaft_od=SHAFT_OD, barrier_radial_span=span,
                      n_barriers=2, barrier_angle_frac=frac, bridge=bridge,
                      barrier_center_angle=math.pi / 4 + math.radians(deg))
    mesh, sub, _ = build_mesh(g, n_theta=3072, n_gap_rows=4)
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
    r_gap = (BORE / 2 + g.rotor_od / 2) / 2
    hg = BORE / 2 - g.rotor_od / 2
    t1 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    t9 = torque_maxwell(sol, r_gap, 1.0, n_theta=2880, n_rings=9, r_spread=0.5 * hg)
    print(f"{label:8s} delta={deg:5.1f}: single={t1:+.4f}  multi9={t9:+.4f}  "
          f"estimator shift={(t9 - t1) / abs(t9):+.1%}", flush=True)
    return {"single": t1, "multi": t9}


def main() -> None:
    base = run(0.012, 0.62, 0.0006, 26.25, "baseline")
    win = run(0.020, 0.70, 0.0004, 32.50, "winner")
    print(f"\nimprovement, SAME extractor both sides:")
    print(f"  single-consistent: {(win['single'] - base['single']) / abs(base['single']):+.1%}")
    print(f"  multi-consistent:  {(win['multi'] - base['multi']) / abs(base['multi']):+.1%}")
    print("  verdict: declared +10% gate must be judged on consistent extraction only.")


if __name__ == "__main__":
    main()
