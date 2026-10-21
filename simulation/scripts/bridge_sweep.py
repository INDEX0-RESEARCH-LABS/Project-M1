"""Bridge-thickness sweep at the point-design frame (bore 130 mm).

Declared expectation (before running): the 0.6 mm continuous surface bridge is the
q-flux short circuit; thinner bridges should raise the differential inductance and
therefore torque per ampere at fixed slot AT. Gate:
  * B1: thinner bridge -> higher T/m at the same AT (monotone down to 0.3 mm),
  * B2: report Bmax at every bridge (thin bridges may saturate harder locally),
  * B3: mechanical note only -- the rotor stress check covers 0.6 mm; thinner bridges
        need a re-run before any hardware decision.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fem_magnetics import load_bh_curve  # noqa: E402
from envelope_validation import run  # noqa: E402

BORE = 0.130
DELTA = 26.25
BRIDGES = (0.0003, 0.0004, 0.0006, 0.0010)


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    print("bridge   T/m(1536)   Bmax    vs 0.6mm")
    base = None
    out = {}
    for br in BRIDGES:
        r = run(DELTA, 1536, 4, H, B, bore=BORE, bridge=br)
        out[br] = r["T_per_m"]
        if br == 0.0006:
            base = r["T_per_m"]
        print(f"{br*1e3:4.1f}mm  {r['T_per_m']:9.2f}   {r['Bmax']:.2f}T   "
              f"{'--' if br == 0.0006 else ''}")
        assert r["conv"], f"no convergence at bridge {br}"
    print()
    for br in BRIDGES:
        print(f"  bridge {br*1e3:.1f} mm: {out[br]/base:.2f}x the 0.6 mm torque")
    # B1 gate: 0.3 mm must beat 0.6 mm
    ok = out[0.0003] > base
    print(f"B1 (thin bridge raises torque): {'PASS' if ok else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
