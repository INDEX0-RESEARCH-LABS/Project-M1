"""Rotor lamination drawing (D-010 baseline) via cadgen eng_drawing.

Run: uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.26 \
    python prototype/drawings/rotor_lam_drawing.py
All dimensions/facts come from lam_models (which reads synrm_geometry + the
committed anchor sources) -- nothing is retyped here.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import cadgen  # noqa: F401
from cadgen.eng_drawing import Sheet, eng_drawing
from lam_models import rotor_lam, FACTS, THK, g


@eng_drawing(out="rotor_lamination_drawing.pdf")
def rotor_lamination_drawing():
    part = rotor_lam()
    sheet = Sheet("A3", scale=1.4, title="ROTOR LAMINATION" + FACTS["TITLE_SUFFIX"],
                  material=FACTS["MATERIAL"], revision="0", author="Project M1",
                  units="mm", projection="THIRD ANGLE",
                  notes=[f"LAMINATION THICKNESS NOMINAL {THK:.1f} mm - "
                         "PENDING PURCHASE SPEC",
                         "GEOMETRY: COMMITTED D-010 BASELINE. "
                         "ALL NON-DIMENSIONED VALUES FROM MODEL.",
                         "BARRIERS CENTRED ON Q-AXIS (LAMINATION TOPOLOGY). "
                         "FEM ROTOR POSITIONS ARE SOLVE STATES, NOT "
                         "LAMINATION FEATURES."])

    plan = sheet.view(part, "top", at=(175, 148), label="PLAN (CROSS-SECTION)")
    iso = sheet.view(part, "iso", at=(352, 232), scale=0.30,
                     label="ISOMETRIC (NOT TO SCALE)")

    plan.diameter((0, 0, 0), FACTS["R_RO_MM"], angle=135)
    plan.hole((0, 0, 0), FACTS["SHAFT_OD_MM"], thru=True, angle=315)
    # barrier radial span on the k=0 stack (centre 90 deg here): outer surface of
    # barrier 0 zone_out, inner face of barrier 1 zone_in (points on the stacks)
    z_out, z_in = FACTS["ZONE_OUT_MM"], FACTS["ZONE_IN_MM"]
    plan.dim((0, z_in, 0), (0, z_out, 0), offset=-38, text="RADIAL SPAN <>")

    # bridge, arc fraction, barrier count as leader notes (model points)
    y0 = FACTS["ZONE_OUT_MM"] + FACTS["BRIDGE_MM"] / 2  # mid of bridging iron ring
    plan.note(f"BRIDGE {FACTS['BRIDGE_MM']:.1f} THK", (z_out - 0.0, 0, 0),
              offset=(20.0, 20.0))
    arc_end = FACTS["R_RO_MM"] - FACTS["BRIDGE_MM"]  # outer arc of barrier 0
    plan.note(f"BARRIER ARC {FACTS['ARC_FRAC']:.2f} x POLE PITCH",
              (arc_end, 0, 0), offset=(28.0, 34.0))
    plan.note(f"FLUX BARRIERS {FACTS['N_BARRIERS']}/POLE x {FACTS['N_POLES']}",
              (0, (z_out + z_in) / 2, 0), offset=(-30.0, -14.0))
    return sheet


if __name__ == "__main__":
    rotor_lamination_drawing()
