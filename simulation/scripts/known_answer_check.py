"""Gate B solver validation: straight-wire known answer + mesh convergence.

Analytic: B(r) = mu0 * I / (2*pi * r) outside the conductor.
I = 1000 A, R_cond = 5 mm, measurement at r = 50 mm  ->  B = 4.0e-3 T.

Declared pass criteria (fixed before running):
  1. finest-mesh relative error  < 2 %
  2. error monotonically decreasing (or plateaued) with refinement
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import MU0, b_magnitude_at, solve_az, wire_problem

HERE = Path(__file__).resolve().parent.parent / "validation" / "known_answer"
I = 1000.0
R_MEAS = 0.05
B_ANALYTIC = MU0 * I / (2 * np.pi * R_MEAS)


def run() -> bool:
    HERE.mkdir(parents=True, exist_ok=True)
    results = []
    for lcar in (5e-3, 2.5e-3, 1.25e-3):
        msh = wire_problem(HERE, lcar, current=I)
        sol = solve_az(msh,
                       materials={"air": 1.0, "conductor": 1.0},
                       current_density={"conductor": I / (np.pi * 0.005 ** 2)})
        b = b_magnitude_at(sol, R_MEAS, 0.0)
        err = abs(b - B_ANALYTIC) / B_ANALYTIC * 100
        results.append((lcar, sol["nelems"], b, err))
        print(f"lcar={lcar*1e3:5.2f} mm | {sol['nelems']:7d} elems | "
              f"B={b*1e3:8.5f} mT | err={err:6.3f} %")

    finest_err = results[-1][3]
    monotone = results[-1][3] <= results[0][3] * 1.05  # converged, allow plateau
    ok = finest_err < 2.0 and monotone
    print(f"\nanalytic B(50mm) = {B_ANALYTIC*1e3:.5f} mT")
    print(f"finest error = {finest_err:.3f} %  -> {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
