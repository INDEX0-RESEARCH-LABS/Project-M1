"""Gate B: nonlinear (saturated iron) solver must satisfy Ampere's law.

The ring carries 7000 A through its bore; on any closed path inside the iron
the line integral of H must equal the enclosed current exactly, whatever the
material does. This is the check that a converged nonlinear solution is
physically correct rather than merely stable.

The full diagnostic version (with saturation reporting) is
simulation/scripts/known_answer_nonlinear.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulation" / "scripts"))

from fem_magnetics import MU0, load_bh_curve, solve_az
from known_answer_nonlinear import AMPS, R_WIRE, _Ht_integral, ring_mesh


def test_saturated_iron_satisfies_ampere():
    msh = ring_mesh(ROOT / "simulation" / "validation" / "known_answer" / "ring.msh",
                    2e-3)
    H, B = load_bh_curve("M-19 Steel")
    sol = solve_az(msh, {"coil": 1.0, "iron": (H, B)},
                   {"coil": AMPS / (np.pi * R_WIRE ** 2)})
    assert sol["converged"], "nonlinear iteration did not converge"

    r = np.hypot(sol["cx"], sol["cy"])
    b = np.hypot(sol["Bx"], sol["By"])
    assert b[(r >= 0.02) & (r < 0.08)].mean() > 1.5, "iron failed to saturate"

    i_enc = _Ht_integral(sol, 0.04, (H, B))
    assert abs(i_enc - AMPS) / AMPS < 0.02, f"{i_enc=} vs {AMPS=}"
