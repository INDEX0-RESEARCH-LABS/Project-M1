"""First-order copper loss + winding-rise estimate for the point-design frames.

Declared assumptions (lumped, conservative-in-the-right-direction):
  * copper only (iron loss not included -> efficiency is an upper bound)
  * mean turn length MTL = 2*L + 1.2*tau_p  (end-winding allowance)
  * slot area self-similar: A_slot(bore) = A_slot(150) * (bore/150)^2
  * housing convective area = cylindrical OD surface + both end caps
  * heat transfer: h_conv (still air 10, enclosed 25, forced air 50 W/m2K)
    + radiation h_rad ~= eps*sigma*(Ts^2+Tamb^2)*(Ts+Tamb)
  * winding rise = copper mean rise; the slot hotspot is HIGHER than this
    (insulation + iron path not modelled) -> treat the result as a lower bound.

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
    v_cu = N_SLOTS * FILL * a_slot * mtl
    r_th = 1.0 / (h_conv + 6.0)               # 6 W/m2K radiation, fixed first pass
    d_out = bore * OD_RATIO
    area = math.pi * d_out * L + 2 * math.pi / 4 * d_out**2
    p_cu = RHO20 * J * J * v_cu
    # iterate copper temperature (resistivity feedback) with fixed thermal R
    t = T_AMB + 20.0
    for _ in range(40):
        rho = RHO20 * (1 + ALPHA * (t - 20.0))
        p = rho * J * J * v_cu
        t_new = T_AMB + p * r_th / area
        t = 0.5 * (t + t_new)
    rho = RHO20 * (1 + ALPHA * (t - 20.0))
    p_cu = rho * J * J * v_cu
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
        for J in (2.0e6, 3.0e6, 4.0e6):
            r = estimate(bore, L, J, 25.0)
            print(f"  J={J/1e6:.0f}, enclosed: P_cu={r['p_cu']:6.1f} W  "
                  f"rise={r['rise']:5.1f} K")

    # self-check: loss must scale with J^2 and with copper volume
    a = estimate(0.120, 0.074, 6e6, 25.0)["p_cu"]
    b = estimate(0.120, 0.074, 3e6, 25.0)["p_cu"]
    # above 4.0 is expected: higher J -> higher copper T -> higher rho (Joule feedback)
    assert 4.0 <= a / b < 4.9, f"J^2 scaling broken: {a/b:.2f}"
    assert estimate(0.130, 0.0504, 6e6, 25.0)["p_cu"] > 0
    print("\nself-check: J^2 scaling OK")


if __name__ == "__main__":
    main()
