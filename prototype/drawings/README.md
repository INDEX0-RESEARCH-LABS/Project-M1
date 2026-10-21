# Lamination drawings (A3, cadgen/engineering-drawing)

Artifacts in this directory (all uncommitted, in working tree):
- `lam_models.py` — build123d models derived from `simulation/scripts/synrm_geometry.py` + `rajini_anchor.py` AST. **Lamination topology at δ=0 (barriers on q-axis).** FEM operating rotor position is a solve state, not a lamination feature (delta not baked into geometry).
- `rotor_lam_drawing.py` — cadgen eng_drawing for rotor lamination
- `stator_lam_drawing.py` — cadgen eng_drawing for stator lamination  
- `rotor_lamination_drawing.pdf` — A3 (1190.55×841.89 pt), generated 2026-10-21
- `stator_lamination_drawing.pdf` — A3 (1190.55×841.89 pt), generated 2026-10-21

Dimensions are model-derived (imported via `lam_models`), not retyped. Title block notes mark thickness as nominal (0.5 mm, pending purchase spec) and steel as M-43 (INDICATIVE per D-009). No invented tolerances. ASCII-only text.

What they do NOT show (per engineering-drawing skill limits): sections, details, auxiliary views. This is a cross-section plan view per lamination.
