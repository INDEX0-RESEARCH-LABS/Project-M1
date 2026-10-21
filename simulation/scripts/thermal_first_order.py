"""First-order copper loss + winding-rise estimate for the point-design frames.

Declared assumptions (lumped, conservative-in-the-right-direction):
  * copper only (iron loss not included -> efficiency is an upper bound)
  * mean turn length MTL = 2*L + 1.2*tau_p  (end-winding allowance)
  * ONE TURN SPANS TWO SLOTS, so the copper volume that MTL multiplies is a
    HALF-turn volume: V_cu = N_SLOTS*FILL*A_slot*(MTL/2). Using MTL directly
    double-counts the end winding (factor-2 loss error; fixed in addendum 9).
  * slot area self-similar: A_slot(bore) = A_slot(150) * (bore/150)^2
  * housing convective area = cylindrical OD surface + both end caps
  * heat transfer: h_conv (still air 10, enclosed 25, forced air 50 W/m2K)
    + radiation h_rad ~= eps*sigma*(Ts^2+Tamb^2)*(Ts+Tamb)
  * winding rise = copper mean rise; the slot hotspot is HIGHER than this
    (insulation + iron path not modelled) -> treat the result as a lower bound.
  * the J passed in is the FEM PEAK slot current density (the 3-phase set is
    solved at the instant phase A peaks); the copper loss uses the RMS value,
    J_rms = J/sqrt(2). Using J directly is a factor-2 loss error.

Use: python thermal_first_order.py
"""
from __future__ import annotations

import math

RHO20 = 1.75e-8
ALPHA = 0.00393
T_AMB = 40.0
EPS = 0.85
SIGMA = 5.670e-8
A_SLOT_150 = 76.1e-6          # measured on the validated 150 mm frame (mesh)
OD_RATIO = 1.4467
N_SLOTS = 36
FILL = 0.40


def estimate(bore: float, L: float, J: float, h_conv: float) -> dict:
    k = bore / 0.150
    a_slot = A_SLOT_150 * k * k
    tau_p = math.pi * bore / 4.0
    mtl = 2.0 * L + 1.2 * tau_p
    v_cu = N_SLOTS * FILL * a_slot * (mtl / 2.0)   # one turn = two slots
    r_th = 1.0 / (h_conv + 6.0)               # 6 W/m2K radiation, fixed first pass
    d_out = bore * OD_RATIO
    area = math.pi * d_out * L + 2 * math.pi / 4 * d_out**2
    p_cu = RHO20 * (0.5 * J * J) * v_cu       # J is peak, loss uses RMS
    # iterate copper temperature (resistivity feedback) with fixed thermal R
    t = T_AMB + 20.0
    for _ in range(40):
        rho = RHO20 * (1 + ALPHA * (t - 20.0))
        p = rho * (0.5 * J * J) * v_cu
        t_new = T_AMB + p * r_th / area
        t = 0.5 * (t + t_new)
    rho = RHO20 * (1 + ALPHA * (t - 20.0))
    p_cu = rho * (0.5 * J * J) * v_cu
    return {"bore": bore, "L": L, "J": J, "h": h_conv, "v_cu_cm3": v_cu * 1e6,
            "p_cu": p_cu, "area_cm2": area * 1e4, "q_kWm2": p_cu / area / 1e3,
            "t_cu": t, "rise": t - T_AMB}


def main() -> None:
    frames = [(0.120, 0.074, "120/74 compact OD"), (0.130, 0.0504, "130/50 short")]
    for bore, L, name in frames:
        t_per_m = {0.120: 26.92, 0.130: 39.67}[bore]      # rows40, this campaign
        p_mech = t_per_m * L * (3000 * 2 * math.pi / 60)
        print(f"\n{name}: bore {bore*1e3:.0f} mm, L {L*1e3:.1f} mm, "
              f"P_mech(1.6 N.m short of full)={1.6*(3000*2*math.pi/60):.0f} W, "
              f"frame capability {t_per_m*L:.2f} N.m")
        for h, label in ((10.0, "still air"), (25.0, "enclosed"),
                         (50.0, "forced air")):
            r = estimate(bore, L, 6.0e6, h)
            print(f"  J=6, {label:10s} h={h:4.1f}: P_cu={r['p_cu']:6.1f} W  "
                  f"q={r['q_kWm2']:5.2f} kW/m2  T_cu={r['t_cu']:5.1f} C  "
                  f"rise={r['rise']:5.1f} K")
        for J in (3.0e6, 5.34e6, 6.0e6):
            r = estimate(bore, L, J, 25.0)
            print(f"  J={J/1e6:.2f} (peak), enclosed: P_cu={r['p_cu']:6.1f} W  "
                  f"rise={r['rise']:5.1f} K")

    # self-check: the copper-loss route used here must equal 3*Irms^2*R_ph.
    #   rho*(J^2/2)*V_cu  ==  9*rho*J^2*FILL*A_slot*MTL
    # with V_cu = 36*FILL*A_slot*(MTL/2)  (a turn spans two slots)
    a_slot = A_SLOT_150 * (0.120 / 0.150) ** 2
    tau_p = math.pi * 0.120 / 4.0
    mtl = 2.0 * 0.074 + 1.2 * tau_p
    p_thermal = RHO20 * 0.5 * (6e6) ** 2 * N_SLOTS * FILL * a_slot * (mtl / 2)
    p_winding = 9 * RHO20 * (6e6) ** 2 * FILL * a_slot * mtl
    assert abs(p_thermal - p_winding) / p_winding < 1e-12, "loss routes disagree"
    print(f"\ncross-check J=6, 120/74: rho*J_rms^2*V_cu = {p_thermal:.2f} W "
          f"== 3*Irms^2*R_ph route = {p_winding:.2f} W")

    # self-check: loss must scale with J^2 and with copper volume
    a = estimate(0.120, 0.074, 6e6, 25.0)["p_cu"]
    b = estimate(0.120, 0.074, 3e6, 25.0)["p_cu"]
    # above 4.0 is expected: higher J -> higher copper T -> higher rho (Joule feedback)
    assert 4.0 <= a / b < 4.9, f"J^2 scaling broken: {a/b:.2f}"
    assert estimate(0.130, 0.0504, 6e6, 25.0)["p_cu"] > 0
    print("\nself-check: J^2 scaling OK")


if __name__ == "__main__":
    main()
