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


def test_kva_per_nm_is_design_invariant():
    """D-023: S/T = (omega + P_cu/T)/PF. Length and bore do not enter."""
    t0, pcu0, pf0 = 1.2305, 22.75, 0.427
    s_per_nm = (W_M + pcu0 / t0) / pf0
    assert abs(s_per_nm * t0 - 959.0) / 959.0 < 0.005, "must reproduce the swept 0.959 kVA"

    # stack route: torque and flux both scale with L, so S scales with L too
    s_at_target = s_per_nm * 1.6
    assert 1.20 < s_at_target / 1e3 < 1.30, s_at_target
    # and both routes land in the same band, not at 1.06 vs 1.38
    pcu_current = pcu0 * (1.6 / t0) ** 2
    s_current = (W_M + pcu_current / 1.6) / pf0 * 1.6
    assert abs(s_current - s_at_target) / s_at_target < 0.05
    assert s_at_target / 1e3 > 1.20, "1.06 kVA at 1.6 N.m must not come back"


def test_angle_study_ranking():
    """D-024: 26 deg is MTPA, and the VA-optimal angle costs current.

    Reads the committed sweep CSVs, so it is a guard on the data, not a re-run.
    """
    import csv
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "simulation/validation/angle_kva"

    def load(angle):
        rows = list(csv.DictReader(open(root / f"sweep_{angle}deg.csv")))
        t = sum(float(r["T"]) for r in rows) / len(rows)
        s = sum(float(r["S_geo"]) for r in rows) / len(rows)
        return t, s

    t20, s20 = load(20)
    t26, s26 = load(26)
    t32, s32 = load(32)
    # 26 is the mean-torque optimum inside the sampled span
    assert t26 > t20 > t32
    # apparent power rises with the angle, so the VA benefit lives below 20
    assert s20 < s26 < s32
    # ... but it is bought with current: S per N.m is what improves, not S per amp
    assert s20 / t20 < s26 / t26
