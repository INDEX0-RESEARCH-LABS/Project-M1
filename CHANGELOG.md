# Changelog

All notable changes to Project M1 deliverables. Format: Keep a Changelog-ish, dated.

## [Unreleased]

### Added
- **2026-10-20** — Phase Zero: workspace created, git initialized, Python venv with
  numpy 2.5.4 / scipy 1.18.1 / pandas 3.0.6 / matplotlib 3.11.2 / pytest 9.1.1.
- Charter, roadmap, decision log, ground rules, toolchain record.
- **2026-10-20** — Phase One (Gate A) research: 72 verified literature sources
  (`research/literature_review.md`, `research/research_matrix.csv`,
  `research/bibliography.bib`), 18-document preliminary patent survey
  (`research/prior_art.md`), research gaps + three falsifiable hypotheses
  H1–H3 (`research/research_gaps.md`).
- **2026-10-20** — Gate B solver: linear A-z solver validated (straight-wire, ≤0.33% error);
  nonlinear Picard-on-ν solver validated (saturated toroid, Ampère error 0.49%/0.18%).
- **2026-10-20** — Steel provenance: anchor grades 35A300 / M1000-65A confirmed from full
  texts (`research/material_grades.md`); manufacturer catalogs checked directly — none
  publish B-H curves; MagWeb SMAG identified as the paid source (founder decision pending).
- **2026-10-20** — Full SynRM mesh: `synrm_mesh.py` (polar grid, region-by-construction
  assignment) with area-agreement tests; all 7 regions within 0.3% of closed-form areas.

### Fixed
- **2026-10-20** — geometry: `synrm_geometry.stator_profile` defined slot bottoms at
  `r_bore - depth` (slots pointing inward, swallowing the airgap) instead of
  `r_bore + depth`. Baseline JSON regenerated; regression tests added.
- **2026-10-20** — geometry: `rotor_barriers` centered barrier sets on the pole axes
  (blocking d-flux: an inverted reluctance rotor) instead of the q-axes; the mesh
  classifier already used the correct q-centering. Cross-module regression test
  added comparing polygon angular midpoints with the classifier.
- **2026-10-20** — solver: load assembly in `solve_az` was nested inside the materials
  loop, so per-slot current regions that replaced the single `slots` group delivered
  no current (all fields read ~0.02 T). Current loading is now independent of
  material classification; `solve_az_core` added for in-memory meshes.

### Added
- **2026-10-20** — torque extraction validation: `synrm_torque_convergence.py` shows
  Maxwell-stress torque converging under mesh refinement (2.6% between finest levels)
  with airgap radius independence ≤3%; `T ≈ 0.030 ± 0.001 N·m` at the test point
  (`simulation/validation/torque/RESULT.md`, placeholder steel). Mesh rays now align
  to slot/barrier edges and the airgap supports multiple element rows.
