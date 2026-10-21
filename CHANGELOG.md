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

## [2026-10-21]

### Added
- **SRM machinery** — `srm_model.py`: 12/8 switched-reluctance model reusing the SynRM
  toolchain (equal-Cu slot solver, N-S-N-S phase pattern, multi-ring torque extractor
  with `n_rings`/`r_spread` averaging).
- **SRM vs SynRM envelope comparison** (`validation/srm_synrm_compare/`, gates G1–G4 all
  pass): SRM peak = 3.467 N·m/m = 0.43× the SynRM's 8.124 N·m/m MTPA (±25% indicative
  band) → D-008: no architecture flip, SynRM baseline stands.
- **Anchor corrected re-run** — wrap-bug fix re-run: MTPA 8.1235 N·m/m (+5.6%), δ=0≡90
  exact period check, R5 gate retired as a formulation error (documented).
- **Rotor-upgrade family sweep** (`validation/anchor_rotor_upgrade/`, U1–U3 pass): the
  declared barrier family ceilings at 8.53 N·m/m (3072 rays); anchor target needs ×12.7
  excitation (76 A/mm²). Baseline upgraded to span 12 mm / 2 barriers/pole (D-010).
- **Gate C declared search** (`validation/gate_c_search/PLAN.md`): 12 configs over the
  v1 baseline neighborhood, frozen C1–C5 gates, run started.

### Fixed
- **barrier wrap bug** — `_in_barrier` used unwrapped angular distance: every barrier
  arc crossing the 45° period seam was shaved/shifted (δ=0 bit-identical regression
  proof; δ=30/+6.8%, δ=45/−13.6% corrected). `expected_areas` barrier factor and
  `split_slots(n_slots)` generalized.
- **torque extractor** — multi-ring averaging added (`n_rings`, absolute `r_spread`
  clamped inside the gap annulus); single-ring regression bit-identical.
- **D-009** — zero-budget decision: M-43/1006 bracket permanent, anchor labels
  INDICATIVE ±25% final for Phase 0; D-004 ≤5% replication formally cancelled.
