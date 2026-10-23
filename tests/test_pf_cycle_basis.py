"""Pins the D-022 finding: PF is a cycle quantity, not a peak-angle one.

Pure arithmetic on the certified state, so it costs no solves. The point is to
stop 0.578 from being quoted as a design number again: it is the value at the
single rotor angle where the machine is producing its peak torque, and the
period-average real power is set by the mean torque instead.

Data: simulation/validation/pf_cycle/RESULT.md, /tmp/opencode/m1/pf_cycle.csv.
"""
from __future__ import annotations

import math

RPM = 3000.0
W_M = 2 * math.pi * RPM / 60.0
T_MEAN = 1.2305        # certified mean torque, 0.5 deg sweep (D-021)
T_PEAK = 1.739         # certified peak-angle torque (D-016/D-021)
P_CU = 22.75           # grid-independent, J=5.21
PF_POINT = 0.578       # D-017, at 26.0 deg
S_MEAN_GEO = 0.959     # kVA, Faraday route
S_MAX_GEO = 0.997
S_MAX_TQ = 1.042


def p_in(t: float) -> float:
    return t * W_M + P_CU


def test_cycle_pf_is_not_the_point_value():
    pf_cycle = p_in(T_MEAN) / (S_MAX_GEO * 1e3)
    assert 0.39 < pf_cycle < 0.43, pf_cycle
    # the point value is optimistic by more than a third
    assert PF_POINT / pf_cycle > 1.35
    # and the gap is the peak/mean torque ratio, not a modelling artefact
    assert math.isclose(pf_cycle, PF_POINT * T_MEAN / T_PEAK, rel_tol=0.12)


def test_apparent_power_is_nearly_angle_invariant():
    # the rail number survives; the real power it buys does not
    assert (S_MAX_GEO - S_MEAN_GEO) / S_MEAN_GEO < 0.05
    assert S_MAX_TQ / S_MAX_GEO < 1.05


def test_ceiling_bracket():
    # V-hat at k=1 for the Faraday route, doubled to the k=2 winding
    v_k2 = 2 * 6.42
    ceiling = RPM * (48 / math.sqrt(3) * 0.95) / v_k2
    assert 5_700 < ceiling < 6_300, ceiling
    assert ceiling < 6_840, "the retired 11.5 V figure must not come back"
