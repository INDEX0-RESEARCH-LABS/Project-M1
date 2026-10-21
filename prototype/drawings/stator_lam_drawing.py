"""Stator lamination drawing (committed anchor envelope) via cadgen eng_drawing.

Run: uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.26 \
    python prototype/drawings/stator_lam_drawing.py
All dimensions/facts come from lam_models (which reads synrm_geometry + the
committed anchor sources) -- nothing is retyped here.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import cadgen  # noqa: F401
from cadgen.eng_drawing import Sheet, eng_drawing
from lam_models import stator_lam, FACTS, THK


@eng_drawing(out="stator_lamination_drawing.pdf")
def stator_lamination_drawing():
    part = stator_lam()
    sheet = Sheet("A3", scale=1.4, title="STATOR LAMINATION" + FACTS["TITLE_SUFFIX"],
                  material=FACTS["MATERIAL"], revision="0", author="Project M1",
                  units="mm", projection="THIRD ANGLE",
                  notes=[f"LAMINATION THICKNESS NOMINAL {THK:.1f} mm - "
                         "PENDING PURCHASE SPEC",
                         "GEOMETRY: COMMITTED ANCHOR ENVELOPE. "
                         "ALL NON-DIMENSIONED VALUES FROM MODEL.",
                         f"{FACTS['N_SLOTS']} SEMI-CLOSED SLOTS, "
                         "DOUBLE-LAYER WINDING (SEE WINDING SPEC v0)."])

    plan = sheet.view(part, "top", at=(175, 148), label="PLAN (CROSS-SECTION)")
    iso = sheet.view(part, "iso", at=(352, 232), scale=0.30,
                     label="ISOMETRIC (NOT TO SCALE)")

    plan.diameter((0, 0, 0), FACTS["R_OUT_MM"], angle=45)
    plan.hole((0, 0, 0), FACTS["BORE_MM"], thru=True, angle=225)
    # slot depth: slot bottom at 0.18*bore radius from the bore surface on +y
    r_bore = FACTS["R_BORE_MM"]
    r_slot_tip = r_bore + r_bore * 0.18
    plan.dim((0, r_bore, 0), (0, r_slot_tip, 0), offset=42, text="SLOT DEPTH <>")

    # slot opening + count as leader notes (model points)
    plan.note(f"SLOT OPENING {FACTS['SLOT_OPENING_MM']:.2f}", (r_bore * 0.72, r_bore * 0.69, 0),
              offset=(30.0, 24.0))
    plan.note(f"SLOTS {FACTS['N_SLOTS']} x 10 DEG PITCH", (0, FACTS["R_OUT_MM"], 0),
              offset=(-34.0, 14.0))
    return sheet


if __name__ == "__main__":
    stator_lamination_drawing()
