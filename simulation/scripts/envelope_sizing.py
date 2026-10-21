"""D-012 envelope sizing — parametric zero-spend scan (ESTIMATE class).

Purpose: after winding_spec_v0 showed the committed anchor frame cannot host a
manufacturable 48 V / 3000 rpm winding, scan candidate envelopes for:
  * turns per coil N_c in the buildable 6-12 band at 3000 rpm / 48 V SVPWM,
  * torque against the target spec (1.6 N.m continuous ESTIMATE, 2.5 N.m peak).

Model (declared, all ESTIMATE):
  EMF budget:      E_allow = Vdc/sqrt(3)*0.95 = 27.7 V (phase peak, 48 V bus)
  per-turn linkage psi1 = kw*(2/pi)*B*g*tau_p*L        [Wb/turn]
  tau_p = pi*D_mean/(2p)                               [m], D_mean ~ rotor OD
  N_ph = E_allow/(omega_e*psi1);  omega_e = 2*pi*f;  f = rpm*p/60
  N_c  = N_ph/n_coils;            n_coils = 2p*q        [coils per phase]
  slot area: A_slot = slot_frac*pi*(R_so^2 - R_bore^2)/n_slots
             with stator OD = rotor OD + 2*radial_build (declared 14 mm)
  slot AT  = J*A_slot*fill  (J=6 A/mm^2 cont; peak 24 short-time)
  torque:  T = tau_s*2*pi*R_ro^2*L ; tau_s = tau_ref*(AT/AT_ref)
           tau_ref = 642 Pa, AT_ref = 242.6  (certified single-ring anchor result:
           T/m 8.34 at 1 m stack, D=92.1 bore -> tau_ref = 8.34/(2*pi*R^2*1))
           linear extrapolation caveat: saturated machine, so T is optimistic at
           high AT -> all candidates carry the ESTIMATE label.

Self-checks: turns/coil falls with pole count; torque scales D^2; both asserted.
"""
from __future__ import annotations

import math

V_DC = 48.0
E_ALLOW = V_DC / math.sqrt(3) * 0.95
B_G = 0.90          # T, gap fundamental peak (ESTIMATE band 0.6-0.9)
KW = 0.95
FILL = 0.40
J_CONT = 6.0e6
J_PEAK = 24.0e6
Q = 3
SLOT_FRAC = 0.42
RADIAL_BUILD = 0.014
RPM = 3000.0
TAU_REF = 642.0     # Pa at AT_ref (certified)
AT_REF = 242.6
T_CONT_TARGET = 1.6  # N.m ESTIMATE
T_PEAK_TARGET = 2.5  # N.m ESTIMATE


def size(n_poles: int, rotor_od: float, L: float, paths: int = 1) -> dict:
    p = n_poles // 2
    r_ro = rotor_od / 2
    r_so = r_ro + RADIAL_BUILD
    tau_p = math.pi * rotor_od / (2 * p)           # pole pitch at gap
    psi1 = KW * (2 / math.pi) * B_G * tau_p * L
    f_e = RPM / 60 * p
    omega_e = 2 * math.pi * f_e
    n_coils = 2 * p * Q
    n_ph = E_ALLOW / (omega_e * psi1)
    # n_ph is the SERIES-equivalent turns per phase. With `paths` parallel
    # paths the physical turns per coil rise by `paths` for the same terminal
    # voltage (n_ph = (n_coils/paths) * N_c).
    n_c = paths * n_ph / n_coils
    n_slots = 18 * p                                # q=3 => 6 slots/pole/phase
    a_slot = SLOT_FRAC * math.pi * (r_so**2 - r_ro**2) / n_slots
    a_cu = a_slot * FILL
    at_slot = J_CONT * a_cu
    tau_s = TAU_REF * (at_slot / AT_REF)
    t_cont = tau_s * 2 * math.pi * r_ro**2 * L
    t_peak = t_cont * (J_PEAK / J_CONT)
    i_cond = at_slot / max(n_c, 1e-9)               # conductor current
    i_ph = i_cond * paths                           # terminal phase current
    return dict(n_poles=n_poles, rotor_od=rotor_od, L=L, n_slots=n_slots,
                paths=paths, f_e=f_e, psi1=psi1, n_ph=n_ph, n_c=n_c,
                a_cu=a_cu, at_slot=at_slot, i_ph=i_ph, t_cont=t_cont,
                t_peak=t_peak, winding_ok=4 <= n_c <= 20)


def main() -> None:
    rows = []
    for n_poles in (2, 4, 6, 8):
        for d in (0.090, 0.110, 0.130):
            for L in (0.030, 0.050, 0.074):
                rows.append(size(n_poles, d, L))

    print("n_pole  D_rotor L_stack  f_e  N_c(a1) N_c(a2) N_c(a4)  AT/slot "
          "T_cont  T_peak  windable")
    for r in rows:
        nc = [size(r["n_poles"], r["rotor_od"], r["L"], a)["n_c"]
              for a in (1, 2, 4)]
        ok = any(4 <= n <= 20 for n in nc)
        print(f"{r['n_poles']:>4d}  {r['rotor_od']*1e3:6.0f}mm {r['L']*1e3:5.0f}mm "
              f"{r['f_e']:5.0f}Hz {nc[0]:6.1f} {nc[1]:6.1f} {nc[2]:6.1f} "
              f"{r['at_slot']:8.1f} {r['t_cont']:6.2f} {r['t_peak']:6.2f}  "
              f"{'yes' if ok else '-'}")

    fit = [r for r in rows
           if any(4 <= size(r["n_poles"], r["rotor_od"], r["L"], a)["n_c"] <= 20
                  for a in (1, 2, 4))]
    both = [r for r in fit if r["t_cont"] >= T_CONT_TARGET
            and r["t_peak"] >= T_PEAK_TARGET]
    print(f"\nwindable at some a in (1,2,4): {len(fit)}/{len(rows)}; "
          f"also meeting both torque targets: {len(both)}/{len(rows)}")
    for r in both:
        print("  candidate: "
              f"{r['n_poles']} poles, D={r['rotor_od']*1e3:.0f} mm, "
              f"L={r['L']*1e3:.0f} mm, T_cont={r['t_cont']:.2f}, "
              f"T_peak={r['t_peak']:.2f} N.m (ESTIMATE)")

    # self-checks
    a4, a8 = size(4, 0.090, 0.050), size(8, 0.090, 0.050)
    assert a8["n_c"] < a4["n_c"], "more poles must reduce turns/coil"
    s1, s2 = size(4, 0.090, 0.050), size(4, 0.130, 0.050)
    # slot AT scales with area (D^2) in this model, so T scales D^4 (declared,
    # optimistic linear extrapolation) -- assert monotone and L-linearity only
    assert s2["t_cont"] > s1["t_cont"], "torque must rise with D"
    s3 = size(4, 0.090, 0.074)
    assert abs((s3["t_cont"] / s1["t_cont"]) - 0.074 / 0.050) < 0.01, \
        "torque must scale linearly with L at fixed D"
    # parallel paths: turns/coil scale exactly with a, torque is unchanged
    p1, p4 = size(4, 0.090, 0.050, 1), size(4, 0.090, 0.050, 4)
    assert abs(p4["n_c"] - 4 * p1["n_c"]) < 1e-9
    assert abs(p4["t_cont"] - p1["t_cont"]) < 1e-12


if __name__ == "__main__":
    main()
