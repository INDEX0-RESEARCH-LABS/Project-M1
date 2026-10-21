"""48 V / 96 V table + PF vs current angle at the 130/50 point design.

Gates are declared in validation/voltage_and_angle/PLAN.md before this ran.
The field solve is `dq_model.solve_point` (same certified solver, 1536 rays,
4 gap rows); nothing about torque or flux extraction is re-derived here.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dq_model as D          # noqa: E402  (constants + solve_point)
import rajini_anchor as A     # noqa: E402
from fem_magnetics import load_bh_curve  # noqa: E402

ANGLES = (12.0, 16.0, 20.0, 24.0, 26.25, 28.0, 32.0, 36.0, 40.0, 44.0)
J = 5.34e6                    # the 1.592 N.m target (T ~ J^2)
T_TARGET = 1.592
P_SHAFT = 500.0               # W, = 1.592 N.m * 314.16 rad/s
ETA = 0.927                   # STATUS.md, with iron (ESTIMATE)
LAM_EXP = 0.90                # lambda_par ~ i^0.90, fitted on the 3 certified J levels

# --- voltage table: exact turns scaling from the k=1 reference state ----------
# base: k=1 -> i=102.1 A peak, Vhat(3000 rpm)=6.52 V, S=999 VA
I1, V1 = 102.1, 6.52
S1 = 1.5 * V1 * I1
V_CEIL_48, V_CEIL_96 = 26.33, 52.66
WIRE_AREA_K1 = 4.58           # mm2, winding_spec_v1 section 3


def voltage_table() -> None:
    print("voltage option table (exact turns scaling; S = P/PF is invariant)")
    print("  Vbus  k  turns/coil  I peak  R_ph     Vhat@3000  C-rate?  "
          "speed ceiling   S")
    rows = ((48.0, 2), (96.0, 2), (96.0, 4))
    for vbus, k in rows:
        i = I1 / k
        r_ph = 1.53e-3 * k * k
        vhat = V1 * k
        ceil_v = V_CEIL_48 if vbus == 48.0 else V_CEIL_96
        n_max = 3000.0 * ceil_v / vhat
        s = 1.5 * vhat * i
        print(f"  {vbus:4.0f} {k:2d} {5*k:10d} {i:7.1f} {r_ph*1e3:6.2f} mOhm "
              f"{vhat:9.2f} V        {n_max:8.0f} rpm {s:7.0f} VA")
        # V1: apparent power is invariant, current/voltage trade exactly
        assert abs(s - S1) / S1 < 1e-12, "S not invariant under turns scaling"
    # V2: 96 V at k=4 halves the current only because turns double; check area
    area = WIRE_AREA_K1 / 4
    print(f"  V2: 96 V/k=4 implies {20} turns/coil at {area:.2f} mm2 per turn "
          f"(1 x 1.2 mm), same copper area, same slot fill")
    print("  -> 96 V buys current and speed headroom; it does NOT change kVA")
    print(f"  -> controller VA is set by PF: S = {P_SHAFT/ETA/0.55:.0f} VA at PF 0.55, "
          f"{P_SHAFT/ETA/0.60:.0f} VA at 0.60\n")


def angle_check(H, B, angles) -> int:
    """Re-solve selected angles on a finer mesh (rays and gap rows).

    The 10-point sweep shows torque jumping 0.881 -> 1.761 N.m between 32 and 36 deg,
    which is far above any plausible SynRM torque ripple. Either the machine really
    ripples that hard (a design problem) or the torque extractor is mesh-phase
    sensitive (a measurement problem). This separates the two.
    """
    print("\nangle check: torque vs mesh refinement (J=5.34)")
    print("angle   1536/r4   1536/r10  3072/r10  drift(3072/r10 vs 1536/r4)")
    for d in angles:
        out = []
        for n_theta, rows in ((1536, 4), (1536, 10), (3072, 10)):
            r = D.solve_point(d, J, H, B, n_theta=n_theta, rows=rows)
            out.append(r["T"] * D.L_STACK)
        drift = out[2] / out[0] - 1
        print(f"{d:5.2f} {out[0]:9.3f} {out[1]:10.3f} {out[2]:9.3f} "
              f"{drift:+9.1%}")
    return 0


def main() -> int:
    voltage_table()
    H, B = load_bh_curve("M-43 Steel")
    n_c1 = D.turns(D.BORE, D.L_STACK, 1)
    w_m = 2 * math.pi * (D.RPM / 60)
    w_e = w_m * D.P_POLES
    print(f"sweep: J={J/1e6:.2f} A/mm2, n_theta=1536, rows=4, "
          f"N_c(a=1)={n_c1:.3f}")
    print("angle   T[N.m]  i[A]   Vhat[V]  Pcu[W]  PF     S[VA]   "
          "| at 0.5 kW: i'[A]  Pcu'[W]  PF'    S'[VA]")
    out = {}
    for d in ANGLES:
        r = D.solve_point(d, J, H, B)
        i = J * A.FILL * r["a_slot"] / n_c1
        t_nm = r["T"] * D.L_STACK
        lam_par = r["lam_alpha"] * n_c1
        lam_perp = r["T"] * D.L_STACK / (1.5 * D.P_POLES * i)
        r_ph = D.RHO * 6 * n_c1**2 * D.MTL / (A.FILL * r["a_slot"])
        vhat = math.hypot(r_ph * i + w_e * lam_perp, w_e * lam_par)
        p_cu = 1.5 * r_ph * i * i
        p_mech = t_nm * w_m
        pf = (p_cu + p_mech) / (1.5 * vhat * i)
        # equal-output correction: same 0.5 kW, so PF is comparable across angles
        ratio = T_TARGET / t_nm
        i2 = i * math.sqrt(ratio)
        lam_par2 = lam_par * ratio ** (LAM_EXP / 2)
        lam_perp2 = lam_perp * math.sqrt(ratio)
        vhat2 = math.hypot(r_ph * i2 + w_e * lam_perp2, w_e * lam_par2)
        p_cu2 = p_cu * ratio
        pf2 = (p_cu2 + P_SHAFT) / (1.5 * vhat2 * i2)
        s2 = 1.5 * vhat2 * i2
        out[d] = {"T": t_nm, "i": i, "vhat": vhat, "pcu": p_cu, "pf": pf,
                  "s": 1.5 * vhat * i, "i2": i2, "pcu2": p_cu2, "pf2": pf2,
                  "s2": s2}
        print(f"{d:5.2f} {t_nm:8.3f} {i:6.1f} {vhat:8.2f} {p_cu:7.1f} "
              f"{pf:6.3f} {1.5*vhat*i:6.0f}   | {i2:10.1f} {p_cu2:8.1f} "
              f"{pf2:6.3f} {s2:7.0f}")

    ref = out[D.DELTA_OP]
    # A1: the harness must reproduce the certified operating point
    ok_t = abs(ref["T"] / T_TARGET - 1) <= 0.02
    ok_pf = 0.53 <= ref["pf"] <= 0.58
    print(f"\nA1 regression at {D.DELTA_OP} deg: T={ref['T']:.3f} N.m "
          f"({ref['T']/T_TARGET-1:+.1%}, {'PASS' if ok_t else 'FAIL'}), "
          f"PF={ref['pf']:.3f} ({'PASS' if ok_pf else 'FAIL'})")
    assert ok_t and ok_pf, "sweep harness does not reproduce the certified point"

    # A2/A3: adopt only a gain >= 0.03 that also exceeds the 0.05 bracket width
    best = max(out.values(), key=lambda r: r["pf2"])
    d_best = [d for d, r in out.items() if r is best][0]
    gain = best["pf2"] - ref["pf2"]
    print(f"A2 strongest angle {d_best:.2f} deg: PF'={best['pf2']:.3f} vs "
          f"ref {ref['pf2']:.3f} (gain {gain:+.3f}), "
          f"T(J=5.34)={best['T']:.3f} N.m "
          f"({best['T']/T_TARGET:.1%} of target)")
    keep_t = best["T"] >= 0.98 * T_TARGET
    if gain >= 0.03 and keep_t:
        print(f"A2 PASS: adopt {d_best:.2f} deg -> S' {best['s2']:.0f} VA "
              f"vs {ref['s2']:.0f} VA")
    else:
        print("A2 FAIL: no angle delivers +0.03 PF at >=98% torque "
              "-> PF is a rotor property, not a control setting")
    if abs(gain) < 0.05:
        print(f"A3: gain {gain:+.3f} is inside the 0.05 bracket width "
              "-> not resolvable at this model fidelity")
    else:
        print(f"A3: gain {gain:+.3f} exceeds the bracket width -> real at this fidelity")
    return 0


if __name__ == "__main__":
    if "--angle-check" in sys.argv:
        _H, _B = load_bh_curve("M-43 Steel")
        raise SystemExit(angle_check(_H, _B, (26.25, 32.0, 36.0)))
    raise SystemExit(main())
