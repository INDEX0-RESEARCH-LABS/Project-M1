"""Rotor mechanical check (Gate-D prep) per prototype/rotor_stress/PLAN.md.

Zero-spend analytic first cut: continuous surface ring hoop stress (M-A), spoke
junction stress as a solid-disk slice (M-B), Kt band, SF against a conservative
yield. All models declared in the PLAN before this run.

Run:  .venv/bin/python simulation/scripts/rotor_stress_check.py
"""
from __future__ import annotations

import math

from rajini_anchor import AIRGAP, BORE

RHO = 7870.0          # kg/m^3, M-43-class electrical steel
NU = 0.30
SIGMA_Y = 230e6       # Pa, declared conservative (PLAN)
KT_BAND = (1.5, 2.0, 3.0)
BRIDGES = (0.0006, 0.0004)
RPMS = range(1000, 15001, 1000)

R_OUT = (BORE - 2 * AIRGAP) / 2
R_SHAFT = 0.012


def hoop_pa(rpm: float, bridge: float) -> float:
    """M-A: thin continuous free ring, self centripetal hoop stress."""
    omega = 2 * math.pi * rpm / 60
    r_m = R_OUT - bridge  # ring inner radius = peak hoop location for a free spinning ring
    return RHO * omega**2 * r_m**2


def spoke_pa(rpm: float) -> float:
    """M-B: spoke/d-axis column junction stress as a solid-disk slice, r=R_shaft."""
    omega = 2 * math.pi * rpm / 60
    return (RHO * omega**2 / 8) * ((3 + NU) * R_OUT**2 - (1 + NU) * R_SHAFT**2)


def main() -> None:
    print(f"R_out={R_OUT*1e3:.3f} mm  ring=continuous annulus (verified in PLAN)")
    print(f"sigma_y={SIGMA_Y/1e6:.0f} MPa (declared conservative)  Kt band {KT_BAND}")
    print("\nper-rpm table — sigma_max = Kt * max(M-A, M-B):")
    head = "rpm | " + " | ".join(f"SF@Kt={k}" for k in KT_BAND)
    print(head)
    for rpm in RPMS:
        sigma = max(hoop_pa(rpm, max(BRIDGES)), spoke_pa(rpm))  # worst ring variant
        sfs = [SIGMA_Y / (k * sigma) for k in KT_BAND]
        print(f"{rpm:5d} | " + " | ".join(f"{sf:6.1f}" for sf in sfs))

    # SF crossing speeds for the committed bridge under each Kt
    print("\nSF crossing speeds (committed b=0.6mm / winner-variant b=0.4mm):")
    for bridge in BRIDGES:
        marks = []
        for target in (2.0, 1.5, 1.0):
            rpm_c = next((r for r in RPMS
                          if SIGMA_Y / (max(KT_BAND) * max(hoop_pa(r, bridge),
                                                           spoke_pa(r))) < target),
                         None)
            marks.append(f"SF<{target}: {rpm_c if rpm_c else '>15k'} rpm")
        print(f"  b={bridge*1e3:.1f}mm: " + ", ".join(marks))

    # airgap-closure sanity at the worst credible table point
    rpm = RPMS[-1]
    omega = 2 * math.pi * rpm / 60
    eps = max(hoop_pa(rpm, max(BRIDGES)), spoke_pa(rpm)) / (210e9 * (1 - 0.3**2))
    dilation = eps * R_OUT
    print(f"\nairgap-closure sanity @{rpm} rpm: ring dilation ~{dilation*1e6:.1f} um "
          f"(airgap {AIRGAP*1e6:.0f} um) -> "
          + ("negligible" if dilation < 0.2 * AIRGAP else "CHECK"))

    # self-checks (non-trivial logic)
    assert hoop_pa(0, 0.0006) == 0.0
    # thin-ring self stress is bridge-thickness independent within Kt=3 margin
    a, b = hoop_pa(6000, 0.0006), hoop_pa(6000, 0.0004)
    assert abs(a - b) / a < 0.05


if __name__ == "__main__":
    main()
