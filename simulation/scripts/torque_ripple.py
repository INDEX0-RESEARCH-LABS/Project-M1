"""Load torque ripple of the D-014 deep-barrier rotor.

**STATUS: the synchronized model below is NOT validated -- do not quote its output.**
It reproduces the certified point and the exact 90 deg periodicity, but it swings
0.64-1.70 N.m over a 45 deg window while the static curve of the same geometry stays
within ~10% of a smooth sinusoid. See `validation/torque_ripple/RESULT.md` s.4.

A SynRM has **no permanent magnets**, so there is no cogging torque: at zero
current the torque is zero at every angle.  All ripple is load ripple.

Modelling choice (this is the whole point of the script).  A ripple sweep must
hold the *current angle* fixed while the rotor turns, because that is the
steady state: the current vector turns with the rotor.  Sweeping the rotor with
a current pattern fixed in the stator frame instead gives the *static
torque-angle curve* T(delta), whose slope over one slot pitch is the
fundamental, not ripple.  So each point here advances the phase currents by
alpha = P_POLES * (delta - delta_op) while the rotor turns by delta, which pins
the relative angle at delta_op.  At delta = delta_op, alpha = 0 and the
pattern is the certified snapshot (i_a = 1, i_b = i_c = -1/2), so the point
must reproduce the certified torque -- that is gate R1.

Window: 45 deg mechanical = half the machine period (90 deg), 0.5 deg steps.
That resolves mechanical order 36 (slot order, period 10 deg) with 20 samples
per period and gives 1.5 cycles of order 12 (the 5th/7th mmf harmonic pair,
period 30 deg).  Frequency resolution is order 10, so an order-12 component is
at the edge of what this window can size.

Run (four quarters per design, then analyse):
    python torque_ripple.py --start 3.75  --stop 15.25 --out /tmp/ripple_a.csv
    ...
    python torque_ripple.py --analyse /tmp/ripple_a.csv ...
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dq_model as D          # noqa: E402
import rajini_anchor as A     # noqa: E402
from envelope_validation import build  # noqa: E402
from fem_magnetics import load_bh_curve, torque_annulus  # noqa: E402
from torque_mesh_convergence import solve_raw, torque_at  # noqa: E402

CAND = dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
            barrier_span=0.0445)
DELTA_OP = D.DELTA_OP
J_DEEP = 5.21
J_BASE = 5.62
PHASE_ANGLE = {"A": 0.0, "B": -2.0 * math.pi / 3.0, "C": 2.0 * math.pi / 3.0}
RINGS = (1, 5, 9)
RING_COL = {1: 1, 5: 2, 9: 3}      # ring count -> CSV column


def moving_pattern(alpha: float) -> dict[int, float]:
    """Balanced 3-phase snapshot with the phase currents advanced by `alpha`."""
    out = {}
    for k in range(A.N_SLOTS):
        ph, s = A.slot_phase36(k)
        out[k] = s * math.cos(alpha + PHASE_ANGLE[ph])
    return out


def sweep(start: float, stop: float, step: float, j_mm2: float, out: str,
          base: bool = False, alpha0: float = DELTA_OP) -> int:
    H, B = load_bh_curve("M-43 Steel")
    kw = {} if base else CAND
    j = j_mm2 * 1e6
    n = int(round((stop - start) / step)) + 1
    done = set()
    if os.path.exists(out):
        with open(out) as f:
            done = {float(r["delta_deg"]) for r in csv.DictReader(f)}
        mode = "a"
    else:
        mode = "w"
    print(f"ripple sweep {start:.2f}..{stop:.2f} step {step} ({n} pts, "
          f"{n - len(done)} to run), J={j_mm2:.2f}, angle {alpha0:.2f}, "
          f"{'BASE' if base else 'S6'}", flush=True)
    with open(out, mode, newline="") as f:
        w = csv.writer(f)
        if mode == "w":
            w.writerow(["delta_deg", "T1", "T5", "T9", "ann_mean", "ann_spread"])
        for i in range(n):
            d = start + i * step
            if d in done:
                continue
            alpha = D.P_POLES * math.radians(d - alpha0)
            g = build(d, D.BORE, **kw)
            res = solve_raw(d, j, H, B, 1536, 4, geom=g,
                            pattern=moving_pattern(alpha))
            t = [torque_at(res, r) for r in RINGS]
            bands = torque_annulus(res["sol"], g.rotor_od / 2 + 1e-6,
                                   g.stator_bore / 2 - 1e-6, 1.0, n_bands=4) * D.L_STACK
            spread = (bands.max() - bands.min()) / abs(bands.mean())
            w.writerow([f"{d:.2f}"] + [f"{x:.6f}" for x in t]
                       + [f"{bands.mean():.6f}", f"{spread:.6f}"])
            f.flush()
            print(f"  {d:6.2f}  T1={t[0]:7.4f}  T5={t[1]:7.4f}  T9={t[2]:7.4f}  "
                  f"ann={bands.mean():7.4f}  band={spread:.1%}", flush=True)
            if not (0.05 < t[1] < 3.0):
                print(f"  HALT: torque {t[1]:.3f} outside the plausible band; "
                      f"current angle or pattern sign is wrong", flush=True)
                return 2
    print(f"wrote {out}", flush=True)
    return 0


def _load(paths):
    rows = []
    for p in paths:
        with open(p) as f:
            for r in csv.DictReader(f):
                rows.append([float(r["delta_deg"]), float(r["T1"]),
                             float(r["T5"]), float(r["T9"]),
                             float(r.get("ann_mean", "nan")),
                             float(r.get("ann_spread", "nan"))])
    rows.sort()
    a = np.array(rows)
    keep = np.concatenate(([True], np.diff(a[:, 0]) > 1e-9))
    return a[keep]


def _pp(t):
    return (t.max() - t.min()) / t.mean()


def analyse(paths, rings: int = 5) -> int:
    a = _load(paths)
    d = a[:, 0]
    if len(d) < 20:
        raise SystemExit(f"only {len(d)} points")
    step = float(np.median(np.diff(d)))
    has_ann = np.isfinite(a[:, 4]).any()
    print(f"n={len(d)}  {d.min():.2f}..{d.max():.2f} deg  step {step:.2f}")
    for name, col in RING_COL.items():
        print(f"  rings {name}: mean {a[:, col].mean():.4f}  min {a[:, col].min():.4f}"
              f"  max {a[:, col].max():.4f}  p-p {_pp(a[:, col]):.2%}")
    if has_ann:
        m = np.isfinite(a[:, 4])
        print(f"  annulus: mean {a[m, 4].mean():.4f}  min {a[m, 4].min():.4f}"
              f"  max {a[m, 4].max():.4f}  p-p {_pp(a[m, 4]):.2%}")
        print(f"  annulus band spread: median {np.median(a[m, 5]):.1%}  "
              f"max {a[m, 5].max():.1%}")
    t = a[:, 4] if has_ann else a[:, RING_COL[rings]]

    mean, lo, hi = t.mean(), t.min(), t.max()
    print(f"\nT = {mean:.4f} N.m  p-p = {hi - lo:.4f} N.m = {_pp(t):.2%}")
    print(f"  min at {d[t.argmin()]:.2f} deg, max at {d[t.argmax()]:.2f} deg")

    # R2: two equal windows must agree. 11.25 deg is the observed dip spacing
    # (32 barrier tips); 10.0 deg is the 36-slot pitch.
    for win in (10.0, 11.25):
        wins = []
        for a0, a1 in ((d.min(), d.min() + win), (d.max() - win, d.max())):
            m = (d >= a0 - 1e-9) & (d <= a1 + 1e-9)
            if m.sum() >= 10:
                wins.append(_pp(t[m]))
        if len(wins) == 2:
            print(f"  R2 window {win:5.2f} deg: {wins[0]:.2%} vs {wins[1]:.2%}, "
                  f"agreement {abs(wins[1]-wins[0])*100:.1f} pp")

    x = t - t.mean()
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    order = np.fft.rfftfreq(len(x), d=step) * 360.0
    top = np.argsort(spec)[::-1][:5]
    print("\ndominant mechanical orders (1 = once per revolution):")
    for i in top:
        if order[i] > 0:
            print(f"  order {order[i]:6.1f} (electrical {order[i] * D.P_POLES:5.1f})"
                  f"  amplitude {2 * spec[i] / len(x):.4f} N.m")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=float, default=3.75)
    ap.add_argument("--stop", type=float, default=15.25)
    ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--j", type=float, default=J_DEEP)
    ap.add_argument("--out", default="/tmp/opencode/m1/ripple.csv")
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--alpha0", type=float, default=DELTA_OP)
    ap.add_argument("--rings", type=int, default=5)
    ap.add_argument("--analyse", nargs="+")
    a = ap.parse_args()
    if a.analyse:
        return analyse(a.analyse, rings=a.rings)
    j = J_BASE if a.base else a.j
    return sweep(a.start, a.stop, a.step, j, a.out, base=a.base,
                 alpha0=a.alpha0)


if __name__ == "__main__":
    raise SystemExit(main())
