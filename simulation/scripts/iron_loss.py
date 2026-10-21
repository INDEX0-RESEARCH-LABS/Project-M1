"""First-order iron loss at the 130/50 point design (gates in validation/iron_loss/PLAN.md).

Anchor: the grade guarantee, not an invented Steinmetz coefficient.
"M400-50A" means 4.00 W/kg at 1.5 T / 50 Hz by definition of EN 10106, and the
repo's material survey confirms catalogs publish loss but not B-H curves.

IMPORTANT: the grade number is at 50 Hz, but this machine runs at
f_e = p * rpm / 60 = 2 * 3000 / 60 = **100 Hz** (3000 rpm is 50 Hz MECHANICAL).
Scaling from the guarantee needs the hysteresis/eddy split, which is not
published, so it is declared as a band s = eddy fraction at 50 Hz:

    P(f) = p_ref * [ (1-s) * (f/50) + s * (f/50)^2 ] * (B/1.5)^n

    P_fe = sum_e  that factor * rho * A_e * L_stack

Rotational loss, excess loss and the building factor are NOT modelled (lower bound);
rotor slot-harmonic loss is NOT modelled and the 100 Hz rotor term is reported as an
upper bound for the fundamental only, separately.

Use: python iron_loss.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rajini_anchor as A  # noqa: E402
from dq_model import BORE, DELTA_OP, L_STACK, solve_point  # noqa: E402
from fem_magnetics import load_bh_curve  # noqa: E402

RHO_ST = 7650.0          # kg/m3, non-oriented electrical steel
B_REF, F_REF = 1.5, 50.0
F_ELEC = 100.0           # p=2 pole pairs at 3000 rpm: 2*3000/60 = 100 Hz
P_REF = (3.3, 4.0, 5.3)  # W/kg at 1.5 T / 50 Hz: M350-50A / M400-50A / M530-50A
EXPONENTS = (1.6, 1.8, 2.0)   # hysteresis-dominated .. eddy-dominated
EDDY_SPLIT = (0.3, 0.45, 0.6)  # eddy fraction at 50 Hz (declared band, not fitted)
P_CU_HOT = {5.34: 53.1, 6.0: 68.3}   # from thermal_first_order.py, enclosed h=25
TARGET = 5.34


def freq_factor(s: float) -> float:
    """Scale a 50 Hz guarantee to F_ELEC with eddy fraction s at 50 Hz."""
    r = F_ELEC / F_REF
    return (1.0 - s) * r + s * r * r


def equivalent_mass(b: np.ndarray, areas: np.ndarray, n: float) -> float:
    """Mass of steel that would lose the same power at B_ref: sum rho*A*L*(B/1.5)^n."""
    return float((RHO_ST * (b / B_REF) ** n * areas * L_STACK).sum())


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    print(f"bore {BORE*1e3:.0f} mm, L {L_STACK*1e3:.1f} mm, delta {DELTA_OP} deg, "
          f"f_e = {F_ELEC:.0f} Hz (guarantee at {F_REF:.0f} Hz, scaled)")

    # F2: the functional must reproduce B^n exactly on a synthetic field
    a = np.array([1e-4])
    for n in EXPONENTS:
        gain = (equivalent_mass(np.array([2 * B_REF]), a, n)
                / equivalent_mass(np.array([B_REF]), a, n))
        assert abs(gain - 2**n) < 1e-9, f"B^n scaling broken at n={n}: {gain}"
    print("F2 PASS: B^n scaling exact for n = 1.6 / 1.8 / 2.0")

    for j_mm2 in (TARGET, 6.0):
        r = solve_point(DELTA_OP, j_mm2 * 1e6, H, B)
        be, ar, regions = r["Belem"], r["areas"], r["regions"]
        print(f"\nJ={j_mm2:.2f}: T={r['T']*L_STACK:.3f} N.m  Bmax={r['Bmax']:.2f} T")
        tot = {}
        for name in ("stator_iron", "rotor_iron"):
            cells = np.asarray(regions[name], dtype=np.int64)
            b = be[cells]
            area = float(ar[cells].sum())
            vol = area * L_STACK
            mass = RHO_ST * vol
            print(f"  {name:12s}: area {area*1e4:8.1f} cm2  vol {vol*1e6:7.1f} cm3  "
                  f"mass {mass:5.2f} kg  B mean {b.mean():.2f}  p95 {np.percentile(b,95):.2f}  "
                  f"max {b.max():.2f} T")
            for n in EXPONENTS:
                tot[(name, n)] = equivalent_mass(b, ar[cells], n)

        # F1: stator volume against the closed-form annulus minus slots
        cells = np.asarray(regions["stator_iron"], dtype=np.int64)
        area_fem = float(ar[cells].sum())
        d_out = 0.217 * (BORE / 0.150)
        area_cf = math.pi / 4 * (d_out**2 - BORE**2) - A.N_SLOTS * r["a_slot"]
        dev = area_fem / area_cf - 1
        print(f"  F1 stator area: FEM {area_fem*1e4:.2f} cm2 vs annulus-slots "
              f"{area_cf*1e4:.2f} cm2  ({dev:+.1%}, gate 5%: "
              f"{'PASS' if abs(dev) <= 0.05 else 'FAIL'})")

        combos = []
        for p_ref in P_REF:
            for n in EXPONENTS:
                for s in EDDY_SPLIT:
                    p = (p_ref * freq_factor(s)
                         * (tot[("stator_iron", n)] + tot[("rotor_iron", n)]))
                    combos.append((p_ref, n, s, p))
        combos.sort(key=lambda c: c[3])
        ps = [c[3] for c in combos]
        med = combos[len(combos) // 2]
        print(f"  P_fe at {F_ELEC:.0f} Hz, {len(combos)} combos: min {ps[0]:.1f} W  "
              f"median {med[3]:.1f} W  max {ps[-1]:.1f} W   "
              f"(median: {med[0]} W/kg, n={med[1]}, eddy {med[2]})")
        f_mid = freq_factor(0.45)
        p_st = 4.0 * f_mid * tot[("stator_iron", 1.8)]
        p_ro = 4.0 * f_mid * tot[("rotor_iron", 1.8)]
        print(f"  split at 4.0 W/kg, n=1.8, s=0.45 (f x{f_mid:.2f}): stator {p_st:.1f} W  "
              f"rotor {p_ro:.1f} W (rotor = UPPER BOUND, fundamental only)")
        p_cu = P_CU_HOT[j_mm2]
        p_mech = r["T"] * L_STACK * 2 * math.pi * 50
        eff_cu = p_mech / (p_mech + p_cu)
        for label, p_fe in (("min", ps[0]), ("median", med[3]), ("max", ps[-1])):
            eff = p_mech / (p_mech + p_cu + p_fe)
            print(f"  efficiency {label:6s} iron ({p_fe:4.1f} W): "
                  f"{eff*100:.1f}%  (copper-only {eff_cu*100:.1f}%)")
        print(f"  P_fe/P_cu: min {ps[0]/p_cu:.2f}  median {med[3]/p_cu:.2f}  "
              f"max {ps[-1]/p_cu:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
