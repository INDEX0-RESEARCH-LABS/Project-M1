"""build123d lamination solids + drawing facts for the M1 SynRM D-010 geometry.

Source of dimensional truth (nothing retyped here):
- 2D cross-section polygons: simulation/scripts/synrm_geometry.py (metres, origin
  at shaft centre, slot k centred at angle 0).
- Anchor constants STATOR_OD / BORE / AIRGAP / SHAFT_OD / N_SLOTS come from
  simulation/scripts/rajini_anchor.py, read from that file's AST (evaluated with
  `math` in namespace) so the values cannot drift from the committed code.
- Rotor barrier family (span 12 mm, n_barriers 2, arc frac 0.62, bridge 0.6 mm)
  = committed D-010 baseline topology: DECISIONS.md D-010 and
  gate_c_coenergy.py CONFIG (also parsed from AST). Note gate_c_extractor_ab.py
  hardcodes SynRMGeometry(..., n_barriers=2, ...) for the same baseline.
- Lamination topology note: barriers are centred on the Q-AXIS (deg=0). The FEM
  operating rotor position (delta 26.25 deg in solve configs) is a SOLVE STATE,
  not a lamination feature, and must not be baked into drawn geometry.

Solids are built in MILLIMETRES (source metres x 1000) and extruded 0.5 mm
(nominal sheet gauge, declared for drawing purposes -- see title-block note
"LAMINATION THICKNESS NOMINAL 0.5 mm - PENDING PURCHASE SPEC").

demo() is the self-check: exact boolean-area identities, centred bounding box,
and synrm_geometry.sanity_checks must all pass.
"""
from __future__ import annotations

import ast
import math
import sys
from pathlib import Path

from build123d import Circle, Polygon, extrude

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "simulation" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import synrm_geometry  # noqa: E402

MIL = 1000.0  # metres -> millimetres
THK = 0.5     # nominal lamination thickness [mm], declared above


def _module_assignments(path: Path, ns: dict) -> dict[str, object]:
    """Eval top-level plain assignments of a source file (no import needed)."""
    out: dict[str, object] = {}
    ns = {**ns, "__builtins__": {}}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            try:
                val = eval(compile(ast.Expression(node.value), "<facts>", "eval"),
                           {**ns, **out})
            except Exception:
                continue
            for t in node.targets:
                out[t.id] = val
    return out


_ANCH = _module_assignments(  # rajini_anchor.py lines 69-83
    SCRIPTS / "rajini_anchor.py", {"math": math})
_CFG = _module_assignments(  # gate_c_coenergy.py CONFIG = dict(span, frac, bridge, deg)
    SCRIPTS / "gate_c_coenergy.py", {"math": math, "dict": dict})
for _k in ("STATOR_OD", "N_SLOTS", "AIRGAP", "SHAFT_OD", "L_STACK", "V_STATOR", "BORE"):
    if _k not in _ANCH:
        raise RuntimeError(f"anchor constant {_k} not parsed from rajini_anchor.py")
for _k in ("span", "frac", "bridge"):
    if _k not in _CFG["CONFIG"]:
        raise RuntimeError(f"D-010 constant {_k} not parsed from gate_c_coenergy.py CONFIG")
_CFG = _CFG["CONFIG"]

# Committed geometry (D-010 baseline v1); lamination topology at deg=0 (q-axis)
g = synrm_geometry.SynRMGeometry(
    stator_od=_ANCH["STATOR_OD"], stator_bore=_ANCH["BORE"], n_slots=_ANCH["N_SLOTS"],
    airgap=_ANCH["AIRGAP"], shaft_od=_ANCH["SHAFT_OD"],
    barrier_radial_span=_CFG["span"], n_barriers=2,  # D-010: 2 barriers/pole
    barrier_angle_frac=_CFG["frac"], bridge=_CFG["bridge"],
    barrier_center_angle=math.pi / 4)

if not synrm_geometry.sanity_checks(g)["all_pass"]:
    raise RuntimeError("committed geometry fails synrm_geometry.sanity_checks")

# Drawing facts, all model-derived (mm text values)
FACTS = {
    "STATOR_OD_MM": g.stator_od * MIL,
    "BORE_MM": g.stator_bore * MIL,
    "ROTOR_OD_MM": g.rotor_od * MIL,
    "SHAFT_OD_MM": g.shaft_od * MIL,
    "AIRGAP_MM": g.airgap * MIL,
    "BRIDGE_MM": g.bridge * MIL,
    "SPAN_MM": g.barrier_radial_span * MIL,
    "ARC_FRAC": g.barrier_angle_frac,
    "N_BARRIERS": g.n_barriers,
    "N_POLES": g.rotor_n_poles,
    "N_SLOTS": g.n_slots,
    "SLOT_OPENING_MM": g.slot_opening * MIL,
    # synrm_geometry.py:75 -- slot body radial depth = 0.18 * bore radius
    "SLOT_DEPTH_MM": 0.18 * g.stator_bore / 2 * MIL,
    "R_BORE_MM": g.stator_bore / 2 * MIL,
    "R_OUT_MM": g.stator_od / 2 * MIL,
    "R_RO_MM": g.rotor_od / 2 * MIL,
    "ZONE_OUT_MM": (g.rotor_od / 2 - g.bridge) * MIL,
    "ZONE_IN_MM": (g.rotor_od / 2 - g.bridge - g.barrier_radial_span) * MIL,
    "TITLE_SUFFIX": " - M1 SYNRM v1 (D-010)",
    "MATERIAL": "M-43 ELECTRICAL STEEL (INDICATIVE - D-009)",
}


def _mm_poly(pts_meters):
    return Polygon(*[(x * MIL, y * MIL) for x, y in pts_meters], align=None)


def barrier_polys():
    """The 8 barrier regions (2/pole x 4 poles) as polygon lists (mm)."""
    return [p["points"] for p in synrm_geometry.rotor_barriers(g)]


def rotor_lam():
    """Disk at rotor OD, shaft bore Thru, 8 barrier polygons removed. 0.5 mm."""
    sk = Circle(FACTS["R_RO_MM"]) - Circle(FACTS["SHAFT_OD_MM"] / 2)
    for pts in barrier_polys():
        sk -= _mm_poly(pts)
    return extrude(sk, THK)


def stator_lam():
    """Disk at stator OD, bore + 36 semi-closed slot notches removed. 0.5 mm."""
    sp = synrm_geometry.stator_profile(g)
    sk = Circle(FACTS["R_OUT_MM"]) - _mm_poly(sp["inner"]) - Circle(FACTS["R_BORE_MM"])
    return extrude(sk, THK)


def demo() -> None:
    def area(poly):  # shoelace, mm^2
        return abs(sum(x1 * y2 - x2 * y1
                       for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1])) / 2)

    bpolys = barrier_polys()
    assert len(bpolys) == FACTS["N_BARRIERS"] * FACTS["N_POLES"] == 8

    rs, ss = rotor_lam(), stator_lam()
    r = max(rs.faces(), key=lambda f: f.area)  # planar cap
    expect = math.pi * (FACTS["R_RO_MM"] ** 2 - (FACTS["SHAFT_OD_MM"] / 2) ** 2)
    expect -= sum(area(p) for p in bpolys) * MIL * MIL
    assert abs(r.area - expect) / expect < 1e-4, (r.area, expect)

    s = max(ss.faces(), key=lambda f: f.area)  # planar cap
    inner = synrm_geometry.stator_profile(g)["inner"]
    rough = math.pi * FACTS["R_OUT_MM"] ** 2 - area(inner) * MIL * MIL
    assert abs(s.area - rough) / rough < 5e-3, (s.area, rough)  # arc-chord sliver eta

    for solid, lam, lo, hi in ((rs, r, -FACTS["R_RO_MM"], FACTS["R_RO_MM"]),
                               (ss, s, -FACTS["R_OUT_MM"], FACTS["R_OUT_MM"])):
        bb = lam.bounding_box()
        assert abs(bb.max.X + bb.min.X) < 1e-6 and abs(bb.max.Y + bb.min.Y) < 1e-6
        assert abs(bb.max.X - hi) < 1e-6 and abs(bb.min.X - lo) < 1e-6
        assert abs(lam.area * THK - solid.volume) / solid.volume < 1e-6

    print("demo OK")
    print(f"  rotor OD {FACTS['ROTOR_OD_MM']:.2f}  bore {FACTS['BORE_MM']:.2f}")
    print(f"  stator area {s.area:.1f} mm^2  rotor area {r.area:.1f} mm^2")


if __name__ == "__main__":
    demo()
