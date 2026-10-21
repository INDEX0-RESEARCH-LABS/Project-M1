"""Envelope point design: smallest self-similar frame for the 1.6 N.m target.

See validation/envelope_point_design/PLAN.md (declared before running).
Screens bores at rows4, then certifies the chosen bore at rows 4/20/40.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fem_magnetics import load_bh_curve  # noqa: E402
from envelope_validation import build, run  # noqa: E402

BORES = (0.100, 0.110, 0.120, 0.130, 0.140)
DELTA = 26.25
T_CONT = 1.6
T_REQ = 1.25 * T_CONT          # 25% margin
# winding model (same as envelope_sizing.py)
V_DC, KW, B_G, FILL, Q = 48.0, 0.95, 0.90, 0.40, 3
E_ALLOW = V_DC / math.sqrt(3) * 0.95


def turns(bore: float, L: float, paths: int = 1) -> float:
    p = 2
    psi1 = KW * (2 / math.pi) * B_G * (math.pi * bore / (2 * p)) * L
    n_ph = E_ALLOW / (2 * math.pi * (3000 / 60 * p) * psi1)
    return paths * n_ph / (2 * p * Q)


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    print("bore   T/m(1536)  Bmax   L@1.6  L@2.0  N_c(a=1,2,4,6) @L@2.0")
    screen = {}
    for bore in BORES:
        r = run(DELTA, 1536, 4, H, B, bore=bore)
        screen[bore] = r["T_per_m"]
        L16, L20 = T_CONT / r["T_per_m"], T_REQ / r["T_per_m"]
        nc = [turns(bore, L20, a) for a in (1, 2, 4, 6)]
        print(f"{bore*1e3:4.0f}mm {r['T_per_m']:9.2f}  {r['Bmax']:4.2f}T "
              f"{L16*1e3:6.1f} {L20*1e3:6.1f}   "
              + " ".join(f"{x:5.2f}" for x in nc))

    # pick the smallest bore whose 2.0 N.m stack is <= 74 mm and windable at a<=6
    pick = None
    for bore in BORES:
        L20 = T_REQ / screen[bore]
        if L20 <= 0.074 and any(4 <= turns(bore, L20, a) <= 20 for a in (1, 2, 4, 6)):
            pick = (bore, L20)
            break
    if pick is None:
        print("\nno bore in the screen meets P1")
        return 1
    bore, L20 = pick
    print(f"\npick: bore {bore*1e3:.0f} mm, stack {L20*1e3:.1f} mm for {T_REQ:.1f} N.m "
          f"(1.6 N.m with 25% margin)")

    angles = (24.0, 26.25, 28.5)
    print("\nangle check (1536/rows4):")
    best = DELTA
    for d in angles:
        r = run(d, 1536, 4, H, B, bore=bore)
        print(f"  delta={d:5.2f}  T/m={r['T_per_m']:7.2f}  Bmax={r['Bmax']:.2f}T")
        if r["T_per_m"] > screen[bore]:
            best = d
    print(f"  peak angle kept: {best}")

    print("\nrows certification (3072 rays):")
    cert = {}
    for rows in (4, 20, 40):
        r = run(best, 3072, rows, H, B, bore=bore)
        cert[rows] = r["T_per_m"]
        print(f"  rows={rows:2d}  T/m={r['T_per_m']:7.2f}  Bmax={r['Bmax']:.2f}T  "
              f"conv={r['conv']}")
        assert r["conv"]
    t_m = cert[40]
    t_cont_frame = t_m * L20
    drift = (cert[40] - cert[4]) / cert[4]
    print(f"\nrows40: T/m={t_m:.2f} -> {t_cont_frame:.2f} N.m at L={L20*1e3:.1f} mm "
          f"({t_cont_frame/T_CONT:.2f}x the 1.6 N.m target)")
    print(f"rows4->rows40 drift = {drift:+.1%}  (P2: <=15% -> "
          f"{'PASS' if abs(drift) <= 0.15 else 'FAIL'})")
    print("windability at L=%.0f mm: " % (L20 * 1e3)
          + ", ".join(f"a={a}:{turns(bore, L20, a):.2f}" for a in (1, 2, 4, 6)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
