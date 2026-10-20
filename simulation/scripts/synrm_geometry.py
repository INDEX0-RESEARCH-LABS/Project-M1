"""Parameterized 4-pole multi-barrier SynRM cross-section generator (Gate B baseline).

Purpose: produce a reproducible, parameter-driven 2D cross-section (polygons in metres)
that can be (a) previewed, (b) exported to JSON for a FEMM/Elmer script, and (c) swept
by the optimization loop later. No FEM solving happens here — this is geometry only.

Conventions:
- Origin at shaft center; +x through a rotor pole axis (q-axis along slot centerline).
- Angles in radians, CCW. All lengths in metres.
- One pole-pair quadrant is NOT assumed; full cross-section is generated.

ponytail: planar single-pole-pitch barriers, constant radial bridge — adequate for a
first baseline; upgrade to per-barrier end-angle windows (à la P13 prior art) only if
ripple results demand it.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SynRMGeometry:
    # Stator
    stator_od: float = 0.120          # outer diameter [m]
    stator_bore: float = 0.066        # bore diameter [m]
    n_slots: int = 24                 # stator slots
    slot_opening: float = 0.003       # slot opening width at bore [m]
    # Rotor / airgap
    airgap: float = 0.0007            # mechanical airgap [m]
    shaft_od: float = 0.0017 * 10     # shaft diameter [m]
    # Flux barriers (per pole)
    n_barriers: int = 3               # barriers per pole
    barrier_radial_span: float = 0.006   # total radial depth of barrier zone [m]
    barrier_gap_frac: float = 0.40    # iron rib fraction between barriers (of zone)
    barrier_center_angle: float = math.pi / 4  # pole-pitch half-angle placement center [rad]
    barrier_angle_frac: float = 0.62  # barrier angular width as fraction of pole pitch
    bridge: float = 0.0006            # thin iron bridge at rotor surface [m]

    @property
    def rotor_od(self) -> float:
        return self.stator_bore - 2.0 * self.airgap

    @property
    def pole_pitch(self) -> float:
        return math.pi / 2  # 4 poles


def _arc(r: float, a0: float, a1: float, n: int = 64):
    return [(r * math.cos(a), r * math.sin(a)) for a in
            [a0 + (a1 - a0) * i / n for i in range(n + 1)]]


def stator_profile(g: SynRMGeometry) -> dict[str, list]:
    """Stator outer circle + inner bore boundary with semi-closed slots.

    Returns polygons: 'outer' (circle), 'inner' (bore with slot notches cut inward).
    Slot geometry: tooth tip opening = slot_opening; slot body widens linearly to the
    next pitch (trapezoidal slot approximation, standard for first-pass designs).
    """
    r_out = g.stator_od / 2
    r_bore = g.stator_bore / 2
    pitch = 2 * math.pi / g.n_slots
    half_open = g.slot_opening / 2
    a_open = math.asin(min(1.0, half_open / r_bore))  # angular half-width of opening
    depth = 0.18 * r_bore  # slot body radial depth (tooth length); adjustable later

    inner = []
    for k in range(g.n_slots):
        c = k * pitch
        # tooth tip flanks from opening to slot bottom corners
        r_bot = r_bore - depth
        half_bot = pitch / 2 * 0.55  # slot occupies 55% of pitch at bottom
        inner += _arc(r_bore, c - pitch / 2, c - a_open, 8)          # tooth face left
        inner += [(r_bot * math.cos(c - half_bot), r_bot * math.sin(c - half_bot))]
        inner += _arc(r_bot, c - half_bot, c + half_bot, 8)          # slot bottom
        inner += [(r_bore * math.cos(c + a_open), r_bore * math.sin(c + a_open))]
    outer = _arc(r_out, 0, 2 * math.pi, 256)
    return {"outer": outer, "inner": inner}


def rotor_barriers(g: SynRMGeometry) -> list[dict]:
    """Flux barriers: one list of polygons per barrier, repeated on all 4 poles.

    Each barrier is an annular sector (constant radial thickness) centered on the
    pole-pitch quarter positions, with a surface bridge gap to the rotor surface.
    """
    r_ro = g.rotor_od / 2
    zone_out = r_ro - g.bridge
    zone_in = zone_out - g.barrier_radial_span
    t = g.barrier_radial_span * (1 - g.barrier_gap_frac) / g.n_barriers  # barrier thickness
    gap = g.barrier_radial_span * g.barrier_gap_frac / (g.n_barriers - 1) if g.n_barriers > 1 else 0.0

    half_span = (g.barrier_angle_frac * g.pole_pitch) / 2
    polys = []
    for k in range(4):  # 4 poles, centered on 0, pi/2, pi, 3pi/2
        center = k * math.pi / 2
        for j in range(g.n_barriers):
            r_o = zone_out - j * (t + gap)
            r_i = r_o - t
            a0, a1 = center - half_span, center + half_span
            poly = _arc(r_o, a0, a1, 48) + list(reversed(_arc(r_i, a0, a1, 48)))
            polys.append({"pole": k, "layer": j, "r_inner": r_i, "r_outer": r_o, "points": poly})
    return polys


def sanity_checks(g: SynRMGeometry) -> dict[str, bool | float]:
    """Geometric invariants — must all pass before any FEM run."""
    r_ro = g.rotor_od / 2
    zone_in = r_ro - g.bridge - g.barrier_radial_span
    checks = {
        "stator_fits_envelope": g.stator_od > g.stator_bore > g.rotor_od > g.shaft_od,
        "rotor_bore_clearance_ok": zone_in > g.shaft_od / 2 + 0.002,  # >=2 mm yoke/shaft margin
        "n_slots_even": g.n_slots % 2 == 0,
        "barrier_count_plausible": 1 <= g.n_barriers <= 6,
        "bridge_positive": g.bridge > 0,
        "airgap_positive": g.airgap > 0,
    }
    checks["all_pass"] = all(checks.values())
    return checks


def export_json(g: SynRMGeometry, path: str) -> None:
    data = {
        "parameters": asdict(g),
        "derived": {"rotor_od": g.rotor_od, "pole_pitch": g.pole_pitch},
        "stator": stator_profile(g),
        "barriers": rotor_barriers(g),
        "sanity": sanity_checks(g),
    }
    with open(path, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "simulation/configs/synrm_baseline_v0.json"
    g = SynRMGeometry()
    checks = sanity_checks(g)
    print("sanity:", checks)
    if not checks["all_pass"]:
        raise SystemExit("sanity checks failed — refusing to export")
    export_json(g, out)
    print(f"exported -> {out}")
