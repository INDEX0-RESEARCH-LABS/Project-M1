"""Tests for the SynRM baseline geometry (Gate B)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulation" / "scripts"))

from synrm_geometry import SynRMGeometry, rotor_barriers, sanity_checks, stator_profile


def test_sanity_checks_pass_for_default():
    checks = sanity_checks(SynRMGeometry())
    assert checks["all_pass"], checks


def test_rotor_od_derived_from_bore_and_airgap():
    g = SynRMGeometry()
    assert math.isclose(g.rotor_od, g.stator_bore - 2 * g.airgap)


def test_barrier_count_and_symmetry():
    g = SynRMGeometry()
    polys = rotor_barriers(g)
    assert len(polys) == 4 * g.n_barriers
    # every pole uses exactly n_barriers layers
    for pole in range(4):
        layers = sorted(p["layer"] for p in polys if p["pole"] == pole)
        assert layers == list(range(g.n_barriers))


def test_barriers_inside_rotor_and_outside_shaft():
    g = SynRMGeometry()
    r_ro = g.rotor_od / 2
    for p in rotor_barriers(g):
        assert p["r_outer"] < r_ro, "barrier breaks rotor surface"
        assert p["r_inner"] > g.shaft_od / 2, "barrier reaches shaft"
        for x, y in p["points"]:
            assert math.hypot(x, y) <= r_ro + 1e-9
            assert math.hypot(x, y) >= p["r_inner"] - 1e-6


def test_barrier_radial_ordering_no_overlap():
    g = SynRMGeometry()
    polys = rotor_barriers(g)
    for pole in range(4):
        layers = sorted([p for p in polys if p["pole"] == pole], key=lambda p: p["layer"])
        for a, b in zip(layers, layers[1:]):
            assert b["r_outer"] <= a["r_inner"] + 1e-9, "adjacent barriers overlap radially"


def test_stator_profile_closed_and_finite():
    g = SynRMGeometry()
    prof = stator_profile(g)
    assert len(prof["outer"]) >= 256
    assert len(prof["inner"]) == g.n_slots * 20  # 9+1+9+1 points per slot pitch
    for ring in prof.values():
        for x, y in ring:
            assert math.isfinite(x) and math.isfinite(y)


def test_slots_extend_outward_from_bore():
    """Regression: slot bottoms must lie OUTWARD of the bore.

    An earlier version defined slot bottoms at r_bore - depth, i.e. slots poking
    inward into the airgap and rotor; the mesh classifier inherited that and
    swallowed the whole airgap band. This test fails for that convention.
    """
    g = SynRMGeometry()
    r_bore = g.stator_bore / 2
    for x, y in stator_profile(g)["inner"]:
        assert math.hypot(x, y) >= r_bore - 1e-9


def test_barriers_disjoint_from_slot_band():
    g = SynRMGeometry()
    r_bore = g.stator_bore / 2
    depth = 0.18 * r_bore
    for p in rotor_barriers(g):
        assert p["r_inner"] > r_bore or p["r_inner"] < g.stator_bore - depth


if __name__ == "__main__":
    raise SystemExit("run with: .venv/bin/python -m pytest tests/ -q")
