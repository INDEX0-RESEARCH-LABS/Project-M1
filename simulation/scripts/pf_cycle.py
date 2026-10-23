"""Power factor and apparent power over one torque-ripple period.

Why this exists.  `dq_model.pf_check` computes PF at a single rotor position:

    PF = (P_cu + T(delta_op) * omega_m) / (1.5 * Vhat(delta_op) * I)

Both the torque and the terminal voltage are that one snapshot.  In a
synchronous-frame drive the current magnitude is constant over a revolution but
the torque is not, so the energy-average real power is set by the MEAN torque
while the apparent power is set by the LARGEST Vhat over the revolution.  That
makes PF 0.578 a peak-angle number and the 1.06 kVA a single-position number,
exactly the error class D-018/D-020/D-021 found in torque and efficiency.

This sweeps the same geometry and current over one 30 deg mechanical period and
records, per angle: annulus torque, lam_alpha, lam_beta, both Vhat routes, S and
PF.  Then it reports:

  * the cycle-average PF (mean real power / mean apparent power),
  * the rail-sizing apparent power (mean current * MAX Vhat),
  * the voltage ceiling implied by the largest Vhat, not by the point value.

Both flux-linkage routes are kept because `pf_check` records a ~33% disagreement
between the phase-linkage route and the torque route; PF stays a bracket.

Run:
    python pf_cycle.py --step 2 --out /tmp/opencode/m1/pf_cycle.csv
    python pf_cycle.py --analyse /tmp/opencode/m1/pf_cycle.csv
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
from fem_magnetics import load_bh_curve  # noqa: E402
from torque_mesh_convergence import solve_raw  # noqa: E402
from torque_ripple import CAND, DELTA_OP, J_DEEP, moving_pattern  # noqa: E402

V_RAIL = 48.0          # V DC link, from the D-012 envelope
V_CEIL = 26.32         # V peak phase available at the rail (48/sqrt(3)) - see dq_model


def point(delta: float, j_mm2: float, H, B, base: bool = False,
          delta_op: float = DELTA_OP) -> dict:
    j = j_mm2 * 1e6
    kw = {} if base else CAND
    alpha = D.P_POLES * math.radians(delta - delta_op)
    g = build(delta, D.BORE, **kw)
    r = solve_raw(delta, j, H, B, 1536, 4, geom=g,
                  pattern=moving_pattern(alpha))
    n_c1 = D.turns(D.BORE, D.L_STACK, 1)
    i_hat = j * A.FILL * r["a_slot"] / n_c1

    lam_a = r["lam_alpha"] * n_c1
    lam_b = (r["lam"]["B"] - r["lam"]["C"]) / math.sqrt(3.0) * n_c1

    # annulus torque, absolute estimator (D-016)
    from fem_magnetics import torque_annulus
    bands = torque_annulus(r["sol"], g.rotor_od / 2 + 1e-6,
                           g.stator_bore / 2 - 1e-6, 1.0, n_bands=4) * D.L_STACK
    t_ann = float(bands.mean())

    r_ph = D.RHO * 6 * n_c1**2 * D.MTL / (A.FILL * r["a_slot"])
    w_e = 2 * math.pi * (D.RPM / 60.0) * D.P_POLES
    w_m = 2 * math.pi * (D.RPM / 60.0)
    p_cu = 1.5 * r_ph * i_hat * i_hat
    p_mech = t_ann * w_m

    # perpendicular flux linkage implied by the torque (second route to Vhat)
    lam_perp = -t_ann / (1.5 * D.P_POLES * i_hat)

    out = {"delta": delta, "T": t_ann, "i": i_hat, "lam_a": lam_a,
           "lam_b": lam_b, "p_cu": p_cu, "p_mech": p_mech}
    for name, lb in (("geo", lam_b), ("tq", lam_perp)):
        vhat = math.hypot(r_ph * i_hat - w_e * lb, w_e * lam_a)
        out[f"vhat_{name}"] = vhat
        out[f"S_{name}"] = 1.5 * vhat * i_hat
        out[f"pf_{name}"] = (p_cu + p_mech) / max(1e-9, out[f"S_{name}"])
    return out


def run(step: float, j_mm2: float, out: str, base: bool = False,
        delta_op: float = DELTA_OP) -> int:
    H, B = load_bh_curve("M-43 Steel")
    n = int(round(30.0 / step))            # 0..29.9, one exact period
    print(f"pf cycle sweep 0..30 step {step} ({n} pts), J={j_mm2:.2f}, "
          f"{'BASE' if base else 'S6'}, delta_op={delta_op:.2f}", flush=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["delta_deg", "T", "i_hat", "lam_alpha", "lam_beta",
                    "p_cu", "p_mech", "vhat_geo", "vhat_tq",
                    "S_geo", "S_tq", "pf_geo", "pf_tq"])
        for k in range(n):
            d = k * step
            r = point(d, j_mm2, H, B, base, delta_op)
            w.writerow([f"{d:.2f}"] +
                       [f"{r[c]:.6f}" for c in ("T", "i", "lam_a", "lam_b",
                                                "p_cu", "p_mech")] +
                       [f"{r['vhat_geo']:.6f}", f"{r['vhat_tq']:.6f}",
                        f"{r['S_geo']:.6f}", f"{r['S_tq']:.6f}",
                        f"{r['pf_geo']:.6f}", f"{r['pf_tq']:.6f}"])
            f.flush()
            print(f"  {d:5.2f}  T={r['T']:6.3f}  Vhat={r['vhat_geo']:5.2f}"
                  f"/{r['vhat_tq']:5.2f} V  S={r['S_geo']:6.0f}/"
                  f"{r['S_tq']:6.0f} VA  PF={r['pf_geo']:.3f}/"
                  f"{r['pf_tq']:.3f}", flush=True)
    print(f"wrote {out}", flush=True)
    return analyse(out)


def analyse(path: str) -> int:
    rows = list(csv.DictReader(open(path)))
    if not rows:
        print("empty file")
        return 2
    col = {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}

    t = col["T"]
    r_rot = D.BORE / 2.0
    v_rot = math.pi * r_rot**2 * D.L_STACK
    print(f"\nn = {len(t)} over one 30 deg period "
          f"(delta {col['delta_deg'].min():.1f}..{col['delta_deg'].max():.1f})")
    print(f"mean torque        {t.mean():.4f} N.m   "
          f"(p-p {(t.max() - t.min()) / t.mean():.1%})")
    print(f"rotor volume       {v_rot * 1e6:.1f} cm3")
    print(f"air-gap shear      mean {t.mean() / (2 * v_rot) / 1e3:.2f} kPa   "
          f"peak {t.max() / (2 * v_rot) / 1e3:.2f} kPa      "
          f"[T = 2 * sigma * pi * r^2 * L]")
    print(f"current            {col['i_hat'][0]:.1f} A peak   "
          f"({col['i_hat'].std() / col['i_hat'].mean():.1e} spread)")

    for route in ("geo", "tq"):
        vh = col[f"vhat_{route}"]
        s = col[f"S_{route}"]
        pf = col[f"pf_{route}"]
        p_in = col["p_mech"] + col["p_cu"]
        print(f"\nroute {route} (Vhat from "
              f"{'phase linkages' if route == 'geo' else 'torque-implied lambda'}):")
        print(f"  Vhat            min {vh.min():.2f}  mean {vh.mean():.2f}  "
              f"max {vh.max():.2f} V   (point value at delta_op was one of these)")
        print(f"  S               mean {s.mean() / 1e3:.3f}  max {s.max() / 1e3:.3f} kVA")
        print(f"  PF instant      min {pf.min():.3f}  mean {pf.mean():.3f}  "
              f"max {pf.max():.3f}")
        print(f"  cycle PF        mean(P_in)/mean(S) = "
              f"{p_in.mean() / s.mean():.3f}   "
              f"mean(P_in)/max(S) = {p_in.mean() / s.max():.3f}")
        print(f"  rail use        {s.max() / 1e3:.3f} kVA of apparent power at "
              f"max Vhat")
        print(f"  voltage ceiling max-Vhat route: "
              f"{D.RPM * V_CEIL / vh.max():.0f} rpm   "
              f"point-Vhat route: {D.RPM * V_CEIL / vh.mean():.0f} rpm")
    return 0


def analyse_angles(specs: str, target: float = 1.6) -> int:
    """Compare current angles on torque per kVA at a fixed mean torque.

    Spec format: "26:/path/a.csv,20:/path/b.csv". Scaling to `target` uses the
    SynRM quadratic law at fixed angle (T proportional to i^2), so k = sqrt(target/T)
    and both S and P_cu scale as k^2. Linear-material estimate: the ranking is the
    claim, not the absolute.
    """
    rows = []
    for spec in specs.split(","):
        ang, path = spec.split(":", 1)
        ang = float(ang)
        recs = list(csv.DictReader(open(path)))
        c = {k: np.array([float(r[k]) for r in recs]) for k in recs[0]}
        t = c["T"].mean()
        k = math.sqrt(target / t)
        p_cu = c["p_cu"].mean() * k * k
        p_in = target * 2 * math.pi * D.RPM / 60.0 + p_cu
        s_mean = c["S_geo"].mean() * k * k
        s_max = c["S_geo"].max() * k * k
        rows.append({"angle": ang, "T": t, "k": k, "p_cu": p_cu,
                     "S_mean": s_mean, "S_max": s_max,
                     "PF": p_in / s_max,
                     "pf_pt": c["pf_geo"].mean()})

    base = next((r for r in rows if abs(r["angle"] - DELTA_OP) < 1e-6), None)
    print(f"target mean torque {target:.2f} N.m, {D.RPM:.0f} rpm, S6, J={J_DEEP:.2f}")
    print(f"{'angle':>6} {'T_mean':>8} {'i/i0':>6} {'P_cu':>7} {'S_mean':>8} {'S_max':>8} "
          f"{'PF':>6} {'S vs 26':>8}")
    for r in sorted(rows, key=lambda r: r["angle"]):
        rel = (r["S_max"] / base["S_max"] - 1.0) if base else float("nan")
        print(f"{r['angle']:6.1f} {r['T']:8.4f} {r['k']:6.3f} {r['p_cu']:7.2f} "
              f"{r['S_mean']/1e3:8.3f} {r['S_max']/1e3:8.3f} {r['PF']:6.3f} {rel:+8.1%}")
    if base:
        print("\nP1 (adopt an angle only if S_max drops >=5% and P_cu <= 40 W):")
        ok = [r for r in rows if abs(r["angle"] - DELTA_OP) > 1e-6
              and r["S_max"] <= 0.95 * base["S_max"] and r["p_cu"] <= 40.0]
        best = min(rows, key=lambda r: r["S_max"])
        print(f"  minimum S_max at {best['angle']:.1f} deg, "
              f"{best['S_max']/1e3:.3f} kVA ({best['S_max']/base['S_max']:+0.1%} vs 26.0), "
              f"P_cu {best['p_cu']:.1f} W")
        print(f"  angles passing: {[r['angle'] for r in ok] or 'none'}")
        print(f"  verdict: {'ADOPT ' + str(best['angle']) if ok else 'KEEP 26.0 deg'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=float, default=2.0)
    ap.add_argument("--j", type=float, default=J_DEEP)
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--delta-op", type=float, default=DELTA_OP)
    ap.add_argument("--out", default="/tmp/opencode/m1/pf_cycle.csv")
    ap.add_argument("--analyse")
    ap.add_argument("--angles")
    ap.add_argument("--target", type=float, default=1.6)
    a = ap.parse_args()
    if a.analyse:
        return analyse(a.analyse)
    if a.angles:
        return analyse_angles(a.angles, a.target)
    H, B = load_bh_curve("M-43 Steel")
    return run(a.step, a.j, a.out, a.base, a.delta_op)


if __name__ == "__main__":
    raise SystemExit(main())
