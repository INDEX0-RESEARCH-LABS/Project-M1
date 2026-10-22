# Changelog

All notable changes to Project M1 deliverables. Format: Keep a Changelog-ish, dated.

## [Unreleased]

### Added
- **2026-10-23 (D-016: re-certification done - torque and efficiency re-certified, PF open)**
  - 181-point 0.25 deg static sweep on the corrected winding (`torque_curve/sweep_0p25deg.csv`).
    Peak **1.813 N.m at 26.0 deg** (9-ring) / 1.753 at 25.5 (annulus); plateau 25.5-27.5
    within 1.5%; peak/mean 2.18 against 1.57 for an ideal `sin(4*delta)`. Gate A2 **FAILS**
    (102/181 points beyond 10% of the 5 deg interpolant).
  - The dips are **torque reversals**, not notches: `torque_at` returns `abs()`. Signed, all
    three estimators agree the torque is negative from 1.5 to 3.9 deg (lobe -0.27 N.m, 15%
    of peak), crossing zero at 3.95. Further dips at 12.5 / 22.5 / 33.0 / 41.75 deg.
  - Four mechanisms tested and **refuted**: ray-merge slivers (`RAY_MERGE_TOL` 1e-4 -> 2e-3
    changes nothing, 5e-3 goes singular; the constant is now module-level), material
    misclassification (barrier area constant to 1e-6 over 46 angles), extractor bias (the
    solid-rotor null is constant in angle), discretisation (dips stable across three meshes,
    0.251 / 0.157 / 0.196 N.m at 33 deg). Saturation is an amplifier: dip/peak 0.455 -> 0.333
    -> 0.292 as J goes 1.05 -> 2.60 -> 5.21 A/mm2.
  - **Solid-rotor null test**: a rotor with no barriers must give zero torque. Single circle
    reads **+0.55 N.m**, 9-ring -0.04, gap annulus -0.13, all constant in angle. The single
    circle was the estimator `dq_model.solve_point` used for PF and efficiency.
  - **Estimator settled by convergence**, not preference: at 26.0 deg over meshes
    1536/4, 2048/6, 3072/10, 4096/10 the annulus reads 1.739 / 1.747 / 1.778 / 1.770 N.m
    (2.2%), the single circle 9.0%, the 9-ring average 22.8% and non-monotone.
  - `solve_point` now returns `T_ann` / `T_ann_err`; `iron_loss`, `pf_check` and
    `saliency_screen` use them. `DELTA_OP` 26.25 -> 26.0 (the sweep argmax).
  - Re-certified: **torque 1.77 +- 0.14 N.m** (vs frozen 1.60), **efficiency 93.2%**
    (91.6-94.1%, unchanged), **iron 16.3 W median** (vs 12.1). **PF 0.578 / 1.06 kVA**
    (vs 0.633 / 0.90) - PF moved down and is **OPEN** pending a same-estimator baseline.
  - Ripple still NOT ESTABLISHED, but the experiment design is now corrected: this sweep is a
    *load-angle* curve because it fixes the current in the stator frame; a running machine
    holds it in the rotor frame, so ripple needs the pattern rotated with the rotor.
  `validation/torque_curve/RESULT.md`, D-016.
- **2026-10-23 (D-015: slot binning fixed, certified numbers frozen)** - Auditing the
  ripple model found that `split_slots` binned cells with `floor(theta/pitch)` while the
  geometry centres slot k at k*pitch, so every bin sat **+0.513 pitch** off its slot
  (measured geometrically). The applied MMF was rotated 5 deg mechanical and the belt
  boundaries mixed two phases into one current density. `rajini_anchor`'s own docstring
  requires T = 0 at delta = 0 and 45; as shipped those read 0.4386 and 0.4577 N.m, and
  after the one-line fix 0.0102 and 0.0296. The fix is not a relabelling: torque at the
  same label moves 1.5761 -> 1.7897 N.m, so D-014's torque, lambda, PF, S, efficiency
  and ceiling are **frozen pending re-certification**, not withdrawn. Regression test
  `test_split_slots_bins_are_centred_on_geometry_slots` (fails at 0.513 pitch).
  Also found and recorded: the torque-angle curve has dips the 5 deg grid stepped over
  (T9 < 0.05 N.m at 42.5-43.75 deg against 1.07 at 40 and 0.46 at 45, reproducible at
  3072/10), and the Maxwell extractor cannot resolve torque below ~0.5 N.m (four gap
  bands spread 10.7% at the certified point, 9x at a dip). New estimator
  `fem_magnetics.torque_annulus` (area integral over the gap, band spread as error bar)
  agrees at the certified point: 1.536 vs 1.576 N.m.
  `validation/torque_curve/RESULT.md`, D-015.
- **2026-10-22 (torque ripple: attempted, NOT established)** - Two harness generations
  for load torque ripple. Gen 1 swept the rotor with the current pattern fixed in the
  stator frame, which is the **static torque-angle curve**, not ripple; it was
  re-scoped and re-used as an independent check of the operating point. New
  `torque_ripple.py` implements the correct steady-state model (phase currents advanced
  with the rotor, current angle pinned at 26.25 deg), plus an optional `pattern=` on
  `solve_raw`. It passes the remaining consistency tests: reproduces the certified
  1.6695 N.m at alpha=0, bit-identical at delta+90 for three pairs, and fine-mesh
  stable. A fourth check - equality under 180 deg current reversal - is **void**:
  `torque_at` returns `abs()`, so sign reversal is folded out. Corrected in RESULT.md
  rather than left as a green tick. It fails adequacy anyway: torque runs 0.64-1.70
  N.m over 45 deg, while the static curve of the same geometry fits orders 4/8/12 at
  1.536/0.137/0.037 N.m with 0.044 RMS (order 12 = 2.4%). The winding harmonics were
  verified correct (5th/7th at 22.7%/18.5%, slipping at alpha/5 backward and alpha/7
  forward), so the mechanism is real but the 25x amplitude gap is unexplained.
  **No ripple number is quoted**; R2 fails, R3 not applied. Side result, quotable:
  the static curve `T = 1.536 sin(4(delta-5)) + ...` peaks at 27-30 deg and confirms
  the certified 1.60 N.m point from an independent sweep. One outlier at delta=78 is
  reproducible at 3072 rays / 10 gap rows (0.53 vs 1.48 expected) and is therefore not
  a coarse-mesh artifact: a 3 deg wide dip between two good neighbours, which points at
  angle-dependent rotor-region classification.
  `validation/torque_ripple/{PLAN,RESULT}.md`.
- **2026-10-22 (D-014 adopted)** - **Gate B and iron loss on the deep-barrier rotor both
  pass, so the candidate becomes the design of record.** New `rotor_stress_fem.py`
  (2D plane-stress, validated against the solid-disk known answer to 0.17%) gives
  SF 16.6 at 6000 rpm and 12.2 at 7000 rpm on the declared p99.5 rule, 9.5/7.3 even on
  the absolute corner peak, and 3.8 um airgap growth of 520. The pessimistic hand bound
  (~420 MPa, "bridge carries the whole rim") is refuted: the arc ribs share the load.
  `iron_loss.py --candidate`: 12.1 W median (7.5-21.2), below the baseline 13.5 W. The
  certified target point at J=5.21 is 49.7 A, PF 0.633, **S 0.86 kVA**, 93.4%,
  ~6,840 rpm, 7.37 kg iron. `STATUS.md` restated to the deep rotor; the shallow-rotor
  numbers are kept in parentheses. Open: torque ripple/NVH and punching tooling.
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
- **2026-10-21 (D-014)** - **deep-barrier rotor candidate: the barrier stack was too
  shallow.** It occupied the outer 10.4 mm of a 64.5 mm rotor radius, so q-flux dived
  under it. Sweeping depth (4 barriers, 25% ribs, 0.62 angular fraction): span 10.4 ->
  20.8 -> 31.2 -> 44.5 mm gives T 1.59 -> 1.71 -> 1.76 -> 1.80 N.m and PF 0.532 -> 0.596 ->
  0.625 -> 0.644 at the same current. Ring-averaged confirmation at 3072/10:
  **+16.2% torque (1.751 vs 1.507), PF 0.635, S 903 VA**. At the 1.6 N.m target that is
  ~0.76-0.80 kVA instead of ~1.1, i.e. the D-012 PF blocker is close to closed without
  changing voltage, winding or frame. Not adopted: Gate B stress and iron loss pending.
  New `validation/saliency_lever/`, `saliency_screen.py`; `envelope_validation.build()`
  gained keyword-only barrier parameters (certified default path unchanged).
- **2026-10-21 (D-012 addendum 10)** - **torque extractor bias found and corrected**:
  the headline 1.592 N.m was one Maxwell-stress sampling circle on a 1536-ray/4-row mesh.
  Rings (1/5/9) scatter 11% on that mesh, so the single-circle number was a high-side
  sample. Ring-averaged fine meshes give 1.44-1.51 N.m and the independent co-energy
  derivative 1.40 N.m. **Adopted 1.45 N.m, band 1.40-1.51 (-9%)**; at J=6 the margin point
  is 1.920 N.m, so the declared 25% envelope margin is really +20%. Consequence at the
  1.6 N.m target: J 5.62, 53.7 A, P_cu 26-28 W, efficiency 92.3%, ceiling ~5,860 rpm,
  **S ~1.09 kVA, PF 0.49-0.54**. New `validation/torque_extractor/`,
  `torque_mesh_convergence.py`, `tests/test_torque_rescope.py`. Rule: quotable absolute
  torque must be ring-averaged with >=10 gap rows.
- **2026-10-21 (voltage and angle)** - **96 V does not fix PF**: at constant slot
  ampere-turns, `V ~ k`, `I ~ 1/k`, `R ~ k^2`, `P_cu` invariant and `S` invariant
  (`tests/test_voltage_scaling.py`, 1e-12); 96 V at k=2 doubles the speed ceiling at 51 A,
  96 V at k=4 halves the current for the same 999 VA. New
  `validation/voltage_and_angle/` + `pf_angle_sweep.py`. A 10-point current-angle sweep
  finds no angle that beats 26.25 deg on equal-output PF (A2 gate FAIL as declared), but
  the sweep is extractor-limited, so the true MTPA is not established and PF is recorded
  as a rotor (saliency) property, not a controller setting.
- **2026-10-21 (D-013)** - **winding turns decided: k = 2** (10 turns/coil at a=4, 2 x 1.2 mm
  per turn). 51 A peak, 12.9 V at 3000 rpm, R_ph 6.12 mOhm, copper loss unchanged (24-26 W),
  PF 0.53-0.58, S ~0.99 kVA; speed ceiling ~6,130 rpm without field weakening (was ~12,300).
  Exact scaling from the FEM reference state (N_c = 1.247), no new solves. Reopens only if
  the final gearing needs more than ~6,100 rpm.
- **2026-10-21 (winding spec v1)** - `prototype/design/winding_spec_v1.md` for the 130/50
  frame: documents that the **solved winding is single-layer** (6 coils/phase, `N_ph = 6*N_c`),
  correcting v0's double-layer description (a double-layer build would need torque
  re-certification), and gives the turns/speed/current trade (k=1/2/3 -> 102/51/34 A,
  12,300/6,100/4,100 rpm, kVA invariant at ~1.0). v0 marked superseded.
- **2026-10-21 (D-012 addendum 9)** - **third factor-2 in the copper path fixed**: the mean
  turn length was multiplied by a *half-turn* copper volume (`V_cu = 36*FILL*A_slot*(MTL/2)`,
  `R_ph = rho*6*N_c^2*MTL/(FILL*A_slot)`). Copper volume 0.82 kg (was 1.65), P_cu **25.6 W**
  at the target (was 53), rise **9.7 K** (was 20). Copper-only efficiency **95.1%**, with
  iron **92.7% (91.1-93.7%)**. PF re-derived: **0.53-0.58**, S 0.91-0.99 kVA. New
  `tests/test_copper_loss_routes.py` pins volume / 3I^2R / slot-fill identities (25 tests).
  Iron-loss s.4 gate note: the F4 ratio branch was written against the superseded 53 W.
- **2026-10-21 (D-012 addendum 8)** - **first-order iron loss** (`simulation/validation/iron_loss/`,
  `iron_loss.py`): anchored on the *grade guarantee* (M400-50A = 4.0 W/kg at 1.5 T/50 Hz),
  per-element B from the certified solve, **100 Hz electrical** (a first pass at 50 Hz was
  discarded before publishing). Result: **8.4-23.4 W, median 13.5 W** at the 1.6 N.m point;
  **efficiency 88.2% (86.7-89.0%; superseded by addendum 9 -> 92.7%)** including iron vs 90.4% copper-only; thermal ~66 W /
  ~25 K enclosed. Stator is lightly fluxed (B mean 0.46 T); 8.9 kg of active iron = 56 W/kg,
  i.e. the efficiency is bought with size. Open: rotor slot-harmonic loss (1800 Hz).
- **2026-10-21 (D-012 addendum 7)** - **PF cross-check**: the perpendicular flux was
  measured two ways at the operating point; torque route gives -5.20 mWb (PF 0.549),
  alpha-beta flux-linkage route gives -3.50 mWb (PF 0.596), **33% apart**. The
  alpha-beta *torque* identity returns 1.07 vs 1.59 N.m Maxwell (and 1.82 co-energy), so
  it captures ~2/3 of the torque on this single-layer 36-slot winding; the torque (and the
  envelope) stands. **PF is published as 0.55-0.60, S 1.0-1.1 kVA** at the target.
  A `dlam/dbeta` check attempt is recorded as invalid (flux magnitude varies with angle,
  ~3x `lam_beta`) so it is not repeated. New mode: `dq_model.py --pf-check`.
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

### Changed
- **2026-10-23 (D-017: PF re-certified like-for-like - D-014 survives its own gate)**
  - `saliency_screen.confirm_deep` now solves **BASE and S6 in the same run** with the
    annulus estimator; the hardcoded `base = 1.507` comparison is gone, so the printed
    gain is like-for-like at 26.0 deg, J=5.34, 3072/10.
  - Result: BASE **1.583 N.m, PF 0.469, 1111 VA**; S6 **1.873 N.m, PF 0.578, 1059 VA**.
    Gate G-PF1 (+0.030) -> **+0.109 PASS**. Torque +18.3% at 4.7% lower apparent power;
    1.768 vs 1.425 N.m/kVA.
  - Baseline PF is corrected from 0.532 to 0.469: the old value was measured on the
    uncorrected winding at 26.25 deg with a ring torque.
  - Consequence: PF is **closed**. The 1.06 kVA requirement belongs to the frame and the
    48 V rail, not to the rotor choice; rejecting S6 would buy 4.7% kVA for 18% torque.
    Ripple becomes the binding electromagnetic risk and is now the open gate.
  - The "order 12 = 2.4%" evidence for small ripple is **withdrawn**: it came from a 5 deg
    sampled curve, i.e. 1.5 samples per 7.5 deg period, so it could not see a 10 deg
    modulation at all.
- **2026-10-23 (torque dip characterisation, `torque_curve/RESULT.md` s.11)**
  - The dips are mirror-symmetric about 22.5 deg (4.00<->41.64, 12.50<->33.00) exactly as
    the geometry requires, which is evidence against a mesh artefact.
  - They are **not one harmonic**: spacing 8.50 / 10.00 / 10.50 / 8.64 deg, the 36-slot
    order is 0.010 N.m, and the apparent 32/rev amplitude (0.344 N.m) drops to 0.038 N.m
    when the 5-10 deg shoulder is excluded. Best description: a 0.25-0.3 N.m absolute
    modulation on a smooth envelope. Origin **unconfirmed**, reality supported.
  - `torque_ripple.py` gains the annulus columns and a window-matched adequacy check;
    Gen 3 gates (R2', R4', R6) are frozen in `torque_ripple/PLAN.md` before running.

### Fixed
- **2026-10-23 (D-018: torque ripple established at ~100% p-p, gate R3 FAIL)**
  - Gen 3 ran with the current pattern rotated with the rotor and the annulus estimator:
    46 points, 15-37.5 deg at 0.5 deg. p-p **100.2%** (annulus), 78.9/90.1/98.7% for
    rings 1/5/9, `1.30 +- 0.07 N.m`; extrema reproduce at 3072/10 within 0.5 pp.
  - The Gen 1 vs Gen 2 contradiction is **closed**: same window gives 91.4% (static) vs
    90.2% (synchronized), ratio 0.99. The old static curve was sampled at 5 deg and could
    not represent a 10-30 deg modulation; its "order 12 = 2.4%" is withdrawn.
  - Modulation period measured: 10 deg shift off by 0.371 N.m, **30 deg shift exact**
    (2.00 vs 32.00). 30 deg = 3 slot pitches = one winding repeat unit, so the mechanism
    is winding-locked (5th/7th mmf at 22.7%/18.5%), not slot-opening-locked.
  - Consequence: the certified 1.873 N.m is an instantaneous peak-angle value; the
    running mean over the measured window is 1.296 N.m. Full-period mean now measured.
  - `torque_ripple.py`: annulus columns added, window-matched adequacy (10 and 11.25 deg),
    ring-column mapping fixed, halt band widened so a legitimate dip cannot abort a sweep.
