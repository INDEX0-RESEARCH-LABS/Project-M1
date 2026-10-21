"""Certification of the 150 mm-bore frame: angle peak + mesh rows (see PLAN.md).

The first pass hit E1 (>=21.6 N.m/m) but with Bmax ~3 T (BH extrapolation) and a 22%
1536->3072 drift, plus a large jump between delta 22.5 and 26.25. This script:
  1. refines delta at 1536/rows4 to show whether the peak is a real peak or an artifact;
  2. re-solves the best angle at 3072 with rows 10/20/40 (the anchor certification
     protocol) to see whether the number is mesh-convergent.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fem_magnetics import load_bh_curve  # noqa: E402
from envelope_validation import run  # noqa: E402

ANGLES = (23.5, 24.5, 25.5, 26.25, 27.0, 28.0, 30.0)
ROWS = (4, 10, 20, 40)


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    print("=== angle refinement (1536/rows4) ===")
    sweep = {}
    for d in ANGLES:
        r = run(d, 1536, 4, H, B)
        sweep[d] = r
        print(f"  delta={d:5.2f}  T/m={r['T_per_m']:7.3f}  "
              f"Bmax={r['Bmax']:.2f}T  conv={r['conv']}")
        assert r["conv"]
    best = max(sweep, key=lambda d: sweep[d]["T_per_m"])
    print(f"peak at delta={best} deg, T/m={sweep[best]['T_per_m']:.3f}")

    print("\n=== mesh rows certification at best delta (3072 rays) ===")
    cert = {}
    for rows in ROWS:
        r = run(best, 3072, rows, H, B)
        cert[rows] = r["T_per_m"]
        print(f"  rows={rows:2d}  T/m={r['T_per_m']:7.3f}  Bmax={r['Bmax']:.2f}T  "
              f"conv={r['conv']}")
        assert r["conv"]
    seq = [cert[r] for r in ROWS]
    drift = (seq[-1] - seq[0]) / seq[0]
    last = (seq[-1] - seq[-2]) / seq[-2]
    print(f"  rows4->rows40 drift = {drift:+.1%} ; last step = {last:+.1%}")
    print(f"  certified-class value (rows40) = {cert[40]:.3f} N.m/m "
          f"-> {cert[40]*0.074:.3f} N.m @ 74 mm")
    print(f"  target 21.6 N.m/m -> {'MET' if cert[40] >= 21.6 else 'NOT MET'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
