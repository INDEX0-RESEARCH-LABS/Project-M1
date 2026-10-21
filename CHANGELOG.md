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

### Added
- **2026-10-21 (freeze)** — `reports/PHASE0_SUMMARY.md`: Phase 0 simulation &
  validation frozen. Full deliverable chain (Gates A–C) with per-claim labels,
  standing honesty rules, and the founder decision point (paper freeze vs
  budget-gated build).
- **2026-10-21 (D-012 addendum 6)** - **two unit errors found and fixed by the energy
  balance** (`P_elec = P_cu + T*w_mech` would not close): `dq_model.py` used the electrical
  instead of mechanical angular speed (P_mech 2x high) and `thermal_first_order.py` used
  the FEM **peak** slot current density as RMS (P_cu 2x high). Independent arithmetic audit
  of 14 identities passes (<=0.1%). **PF is published at 0.55**: model-independent value
  from measured flux linkage + Maxwell torque, **~1.0 kVA at 1.6 N.m / 1.25 kVA at 2.0 N.m**,
  Vhat 6.5-7.3 V vs 26.3 V ceiling. **Thermal corrected to ~53 W / ~20 K at the target**
  (68 W / 26 K at J=6; still air 75 W / 55 K), **~90% copper-only** - efficiency is no
  longer the gap; PF and the ~100 A design-winding current are. L-based PF (0.49-0.50) kept
  as a diagnostic bracket only.
- **2026-10-21 (D-012 addendum 5)** - **dq model attempt**: torque **corroborated** by an
  independent co-energy derivative (36.08 vs 40.12 N.m/m, -10%), but the two-parameter
  `1.5p(Ld-Lq)id iq` model is **falsified** (0.643 vs 2.022 N.m, -68% despite converged
  Ld/Lq). **PF withdrawn** (no admissible number); survivors are the ~100 A phase current
  and the ~6-8 V vs 26.3 V voltage headroom -> the winding is under-turned ~3x (rewind ~35 A
  at identical copper loss). **Correction:** torque scales as J^2, so 1.6 N.m is at
  J=5.34 -> ~119 W, ~45 K, ~81% (not 97 W / 37 K / 84%). *The thermal half of this entry is
  superseded by addendum 6 (peak-vs-RMS); the J=5.34 correction stands.*
- **2026-10-21 (D-012 addendum 4)** — **envelope point design + thermal/bridge checks**
  (`simulation/validation/envelope_point_design/`): 130 mm bore / 50 mm stack gives
  **2.00 N.m at J=6 (1.25x margin)**, 120/74 gives 1.99 N.m (174 mm OD); certification
  drift +2.9/+3.0%. At the exact 1.6 N.m target (J~4.8): ~97 W copper, ~37 K rise enclosed,
  ~84% copper-only efficiency. **PF ~0.25 / ~4 kVA inverter / ~87 A phase** is the real
  product gap. **Bridge thickness falsified as a lever** (0.3-1.0 mm flat within 2%).
- **2026-10-21 (D-012 addendum 3)** — **150 mm-bore 4-pole envelope FEM validation**
  (`simulation/validation/envelope_validation/`, `simulation/scripts/envelope_validation.py`,
  `envelope_certify.py`): 68.49 N.m/m at rows40 = **5.07 N.m @ 74 mm** (1006 bound 4.90),
  ~3x the 1.6 N.m target, bracket spread 3%. Recorded limitations: non-monotone rows
  sequence (INDICATIVE, not certified) and local Bmax ~3 T beyond the BH bracket. 2-pole
  topology no longer required; frame is over-sized, next = point design at 110-130 mm bore.
- **2026-10-21 (D-012 addendum 2)** — **torque-density audit** (`simulation/validation/torque_density_audit/`,
  `simulation/scripts/torque_density_audit.py`): one certified-point solve + MMF/gap-field
  spectra + textbook sizing. Dominant MMF harmonic = p=2 (excitation convention confirmed);
  A1 = 9.70 kA/m, Bhat = 0.269 T, T_fem/T_sizing = **0.433** (normal SynRM utilization, no
  solver defect). The earlier "~4x density gap" is re-scoped to a current-density/thermal
  gap. Sizing scan corrected for parallel paths: **24/36 windable**, **1/36 meets both torque
  targets** (2-pole 130/74 mm, 1.84 N.m cont, ESTIMATE). Envelope direction: 130 mm-class
  2-pole (or 4-pole ~150 mm), 2-4 parallel paths; next = 2-pole geometry + certified chain
  and a copper-loss/thermal gate.
- **2026-10-21 (D-012 addendum)** — **envelope sizing scan** (`simulation/scripts/envelope_sizing.py`,
  `prototype/design/envelope_redesign_proposal.md`): 36 candidates at 3000 rpm/48 V/6 A/mm²
  against the certified density — **1/36 windable** (2-pole 90/30 mm, 6.1 turns/coil, 21 A,
  but 0.26/1.03 N·m), **0/36 meet torque targets**. Windability and certified torque have no
  intersection at 48 V/3000 rpm: blocker is the ~4× torque-density gap (0.64 vs ~2.5 kPa),
  not frame size. D-012 addendum: no envelope freeze; density workstream proposed (zero budget).
- **2026-10-21 (same day, after freeze)** — **extractor-convergence study**
  (`validation/extractor_convergence/`, PLAN with frozen rules + amendment 1 before
  run): gap-rows sweep 4→10→20→40 at 3072 rays. **single-ring certified
  mesh-converged** (−2.2% total, monotone → 8.34 N·m/m baseline absolute);
  **multi9-ring uncertifiable** on the SynRM's saturated gap (12.15→6.10, −46% swing).
  Reframes Gate C's C4 mystery as a certification asymmetry; certified SRM/SynRM
  ratio = single-consistent **0.44** (multi 0.33 downgraded); SRM's multi-ring usage
  remains valid (smooth gap, +0.6% agreement). §Result: RESULT.md incl. cost record
  (71–258 s/solve, up to 803k elements). Phase 0 summary unchanged except labels now
  certification-based rather than spread-based.
- **2026-10-21 (Gate-D prep)** — first zero-spend Gate-D deliverable: **rotor
  mechanical check** (`prototype/rotor_stress/`, PLAN frozen before run + script
  `rotor_stress_check.py`): continuous surface-ring hoop + spoke models with Kt band
  1.5–3, σ_y=230 MPa conservative. **PASS**: SF≥2 to ~15,000 rpm (5× the declared
  peak envelope; ≥12× headroom at 6000 rpm); bridge-thickness-independent margins →
  winner-family 0.4 mm bridge carries no mechanical penalty; airgap closure
  negligible (~9 µm @15k). Out-of-scope flags recorded (corner radii → spin test
  stays a Gate E acceptance item; SRM open-slot fins out of scope with D-008).
- **2026-10-21 (Gate-D prep)** — **winding spec v0** (`prototype/design/winding_spec_v0.md`):
  36/4/3 topology table final (q=3, double layer, full pitch, k_w≈0.95); ψ₁–turns–EMF
  budget computed against the 48 V window. **Finds the envelope/spec mismatch**: at
  3000 rpm the frame demands 1–2 turn bar coils ~200 A/coil (impractical), hub-direct
  is windable but 13–20× torque-starved, geared paths stay bar-coil territory. The scalars are
  geometry-only (ψ₁ ∝ R²) — mismatch is structural, not winding skill.
  **D-012 PROPOSED for founder: envelope redesign (recommended) vs target-spec revision.**
  Envelope-independent pieces (belt table, formulas, AT↔torque ledger) recorded.

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
- **Gate C RESULT** (`validation/gate_c_search/RESULT.md`): C1–C3 pass; C4/C5 fail
  honestly — winner 20/0.70/0.4 mm improves the baseline only +8.5% (single-consistent)
  / +1.2% (multi-consistent) vs the declared +10% gate, while the two Maxwell torque
  extractors disagree by ±25–30% on the SAME solution at deep saturation. Barrier family
  declared exhausted (~9.2–9.5 N·m/m @1536 single); no winner declared, D-010 baseline
  stands (D-011). Same-day follow-ups: co-energy arbiter implemented and aborted
  (~60× re-mesh drift floor); gap-rows 4→10 probe narrows spread to 16–22%, not
  converged; **standardized same-extractor ratio rule adopted** for all quotable numbers.
- **SRM/SynRM C1 re-evaluated under consistent extraction**: ratio 0.44 (single) /
  0.33 (multi) — SRM is extractor-robust (+0.6% spread, smooth gap field), the +36%
  ambiguity lives entirely on the SynRM side; original 0.43 sat inside the honest
  range by coincidence and the ±25% band stands with consistent support; win margin
  tightens to 2.3×–3.0×. Also fixed `gate_c_search` late KeyError (refine rows missing
  `area_err`) and recorded search log as artifact.

### Fixed
- **barrier wrap bug** — `_in_barrier` used unwrapped angular distance: every barrier
  arc crossing the 45° period seam was shaved/shifted (δ=0 bit-identical regression
  proof; δ=30/+6.8%, δ=45/−13.6% corrected). `expected_areas` barrier factor and
  `split_slots(n_slots)` generalized.
- **torque extractor** — multi-ring averaging added (`n_rings`, absolute `r_spread`
  clamped inside the gap annulus); single-ring regression bit-identical.
- **D-009** — zero-budget decision: M-43/1006 bracket permanent, anchor labels
  INDICATIVE ±25% final for Phase 0; D-004 ≤5% replication formally cancelled.
