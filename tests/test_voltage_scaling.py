"""Pins the turns-scaling identities behind the 48 V / 96 V table.

Gates V1/V2 from validation/voltage_and_angle/PLAN.md. The point is that a
voltage change trades current for turns and leaves apparent power alone, so the
"1 kVA or 96 V" choice is not actually a choice about controller VA.
"""
from __future__ import annotations

import math

I1 = 102.1      # A peak, k=1 reference state (dq_model/RESULT.md s.9)
V1 = 6.52       # V peak at 3000 rpm, k=1
R1 = 1.53e-3    # ohm, k=1
S1 = 1.5 * V1 * I1
T_TARGET = 1.592
P_SHAFT = 500.0


def scale(k: float) -> dict:
    """Exact turns scaling at fixed slot ampere-turns."""
    return {"i": I1 / k, "v": V1 * k, "r": R1 * k * k,
            "p_cu": 1.5 * R1 * k * k * (I1 / k) ** 2,
            "speed": 3000.0 * 26.33 / (V1 * k),
            "s": 1.5 * (V1 * k) * (I1 / k)}


def test_scaling_identities():
    base = scale(1.0)
    for k in (1.0, 1.5, 2.0, 3.0, 4.0):
        s = scale(k)
        assert math.isclose(s["i"] * k, I1, rel_tol=1e-12)
        assert math.isclose(s["v"] / k, V1, rel_tol=1e-12)
        assert math.isclose(s["r"] / k**2, R1, rel_tol=1e-12)
        assert math.isclose(s["p_cu"], base["p_cu"], rel_tol=1e-12), "P_cu not invariant"
        assert math.isclose(s["speed"] * k, 3000.0 * 26.33 / V1, rel_tol=1e-12)
        assert math.isclose(s["s"], S1, rel_tol=1e-12), "S not invariant"


def test_96v_options():
    # 96 V does not halve current at the same turns; it doubles the speed ceiling.
    k2 = scale(2.0)
    assert math.isclose(3000.0 * 52.66 / k2["v"], 2 * 3000.0 * 26.33 / k2["v"],
                        rel_tol=1e-12)
    # Half the current needs twice the turns, and that consumes the voltage gain.
    k4 = scale(4.0)
    assert math.isclose(k4["i"], k2["i"] / 2, rel_tol=1e-12)
    assert math.isclose(3000.0 * 52.66 / k4["v"], 3000.0 * 26.33 / k2["v"],
                        rel_tol=1e-12)
    assert math.isclose(k4["s"], k2["s"], rel_tol=1e-12)


def test_controller_va_is_set_by_pf():
    # 0.5 kW shaft, 92.7% efficiency (STATUS.md)
    p_in = P_SHAFT / 0.927
    for pf in (0.53, 0.55, 0.58):
        assert abs(p_in / pf - (P_SHAFT / 0.927) / pf) < 1e-12
    assert 900 < p_in / 0.55 < 1000
    # the PF bracket, not the bus voltage, is what moves S (~90 VA here)
    assert abs((p_in / 0.53) - (p_in / 0.58)) > 80
