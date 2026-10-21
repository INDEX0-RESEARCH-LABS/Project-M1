"""Rajini envelope anchor: winding-table + mesh-area tests (no FEM)."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "simulation" / "scripts"))
from fem_magnetics import load_bh_curve  # noqa: E402
from rajini_anchor import (AIRGAP, BARRIER_SPAN, BORE, L_STACK, SHAFT_OD,
                           STATOR_OD, T_TARGET, V_STATOR, d_pattern,
                           slot_phase36, tri_areas)
from synrm_geometry import SynRMGeometry  # noqa: E402
from synrm_mesh import build_mesh, expected_areas  # noqa: E402


def g_rajini(**kw):
    base = dict(stator_od=STATOR_OD, stator_bore=BORE, n_slots=36,
                airgap=AIRGAP, shaft_od=SHAFT_OD,
                barrier_radial_span=BARRIER_SPAN)
    base.update(kw)
    return SynRMGeometry(**base)


def sanity(g) -> bool:
    from synrm_geometry import sanity_checks
    return sanity_checks(g)["all_pass"]


# ---- declared vs derived constants (mirrors the script's derivation) ----
def test_bore_derivation():
    expect = math.sqrt(STATOR_OD**2 - 4 * V_STATOR / (math.pi * L_STACK))
    assert BORE == pytest.approx(expect)
    assert BORE == pytest.approx(0.09210, abs=2e-4)   # 92.10 mm, Table 4 derived


def test_geometry_sanity():
    assert sanity(g_rajini())


# ---- winding table: 36/4/3, q=3 belts of 3, A-belt centred at 0 deg ----
def test_belt_structure():
    belts = {k: slot_phase36(k) for k in range(36)}
    # A+ belts: {35, 0, 1} and its pole-pair repeat {17, 18, 19}
    a_plus = sorted(k for k, (ph, s) in belts.items() if ph == "A" and s > 0)
    assert a_plus == [0, 1, 17, 18, 19, 35]
    # every phase: 3 slots positive + 3 negative per pole pair = 12 of 36
    for ph in "ABC":
        n_pos = sum(1 for ph2, s in belts.values() if ph == ph2 and s > 0)
        n_neg = sum(1 for ph2, s in belts.values() if ph == ph2 and s < 0)
        assert n_pos == 6 and n_neg == 6


def test_pattern_balanced():
    pat = d_pattern()
    assert len(pat) == 36
    assert sum(pat.values()) == pytest.approx(0.0)   # zero net MMF DC


def test_pattern_continuity():
    """MMF pattern constant within a belt (q=3): belt {35, 0, 1} is A+."""
    pat = d_pattern()
    assert pat[35] == pat[0] == pat[1] == 1.0
    assert pat[2] != pat[1]          # belt boundary at slot 2 (C')


def test_full_pitch_pairing():
    """A- belt slots are +pole-pitch (9 slots) from A+ slots (full pitch)."""
    belts = {k: slot_phase36(k) for k in range(36)}
    for k in (35, 0, 1):
        assert belts[(k + 9) % 36] == ("A", -1)


def test_winding_axis_at_plus_45_deg():
    """Winding (MMF-lobe) axis = +45 deg mech, NOT 0 deg.

    Standard coil-axis rule: axis midway between full-pitch coil side groups.
    A+ {35,0,1} centred 0 deg vs A- {8,9,10} centred 90 deg -> axis +45 deg.
    Equivalent phasor check: slot pattern even about 0 deg => its harmonic-2
    phasor C2 is real (arg 0), so the integrated MMF wave ~ sin(2θ) with the
    positive lobe at +45 deg. Pins the delta-frame convention documented in
    rajini_anchor.py (delta=0 q-aligned, delta=45 d-aligned).
    """
    N, PITCH = 36, math.radians(10.0)
    p = np.array([d_pattern()[k] for k in range(N)])
    th = np.array([k * PITCH for k in range(N)])

    # C2 real and positive (even slot pattern)
    c2 = complex(np.sum(p * np.exp(-2j * th)))
    assert abs(c2) == pytest.approx(17.2763, abs=1e-3)
    assert np.angle(c2) == pytest.approx(0.0, abs=1e-9)

    # MMF staircase (current sheet integral, DC removed): lobe interval
    # centred at +45 deg. Full pitch (18 slots) => F(θ+180°)=F(θ).
    f_mid = np.cumsum(p) - np.cumsum(p).mean()
    assert int(np.argmax(f_mid)) == 4       # interval (40°,50°), centre 45°
    assert f_mid.min() == pytest.approx(-3.0, abs=1e-9)  # half-wave symmetric


# ---- mesh areas at anchor dims (the R1 gate, mini level) ----
def test_region_areas_rajini():
    g = g_rajini()
    mesh, sub, _ = build_mesh(g, n_theta=768, n_gap_rows=2)
    exp = expected_areas(g)
    worst = max(abs(tri_areas(mesh)[sub[n]].sum() / e - 1.0)
                for n, e in exp.items())
    assert worst < 0.01, f"region area error {worst:.3%}"


def test_matlib_bracket_curves_parse():
    for name in ("M-43 Steel", "1006 Steel"):
        H, B = load_bh_curve(name)
        assert np.interp(2.1, B, H) > 0          # bracket brackets 2.1 T
    # matlib block "M-47 Steel" mis-parses (multiline table) -- not used, and
    # load_bh_curve must stay away from it in the anchor (documented here).
    with pytest.raises(Exception):
        load_bh_curve("M-47 Steel")
