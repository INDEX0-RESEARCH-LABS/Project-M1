"""Gate B: solver must reproduce an analytic magnetostatic field within 2 %.

Runs a single coarse-mesh wire solve (fast) and checks |B| at r = 50 mm against
B = mu0*I/(2*pi*r). The full three-mesh convergence study lives in
simulation/scripts/known_answer_check.py, which is the authoritative record.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulation" / "scripts"))

from fem_magnetics import MU0, b_magnitude_at, solve_az, wire_problem

I = 1000.0
R_MEAS = 0.05


def test_straight_wire_matches_analytic():
    msh = wire_problem(ROOT / "simulation" / "validation" / "known_answer", lcar=5e-3)
    sol = solve_az(msh, {"air": 1.0, "conductor": 1.0},
                   {"conductor": I / (np.pi * 0.005 ** 2)})
    b = b_magnitude_at(sol, R_MEAS, 0.0)
    analytic = MU0 * I / (2 * np.pi * R_MEAS)
    assert abs(b - analytic) / analytic < 0.02, f"{b=} vs {analytic=}"
