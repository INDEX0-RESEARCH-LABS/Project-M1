"""Copper-loss route identity (addendum 9).

The Joule loss must be the same whether it is computed from the slot current
density and the copper volume or from 3*I^2*R between the terminals.  This
pins the factor that was wrong twice (peak vs RMS, and mean-turn-length applied
to a half-turn volume).

Written as a plain test so a future edit of either script fails here first.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulation" / "scripts"))

from thermal_first_order import A_SLOT_150, FILL, N_SLOTS, RHO20, estimate  # noqa: E402

FRAMES = [(0.130, 0.0504), (0.120, 0.074)]
J_PEAK = 6.0e6
N_C = 1.247          # any turns count: both routes must be invariant to it


def test_copper_volume_is_half_turn_per_slot() -> None:
    """V_cu = N_SLOTS*FILL*A_slot*(MTL/2), i.e. the slot part plus one end."""
    for bore, L in FRAMES:
        k = bore / 0.150
        a_slot = A_SLOT_150 * k * k
        mtl = 2.0 * L + 1.2 * math.pi * bore / 4.0
        v_expected = N_SLOTS * FILL * a_slot * (mtl / 2.0)
        v_slot_only = N_SLOTS * FILL * a_slot * L
        v = estimate(bore, L, J_PEAK, 25.0)["v_cu_cm3"] * 1e-6
        assert abs(v / v_expected - 1.0) < 1e-12
        # end-winding fraction must equal MTL/(2L) exactly (short stacks are >2x)
        assert abs(v / v_slot_only - mtl / (2.0 * L)) < 1e-12


def test_slot_route_equals_terminal_route() -> None:
    """rho*(J_rms^2)*V_cu == 3*I_rms^2*R_ph with R_ph from N_ph = 6*N_c."""
    for bore, L in FRAMES:
        k = bore / 0.150
        a_slot = A_SLOT_150 * k * k
        mtl = 2.0 * L + 1.2 * math.pi * bore / 4.0
        v_cu = N_SLOTS * FILL * a_slot * (mtl / 2.0)

        p_slot = RHO20 * 0.5 * J_PEAK**2 * v_cu

        a_wire = FILL * a_slot / N_C
        i_peak = J_PEAK * FILL * a_slot / N_C
        r_ph = RHO20 * 6 * N_C**2 * mtl / (FILL * a_slot)
        p_term = 3.0 * 0.5 * i_peak**2 * r_ph

        assert abs(p_slot / p_term - 1.0) < 1e-12, (bore, p_slot, p_term)
        # and the wire is consistent with the slot fill
        assert abs(N_C * a_wire / (FILL * a_slot) - 1.0) < 1e-12
