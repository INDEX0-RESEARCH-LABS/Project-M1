"""Pins the torque-extractor correction arithmetic (addendum 10).

Numbers come from validation/torque_extractor/RESULT.md; this file only makes
sure the derived consequences cannot drift silently. No field solves here.
"""
from __future__ import annotations

import math

T_CERT = 1.592          # single-circle, 1536 rays (the old headline)
T_ADOPT = 1.445         # midpoint of the two arbitration routes (RESULT s.3)
T_BAND = (1.40, 1.51)
J_REF = 5.34
J_6 = 6.0
P_CU_REF = 25.6         # thermal route at J_REF (STATUS.md)
P_FE = 13.5             # median iron loss
P_SHAFT = 500.0
V_K2 = 12.88            # V peak at 3000 rpm, k=2
I_K2 = 51.05
ETA = 0.90              # lambda_par ~ i^0.90


def test_correction_size():
    drop = T_ADOPT / T_CERT - 1
    assert -0.12 < drop < -0.07, f"correction moved: {drop:+.1%}"
    assert T_BAND[0] < T_ADOPT < T_BAND[1]


def test_current_for_target():
    # T ~ J^2 (measured exponent 1.9-2.0 on the three certified levels)
    for t in (T_BAND[0], T_ADOPT, T_BAND[1]):
        j = J_REF * math.sqrt(1.6 / t)
        assert 5.45 < j < 5.75, j
    j = J_REF * math.sqrt(1.6 / T_ADOPT)
    p_cu = P_CU_REF * (j / J_REF) ** 2
    assert 27.0 < p_cu < 29.5, p_cu
    eta = P_SHAFT / (P_SHAFT + p_cu + P_FE)
    assert 0.915 < eta < 0.93, eta
    # flux, terminal voltage and speed ceiling at the corrected current
    vhat = V_K2 * (j / J_REF) ** ETA
    assert 13.2 < vhat < 13.8, vhat
    n_max = 3000.0 * 26.33 / vhat
    assert 5600 < n_max < 6000, n_max
    # apparent power rises because both V and I rise at constant shaft power
    i = I_K2 * (j / J_REF)
    s = 1.5 * vhat * i
    pf = (P_SHAFT + p_cu) / s
    assert 0.47 < pf < 0.52, pf
    assert 1050 < s < 1120, s


def test_current_held_option():
    # hold the current and accept less torque: PF unchanged, power down ~9%
    p_shaft = P_SHAFT * (T_ADOPT / T_CERT)
    eta = p_shaft / (p_shaft + P_CU_REF + P_FE)
    assert 0.91 < eta < 0.93
    assert 440 < p_shaft < 465


def test_margin_at_j6():
    t6 = 1.920             # ring-averaged, 3072/rows10 (RESULT s.3)
    assert t6 / 1.6 - 1 < 0.25, "the 25% margin claim must not be restated"
    assert t6 / 1.6 - 1 > 0.15
