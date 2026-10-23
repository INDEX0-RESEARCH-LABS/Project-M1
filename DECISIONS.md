# Decision Log

Format: `## D-NNN — Title` · date · context · decision · alternatives · status.
Status: `PROPOSED` | `APPROVED` | `REJECTED` | `SUPERSEDED` by D-NNN.

## D-001 — Workspace layout and toolchain
- **Date:** 2026-10-20
- **Context:** Phase Zero required a clean, version-controlled workspace without touching existing user projects.
- **Decision:** Create `project-m1/` at `/home/darion-dev/project-m1`, structure per master prompt; Python 3.14.8 venv with numpy/scipy/pandas/matplotlib/pytest; git for version control.
- **Alternatives:** Reuse an existing project directory (rejected — violates "clean workspace"); poetry/conda (rejected — venv + pip is sufficient and reproducible).
- **Status:** APPROVED (self, pending founder ratification)

## D-002 — No architecture selected yet
- **Date:** 2026-10-20
- **Context:** Master prompt forbids assuming a novel architecture exists.
- **Decision:** Baseline selection deferred to Gate B after literature review; no default commitment to SRM or SynRM.
- **Status:** APPROVED

## D-003 — Simulation tool candidates, not commitments
- **Date:** 2026-10-20
- **Context:** FEMM/Elmer not installed on this machine; Arch Linux (pacman/paru available).
- **Decision:** Attempt OpenFemm (AUR) and Elmer FEM installation at Gate B; record blockers rather than fabricate output. Python stack is the guaranteed fallback for analytical/geometry/analysis work.
- **Status:** PROPOSED

## D-004 — Provisional baseline: SynRM (4-pole multi-barrier); SRM as comparison architecture
- **Date:** 2026-10-20
- **Context:** Gate A desk comparison of SRM/SynRM/PMSM/IM for 0.5–1 kW, 24–48 V e-2W/e-3W.
- **Decision:** SynRM baseline (weighted matrix ~3.8 vs SRM ~3.6), SRM as live comparison, PMSM as literature benchmark only. Flip criterion: if Gate B same-envelope FEM shows SynRM losing torque density by >15% at equal current density, baseline becomes SRM.
- **Alternatives:** SRM baseline (rejected for now on ripple/NVH — documented 2W adoption blocker); EESM (parked — excitation system adds first-prototype complexity); axial-flux (parked — no verified magnet-free precedent at this band).
- **Status:** PROPOSED — requires founder approval; revisable at Gate B.

## D-005 — Primary solver: in-house 2D magnetostatics (scikit-fem); xfemm demoted to cross-check
- **Date:** 2026-10-20
- **Context:** xfemm 3.0 (AUR, rebuilt without Arch's `_GLIBCXX_ASSERTIONS`) is unreliable headless: `femmcli` lua hangs nondeterministically before `mi_saveas`; `fsolver` ran 13+ min without converging on a 10k-node problem while solving tiny ones in seconds; killed `fsolver` runs delete their own mesh files; `femmcli` lacks `mo_*` solution queries. `fmesher` and the `.fem` text format work fine.
- **Decision:** Primary Gate B/C solver = in-house linear A-z magnetostatics on scikit-fem + triangle (pip-only, fully scriptable, validated against an analytic straight-wire answer + mesh-convergence study). xfemm kept as secondary/independent cross-check where it works — H3 re-verification needs an independent model anyway. Elmer remains a second-opinion candidate.
- **Alternatives:** Keep debugging xfemm UB (rejected — nondeterministic); wine + FEMM 4.2 (rejected — heavy, unscriptable).
- **Status:** APPROVED (self)

## D-006 — Nonlinear saturation is in the critical path; M-19 is a validation-only material
- **Date:** 2026-10-20
- **Context:** Linear-μ torque curves would be a relative-only comparison: at 0.5–1 kW in a 66 mm-bore frame, the SynRM rotor bridges and stator teeth sit well above 1.5 T, so μr is not constant along the flux path and a linear curve would mis-rank candidate geometries. A nonlinear path also had to be built before any anchor comparison, since both Gate B anchors ran nonlinear material.
- **Decision:** Saturation (Picard-on-ν with a tabulated B-H curve) is implemented and validated **before** the first torque-vs-current curve. Validated against Ampère's law on a deeply saturated toroid: 0.49% / 0.18% error, iron at 1.92 T mean. M-19 from the local FEMM library is a **solver-validation material only** and must not be used for anchor comparisons — the anchor grades are 35A300 and M1000-65A (see `research/material_grades.md`), and neither curve is in the local library.
- **Alternatives:** Linear-μ curve first for relative comparison (rejected — would produce a curve that cannot be defended and would need redoing; the extra cost was one iteration scheme).
- **Status:** APPROVED (self). Evidence: `simulation/validation/known_answer/RESULT_NONLINEAR.md`

## D-007 — Gate B torque validation is per-anchor, with that anchor's own steel
- **Date:** 2026-10-20
- **Context:** Full texts confirm the two anchors use materially different steel: Kachapornkul 2022 uses 35A300 (0.35 mm, low-loss, JIS ≡ AISI 36F168 / DIN V300-35A); Rajini 2024 uses M1000-65A (0.65 mm CRNO, 2.1 T assumed saturation). These differ ~3× in loss class and 2× in thickness, so a single steel curve cannot validate both machines.
- **Decision:** The ≤5% Gate B torque-match criterion is applied **per anchor, using that anchor's steel curve**. Primary anchor = Rajini 2024 (1.2 kW, same power class, Indian context); secondary = Kachapornkul 2022 (3.5 kW, above our band, SRM). Where an anchor's own curve cannot be sourced, the comparison is reported as *relative* and the gate is **not** marked passed on it.
- **Consequence:** Sourcing citable B-H curves for 35A300 and M1000-65A is now on the critical path ahead of the torque curve — ahead of, not parallel to, because a curve run on M-19 compares materials rather than machines.
- **Status:** PROPOSED — needs founder confirmation of the primary-anchor choice.

## D-008 — D-004 flip criterion evaluated: SynRM baseline stands
- **Date:** 2026-10-21
- **Context:** D-004 set a flip trigger: if same-envelope FEM showed SRM beating SynRM on torque density by >15% at equal J, the baseline flips. The declared same-envelope comparison (`simulation/validation/srm_synrm_compare/RESULT.md`, all gates pass) found the opposite: SRM peak torque = 0.43× the SynRM's MTPA torque (equal installed Cu, equal fill, equal J; ±25% indicative band ⇒ 0.32–0.53), and SRM continuous duty (1/3 phase conduction) ranks it lower still.
- **Decision:** No flip. SynRM baseline stands for Gate C optimization. The SRM remains on record as the comparison architecture with the strongest same-toolchain evidence yet produced.
- **Status:** APPROVED (self) — the ±25% indicative label applies; a >2.3× SRM redesign would be needed to reverse the ordering.

## D-009 — Zero budget for materials data; bracket + indicative labels are the standing basis
- **Date:** 2026-10-21
- **Context:** Founder states no funds are available. Two pending purchases were gated on founder approval: MagWeb SMAG measured B-H library ($400/yr) and any paid M1000-65A curve source. Free-source search for M1000-65A B-H was already exhausted (`research/material_grades.md`: no citable free table exists for this grade). Both anchor runs and the SRM comparison were already built to run *without* these purchases, on the declared M-43/1006 dual-grade bracket (measured internal spread: 0.5% between bracket steels at anchor field levels).
- **Decision:** No external data purchases. The M-43/1006 bracket is the permanent material basis for Phase 0; all anchor comparisons keep the INDICATIVE ±25% label permanently (not just "until MagWeb is bought"). D-007 resolves to: Rajini primary anchor, envelope-level only. Any D-004-class ≤5% replication is cancelled as a Phase 0 goal and re-scoped to a future phase if funding appears.
- **Alternatives:** Defer purchase until later (same outcome); fabricate a curve for M1000-65A (rejected — rigor rule); borrow a library curve from the local FEMM database not matching the grade (rejected — mislabels the material, D-006 precedent).
- **Consequences:** (1) The remaining campaign percentage that was founder-gated collapses into accepted indicative status — Phase 0's simulation-validation work is effectively COMPLETE when the running rotor-upgrade sweep lands. (2) Prototype-material measurement later (e.g., coupon B-H at a local lab / the built machine itself) becomes the future upgrade path for material fidelity. (3) Downstream phases must not silently treat bracket steel as verified for M1000-65A.
- **Status:** APPROVED (founder, 2026-10-21).

## D-010 — Baseline geometry v1 for Gate C: span 12 mm, 2 barriers/pole, arc frac 0.62
- **Date:** 2026-10-21
- **Context:** The rotor-upgrade sweep (`validation/anchor_rotor_upgrade/RESULT.md`, gates U1–U3 pass) mapped the barrier family: nb=2 beats nb=3 consistently (~+6%), radial span rises monotonically 6→12 mm, and the wide 0.62 arc wins under deep saturation (U4 expectation violated and interpreted). The committed v0 layout (8.4 mm, nb 3) sits within ~5% of the family optimum.
- **Decision:** Gate C baseline = stator unchanged; rotor = barrier_radial_span 12 mm, n_barriers 2, barrier_angle_frac 0.62, bridge 0.6 mm. Measured at declared excitation: 9.0950 N·m/m (1536, delta 26.25) / 8.5265 (3072) — +5% torque at equal Cu, J, fill, envelope, for free.
- **Alternatives:** Keep v0 as Gate C baseline (rejected — we would optimize around a known-inferior point); adopt an iron-rich frac 0.30–0.50 layout (rejected — measured inferior in every member family).
- **Status:** APPROVED (self, data-backed; founder ratification rides along with D-004 sign-off).

## D-011 — Gate C as declared fails: extractor uncertainty dominates; family exhausted
- **Date:** 2026-10-21
- **Context:** The declared Gate C search (12 configs, C1–C5 gates) passed C1–C3 but the winner's multi-ring torque read +24.7% above its single-ring value (C4 ≤15% failed). Per the PLAN's no-post-hoc-swap clause, both baseline and winner were re-extracted under ONE extractor each (arbiter `gate_c_extractor_ab.py`): improvement = +8.5% (single-consistent) / +1.2% (multi-consistent) — inside the ±25–30% estimator spread, below the frozen +10% decision gate. The barrier family saturates at ~9.2–9.5 N·m/m (1536, single-ring), with bridge 0.4 mm / arc 0.70 / span ≥16 mm the winning direction.
- **Decision:** No winner declared. D-010 baseline unchanged (no candidate beats it beyond extractor uncertainty). Gate C is BLOCKED on the declared follow-up: settle the torque extractor (co-energy `T = −∂W′/∂δ` cross-check on one configuration, then re-label all absolute numbers with the standardized extractor). Before that, no absolute torque claims from this toolchain carry meaning beyond same-extractor ratios.
- **Alternatives:** Declare split20/0.70/0.4 the winner on the single-consistent +8.5% (rejected — inside the uncertainty the gate exists to catch); re-run the search with extra configs inside the exhausted family (rejected — mapped neighborhood is flat, cost without information).
- **Status:** APPROVED (self). Result: `validation/gate_c_search/RESULT.md`.
- **Addendum (2026-10-21, same day):** the declared co-energy arbiter was implemented and
  aborted as unusable — FD of W′ across re-meshed one-degree steps carries a ~60×
  numerical floor (ΔW′ = 8.9 J vs expected 0.15 J signal; `gate_c_coenergy.py` kept as
  honest negative artifact). Gap-row refinement 4→10 narrows the single/multi spread
  25–30% → 16–22% but does not converge at acceptable cost; the extractor question stays
  OPEN under this decision. In the same pass, the SRM/SynRM headline ratio was re-derived
  under one extractor per comparison (0.44 single / 0.33 multi; SRM side itself is
  extractor-robust at +0.6%): the ±25% band stands with consistent support — D-008/D-009
  unaffected. Standing rule: only same-extractor ratios are quotable; absolute N·m/m
  numbers carry their extractor name or the ±25–30% label.
- **Addendum 2 (2026-10-21, later same day):** gap-rows convergence study
  (`validation/extractor_convergence/`, rows 4→10→20→40 on the baseline at 3072 rays)
  resolved the character of the spread: **single-ring extracts are monotone
  mesh-converged** (8.5265→8.3414, −2.2% total, last step −0.5%), **multi9-ring is
  uncertifiable** (12.15→10.83→11.33→6.10, a −46% swing between adjacent levels).
  The former "+25–30% single-vs-multi spread" is reframed as one certified extractor
  vs one uncertified estimator — NOT symmetric doubt. Certified SynRM absolute:
  ≈8.34 N·m/m (single @ 3072/40). The single-consistent SRM/SynRM ratio 0.44 is the
  certified number; the multi column (0.33) downgraded to uncertified.
  E3's frozen mean-rule verdict remains FAIL (no adoption through that path) — the
  certification finding above is evidence-based, recorded in RESULT findings.

## D-012 — committed envelope vs target spec: winding infeasibility; envelope revision proposed
- **Date:** 2026-10-21
- **Context:** Winding spec v0 (`prototype/design/winding_spec_v0.md`) computes the
  48 V EMF budget against the committed anchor envelope (R_ro 45.5 mm, τ_p 71.9 mm,
  ψ₁ = 2.4–3.2 mWb/series-turn): a manufacturable 2W-class winding is impossible at
  the 3000 rpm target spec (1–2 turn bar coils at ~200 A/coil), hub-direct at ~750
  rpm is windable but 13–20× short on torque (0.62 N·m continuous thermal vs ~8–12
  N·m wheel demand), and a geared 1500 rpm variant stays bar-coil territory. Torque
  is turn-invariant at fixed slot AT (validated machinery property), so turns only
  trade the EMF window, not torque — the mismatch is geometric, not winding skill.
- **Options (owner: founder):** (1) envelope redesign to a 2W-sized frame (recommended;
  requires a fresh Gate-B-style validation pass on the new envelope); (2) revise the
  target spec (slower base speed + gearing, or higher bus voltage — marginal);
  (3) keep envelope with accepted torque deficit (not viable for a real 2W).
- **Decision:** PROPOSED — awaiting founder choice. In the interim, the belt/connection
  topology, k_w, ψ₁–turns–EMF formulas and the AT↔torque ledger are recorded as
  envelope-independent design tools; no Phase-0 validation artifact is invalidated
  (D-009 always framed Phase 0 as methodology, not marketability).
- **Status:** PROPOSED

## D-012 — addendum: sizing scan says the blocker is torque DENSITY, not envelope size
- **Date:** 2026-10-21 (same day as D-012)
- **Evidence:** `simulation/scripts/envelope_sizing.py` + `prototype/design/envelope_redesign_proposal.md`
  scan (36 candidates, 3000 rpm / 48 V, certified density): **1/36 windable**, that point
  6× short on continuous torque; **0/36** meet torque targets. Windability N_c ∝ 1/(B·D·L)
  and torque ∝ D⁴·L only intersect outside the 48 V / 3000 rpm constraint set.
- **Amended decision:** no envelope freeze until the ~4× gap between certified gap shear
  (0.64 kPa) and 2W-class machines (~2.5 kPa) is understood. Next step = zero-budget
  density workstream (published-machine comparative analysis + our J/AT convention audit),
  then choose topology/spec/voltage path. Original D-012 options remain available but are
  superseded as the immediate action.
- **Status:** PROPOSED (amended) — founder call on running the density workstream.

## D-012 — addendum 2: torque-density audit re-scopes the gap (no solver defect; J is the lever)
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/torque_density_audit/{PLAN,RESULT}.md`,
  `simulation/scripts/torque_density_audit.py` (one solve at the certified point, then MMF +
  gap-field spectra and textbook sizing).
- **Measured:** dominant MMF harmonic = 2 pole pairs (matches the 4-pole machine; the
  excitation convention is confirmed correct); A1 = 9.70 kA/m; Bhat = 0.269 T;
  sigma_textbook = 1.31 kPa; T_fem/T_sizing = **0.433**. That is normal SynRM utilization
  at delta = 26 deg with a bridge-saturated rotor - **no order-of-magnitude solver defect**.
  The ~100 N.m/m first-principles figure that motivated the audit was an arithmetic error
  in the audit premise (|AT|-sum/circumference is not the fundamental electric loading);
  corrected value reproduces the FEM within the normal utilization factor.
- **Re-scope:** the "~4x density gap vs 2W-class machines" is a **current-density/thermal**
  gap plus a frame-size choice, not a mystery: at J = 6 A/mm2 continuous the machine is
  normal; literature 1-2 N.m/L is reached at J ~ 15-25 A/mm2 (peak), consistent with the
  campaign's ~0.42 N.m/L at J = 6.
- **Scan correction:** the D-012 sizing scan assumed series-only windings. With `a`
  parallel paths, **24/36 frames are windable** (a in 1,2,4) and **1/36 meets both torque
  targets**: 2-pole, D = 130 mm, L = 74 mm, N_c = 3.4 (a=2) / 6.8 (a=4), 1.84/7.4 N.m
  (ESTIMATE). 4-pole fallback: bore ~150 mm, L 74 mm, a = 6 (~4 turns/coil), ~1.6 N.m cont.
- **Amended decision:** envelope direction = 130 mm-class 2-pole (or 4-pole ~150 mm
  fallback), winding with 2-4 parallel paths; next zero-budget validation = 2-pole rotor
  topology in `synrm_geometry` + certified chain, and a first-order copper-loss/thermal
  gate at J = 6. No envelope freeze until both land.
- **Status:** PROPOSED (amended). Founder direction still required only for the spec-level
  question (continuous rating defined thermally vs by J = 6).

## D-012 — addendum 3: 150 mm-bore 4-pole envelope FEM-validated (target met with ~3x margin)
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/envelope_validation/{PLAN,RESULT}.md`;
  `simulation/scripts/envelope_validation.py`, `envelope_certify.py`.
- **Result:** 4-pole, 36 slots, bore 150 mm, stator OD 217 mm, L 74 mm, span 12/nb2/frac
  0.62/bridge 0.6, J = 6 A/mm2, M-43: **68.49 N.m/m at rows40 = 5.07 N.m @ 74 mm**
  (1006 Steel bound 4.90); target 1.6 N.m met with ~3x margin. Bracket spread 3%.
  Winding ~4 turns/coil with a = 6 parallel paths.
- **Limitations (recorded):** rows sequence non-monotone (63.9 -> 68.9 -> 74.9 -> 68.5,
  last step -8.5%) so the number is INDICATIVE, not certified; local Bmax ~3 T is outside
  the BH bracket (torque insensitive, 3% spread); delta = 23.5 deg outlier is a
  mesh/barrier-edge artifact.
- **Decision:** 2-pole topology is not required for the target; the 4-pole 150 mm route is
  the validated direction and is over-sized for 1.6 N.m (~5 N.m at J=6), so the next task
  is a point design at bore 110-130 mm + certified rows40 + copper-loss/PF/thermal gate.
  No envelope freeze yet.
- **Status:** PROPOSED.

## D-012 — addendum 4: envelope point design (130/50) meets the target; PF/efficiency is the real gap
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/envelope_point_design/{PLAN,RESULT}.md`;
  `envelope_point_design.py`, `thermal_first_order.py`, `bridge_sweep.py`.
- **Point design:** bore screen 100-140 mm -> 120 and 130 mm certified at 3072 rows 4/20/40
  (drift +2.9% / +3.0%). **130 mm bore / 50 mm stack: 2.00 N.m at J=6 (1.25x margin)**,
  188 mm OD; **120/74 mm: 1.99 N.m**, 174 mm OD (take if OD is the constraint).
  Windability a=4 -> 5.0 turns/coil (130/50), 3.7 (120/74).
- **Thermal:** at the exact 1.6 N.m target (J ~ 4.8) ~97 W copper, ~37 K rise enclosed,
  ~84% copper-only efficiency -> viable. At the 2.0 N.m margin point (J=6) 151 W / 57 K ->
  needs forced air. Still air is not viable at J=6.
- **System-level finding (ESTIMATE, upper bound on VA):** kT ~ 0.018 N.m/A -> ~87 A
  phase at 0.5 kW, **PF ~0.25, ~4 kVA inverter**. This is the product-level gap, not
  torque or thermal. A proper PF needs the dq model (Ld, Lq, EMF) - next analysis.
- **Lever falsified:** bridge thickness 0.3-1.0 mm changes torque by <2% -> the 0.6 mm
  bridge is not the limiter; consistent with the Gate C family ceiling. This family is
  intrinsically low-density; fixing it is a topology research task.
- **Decision:** adopt 130/50 (fallback 120/74) as the validated envelope for Phase 1
  planning; record efficiency/PF as the open product gap; next zero-budget step = iron
  loss + PF from the same solution, then the 48 V vs 96 V architecture question.
- **Status:** PROPOSED.

## D-012 — addendum 5: torque corroborated; two-parameter dq falsified; PF withdrawn; J for 1.6 N.m corrected
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/dq_model/{PLAN,RESULT}.md`; `dq_model.py`.
- **Torque is corroborated**: at the MTPA point the Maxwell torque (40.12 N.m/m) and the
  co-energy derivative T = dW'/d(delta) (36.08 N.m/m) agree within **10%** (the extractor's
  known re-mesh floor). The envelope result does not depend on the dq model.
- **Two-parameter dq model FAILED**: `1.5p(Ld-Lq)id iq` = 0.643 N.m vs 2.022 N.m from the
  solve (**-68%**, factor 3.1, systematic at both current levels). The measured apparent
  inductances are converged (+0.0% / +0.1% from 1536 to 3072/rows10), so this is a **model
  class failure**, not a numerical one: the co-energy is dominated by saturated iron, not
  airgap saliency. Torque does not vanish at either alignment axis; the co-energy has a
  minimum at the torque peak.
- **PF WITHDRAWN**: the `PF ~0.25 / ~4 kVA` figure from addendum 4 is not admissible and is
  withdrawn. What survives: phase current ~115 A (J=6) / ~102 A (1.6 N.m point) at the
  current winding; `omega*lambda` = 6-8 V against a 26.3 V ceiling, so the winding is
  **under-turned ~3x** - rewinding to N_c ~3.7 (a=1) cuts the phase current to ~35 A at
  **identical copper loss**. That is the inverter-cost lever, independent of the failed model.
- **Measurement correction**: torque scales as **J^2** between 4.8 and 6 A/mm2 (ratio 1.581
  vs 1.5625). The 1.6 N.m target sits at **J = 5.34**, not 4.8 -> **~119 W copper, ~45 K
  rise, ~81% copper-only efficiency** (previously reported 97 W / 37 K / 84%). The thermal
  verdict is unchanged in kind; the target point is 8 K hotter.
- **Method limitation recorded**: the phase-flux probe is not mirror-symmetric (L at
  +18.75 deg from d = 0.0862 mH vs 0.1016 at the mirror point, -18%). The barrier polygons
  are symmetric by construction, so the cause is the discrete single-layer winding; future
  inductance claims need a symmetric excitation.
- **Open**: Maxwell vs co-energy disagree at the alignment axes (and Maxwell varies 47% per
  degree at delta=45) -> no cogging/ripple claim near the axes. A real PF needs a saturated
  dq model (lambda_d = dW'/di_d, lambda_q = dW'/di_q at the operating point, ~4 solves).
- **Status:** PROPOSED.

## D-012 — addendum 6: energy-balance check found two unit errors; PF = 0.55; thermal halved
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/dq_model/RESULT.md` s.7;
  `simulation/validation/envelope_point_design/RESULT.md` s.3-4; `dq_model.py`,
  `thermal_first_order.py`; logs `/tmp/opencode/m1/dq_model_v2.log`, `thermal_v2.log`.
- **How found:** the energy balance `P_elec = P_cu + T*w_mech` did not close (implied
  PF > 1). Two independent factor-2 errors:
  1. `dq_model.py` used the electrical angular speed (628 rad/s) with the torque, so
     mechanical power was 2x high. `T = 1.5p(lam_d i_q - lam_q i_d)` pairs with
     `w_mech = 314 rad/s`; `w_e = p*w_mech` belongs only inside the back-EMF.
  2. `thermal_first_order.py` used the FEM **peak** slot current density as RMS, so copper
     loss and every rise were 2x high. Correct: `P_cu = rho*(J_peak^2/2)*V_cu`, which is
     algebraically identical to `3*I_rms^2*R_ph` (asserted in the script).
- **Independent check:** a fresh-context arithmetic audit of 14 identities (w_m/w_e
  placement, peak/RMS, 3-phase/1.5 factors, copper-volume route) passes, max deviation
  0.08%.
- **PF published (ESTIMATE, model-independent):** from the alpha-axis flux linkage
  (slot stream function) and the Maxwell torque, `lam_perp = T/(1.5 p i)`; the failed
  two-parameter dq model is not used.
  - 1.6 N.m target (J=5.34): 102 A, 6.5 V, **999 VA, PF 0.549**, 1.59 N.m measured.
  - 2.0 N.m margin (J=6): 115 A, 7.3 V, **1253 VA, PF 0.555**.
  - Bracket: the L-based voltage gives PF 0.49-0.50, so the honest range is **0.49-0.56**.
  - Withdrawn for good: PF ~0.25 / ~4 kVA (VA upper bound, addendum 4).
- **Thermal corrected (130/50, enclosed):** J=6 -> 68 W / 26 K; target J=5.34 -> 53 W /
  20 K; still air J=6 -> 75 W / 55 K. Copper-only efficiency **~90%** at both points
  (was 81%). Iron loss still excluded, so this is an upper bound. The addendum-5
  "119 W / 45 K / 81%" was the peak-as-RMS error, not a real design penalty.
- **Decision:** no envelope change. Adopt PF 0.55 / ~1.0-1.25 kVA / ~100 A at the 48 V
  design winding as the working system figure. The product-level lever is the ~3x turns
  increase (~35 A at identical copper loss), not a larger controller. Thermal margin means
  the next zero-budget task is **iron loss** (efficiency is the only unquantified term),
  then the founder call on PF 0.55 / 100 A vs rewinding vs 96 V.
- **Lesson recorded:** a printed PF is not evidence; the energy balance is. Both errors
  would have been caught by `1.5*(v_d i_d + v_q i_q) = P_cu + T*w_mech` on the first run.
- **Status:** PROPOSED.

## D-012 — addendum 7: PF is a bracket (0.55-0.60); the alpha-beta torque identity understates torque by 33%
- **Date:** 2026-10-21
- **Evidence:** `dq_model.py --pf-check`, log `/tmp/opencode/m1/pf_check3.log`;
  `simulation/validation/dq_model/RESULT.md` s.8.
- **Two routes to the perpendicular flux at the operating point** (J=5.34, 1.592 N.m,
  102.1 A): torque route `lam_perp = -T/(1.5 p i)` = -5.20 mWb (PF 0.549); phase
  flux-linkage route `lam_beta = (lb-lc)/sqrt3` = -3.50 mWb (PF 0.596). **33% apart.**
- **The torque stands.** The torque implied by the alpha-beta linkages is 1.07 N.m vs
  1.59 N.m Maxwell and 1.82 N.m co-energy. That identity assumes a balanced sinusoidal
  winding; this single-layer 36-slot winding's phase linkages are not a 120-deg set
  (sum +0.61 mWb), so it captures about two thirds of the torque. Two distribution-free
  field integrals (Maxwell stress, dW'/ddelta) agree within 10%, and Maxwell was
  mesh/radius-certified. No envelope or kT change.
- **A rejected check is recorded, not deleted:** `dlam_alpha/dbeta` over a 10-deg rotor
  sweep is -15.2 mWb/rad, ~3x `lam_beta`, because the flux magnitude itself varies strongly
  with angle. Using that derivative as `lam_perp` was invalid; it is documented so nobody
  repeats it.
- **Decision:** quote **PF 0.55-0.60**, S **1.0-1.1 kVA** at the 1.6 N.m target
  (1.13-1.25 kVA at J=6). This does not change the addendum-6 conclusion: the inverter is
  ~1.2 kVA, not 4 kVA, and the ~100 A design-winding current remains the cost driver.
  The only clean closure is a rotating-field (time-domain) solution at fixed current angle.
- **Status:** PROPOSED.

## D-012 — addendum 8: iron loss quantified (~13 W median); efficiency ~88%, not 90%
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/iron_loss/{PLAN,RESULT}.md`;
  `simulation/scripts/iron_loss.py`, log `/tmp/opencode/m1/iron_loss.log`.
- **Method without fabricated coefficients:** the loss anchor is the *grade guarantee*
  (M400-50A = 4.00 W/kg at 1.5 T / 50 Hz by EN 10106), which the repo's material survey
  confirms is the one loss datum public catalogs do publish. Per-element B comes from the
  same certified solve as the torque; no new physics and no purchased data.
- **Frequency correction:** the machine runs at **100 Hz electrical** (3000 rpm is 50 Hz
  mechanical, p=2). The first pass used 50 Hz and is discarded (kept in the log); the plan
  was corrected before publishing any loss number. Scaling needs the hysteresis/eddy
  split, declared as a band (eddy fraction 0.30-0.60 at 50 Hz -> factor 2.6-3.2).
- **Result (130/50, J=5.34):** P_fe = **8.4-23.4 W, median 13.5 W** (27 combos of
  p_ref 3.3/4.0/5.3 W/kg, n 1.6/1.8/2.0, eddy split). Stator 8.4 W, rotor 5.0 W.
  At J=6: 10.4-27.9 W, median 16.7 W.
- **Efficiency:** **88.2% (86.7-89.0%)** including iron at the target; copper-only 90.4%.
  Thermal with iron charged to the winding: ~66 W, **~25 K** enclosed (was 20 K).
  The "thermally comfortable enclosed" conclusion stands, and F4's first branch applies
  (P_fe < 0.5 P_cu -> efficiency > 85%).
- **Physical reading:** the stator is lightly fluxed (B mean 0.46 T, max 1.42 T), so iron
  loss is small; the frame is oversized, and the 88% is bought with 8.9 kg of active iron
  (56 W/kg). This is consistent with the certified 0.43 torque utilization.
- **Open:** rotor **slot-harmonic** loss at 1800 Hz is not modelled (the 5.0 W rotor figure
  is a 100 Hz fundamental upper bound); with f^2 eddy scaling it is the dominant remaining
  efficiency uncertainty (order +/-5 W). Excess loss and the lamination building factor
  (+20-40% typical) are absent, so the band is a lower bound on the assembled core.
- **Decision:** adopt **~88% (87-89%)** as the working efficiency, label it ESTIMATE, and
  keep the rotor-harmonic term as the one open loss item. No envelope or BOM change.
- **Status:** PROPOSED.

## D-012 - addendum 9: copper-loss factor-2 (half-turn volume) corrected; efficiency 92.7%, PF 0.53-0.58
- **Date:** 2026-10-21
- **Evidence:** `simulation/validation/dq_model/RESULT.md` s.9,
  `simulation/validation/envelope_point_design/RESULT.md` s.3/s.4,
  `simulation/validation/iron_loss/RESULT.md`, `tests/test_copper_loss_routes.py`;
  logs `/tmp/opencode/m1/{thermal_fix,iron_loss_fix,dq_fix,dq_pfcheck_fix}.log`.
- **Defect:** one turn spans **two slots**, so the copper volume that the mean turn length
  multiplies is a *half-turn* volume. Both the thermal model and `dq_model`'s resistance
  used `MTL` directly (and `R_ph = rho*12*N_c^2*MTL/(FILL*A_slot)`), each exactly 2x high.
  Correct: `V_cu = 36*FILL*A_slot*(MTL/2)` = 91.9 cm3 / **0.82 kg**, and
  `R_ph = rho*6*N_c^2*MTL/(FILL*A_slot)` with `N_ph = 6*N_c` (the single-layer 36-slot
  pattern already recorded in dq RESULT s.8).
- **Why the old cross-check missed it:** the thermal volume route and the dq resistance
  route agreed with each other because both carried the same 2x. A cross-check between two
  copies of one error is not a check. Now pinned by a three-route test (volume,
  terminal 3I^2R, slot-fill identity) at 1e-12.
- **Corrected numbers (130/50, enclosed h=25):**
  - P_cu hot **25.6 W** at the target (was 53), **32.6 W** at J=6 (was 68).
  - Winding rise **9.7 K** (was 20), 12.3 K at J=6. Still air at J=6 is 25 K.
  - Copper-only efficiency **95.1%**; with iron loss (13.5 W median) **92.7%
    (91.1-93.7%)**, total ~39 W / ~15 K at the target.
  - Terminal: Vhat 6.44 V, i 102 A, S 986 VA, **PF 0.532** (torque route) .. 0.576
    (flux-linkage route) -> **bracket 0.53-0.58**, S 0.91-0.99 kVA. At J=6: 1.24 kVA.
- **Unchanged:** torque (1.592 N.m), envelope 130/50, iron loss, the 33% flux-route gap,
  the D2 dq-model failure, and the "voltage is not the constraint, current is" conclusion.
- **Process note:** this is the third factor-2 on the same extensive quantity (addendum 6:
  peak vs RMS; addendum 9: turn vs half-turn). Rule adopted: any change to a copper-loss
  or copper-volume expression must pass the three-route test, and no absolute loss number
  is quoted without it.
- **F4 gate note (iron loss):** the ratio branch text in `iron_loss/PLAN.md` was written
  against the superseded 53 W copper loss; the gate's intent is answered (iron costs ~2.4
  efficiency points) and the stale branch is recorded in `iron_loss/RESULT.md` s.4.
- **Status:** PROPOSED.

## D-013 - Winding turns: k = 2 (10 turns/coil at a=4), 51 A, ~6,130 rpm ceiling
- **Date:** 2026-10-21
- **Context:** D-012 left the turns count open because it trades current against speed
  headroom at constant torque, copper loss and apparent power. The application case is a
  2W drivetrain with a 5-6:1 reduction and a 45-60 km/h top speed, i.e. ~5,000-6,000 rpm
  at the motor.
- **Decision:** double the series turns relative to the FEM reference state
  (`N_c = 1.247` -> `2.494`, i.e. **10 physical turns/coil at a = 4**, 2 strands of 1.2 mm
  per turn). Phase current **51 A** peak, terminal voltage **12.9 V** peak at 3000 rpm,
  R_ph 6.12 mOhm, copper loss unchanged at 24-26 W, PF 0.53-0.58, S ~0.99 kVA.
- **Why scaling is exact, not a new solve:** at constant slot ampere-turns the torque and
  the field are unchanged; `lambda ~ N_c`, `R ~ N_c^2`, `I ~ 1/N_c`, so `V ~ N_c` and
  `P_cu = 3 I^2 R` is invariant. The field solutions stay at the reference state and remain
  the certification basis.
- **Trade made:** the no-field-weakening speed ceiling falls from ~12,300 rpm to
  **~6,130 rpm** (26.33 V / 12.9 V x 3000 rpm). At 5,600 rpm the winding uses 91% of the
  48 V envelope. Current halves, kVA does not change - the gain is controller and harness
  current rating, not silicon.
- **Does not change:** torque (1.592 N.m), envelope (130/50), iron loss, efficiency
  (92.7%), thermal (~15 K), PF bracket.
- **Revisit trigger:** the final gear ratio. If the motor must exceed ~6,100 rpm, k = 2
  fails on voltage and the choice returns to k = 1 (102 A) or k = 1.5 with field weakening.
- **Status:** PROPOSED (founder confirmation), implemented in `prototype/design/winding_spec_v1.md`.

## D-012 addendum 10 - Torque extractor bias: 1.592 -> 1.45 N.m, and the false 48/96 V binary
- **Date:** 2026-10-21
- **Trigger:** the PF-vs-angle sweep needed for the D-012 founder call produced a torque
  curve that is unphysical in shape (0.881 N.m at 32 deg, 1.761 at 36 deg). Chasing it
  found the cause in the extractor, not the machine.
- **Found:** torque was extracted with a single Maxwell-stress circle on a 1536-ray /
  4-gap-row mesh. Because the solver's B is element-wise constant, that single radius
  samples whichever element it lands in: at the operating point the same solution gives
  1.592 / 1.518 / 1.412 N.m for 1 / 5 / 9 sampling rings (-11%). Mesh refinement to
  3072/10 and 4096/10 gives 1.507 and 1.436 N.m ring-averaged, and the independent
  co-energy derivative at 3072/10 gives 1.399 N.m.
- **Adopted:** **1.45 N.m at J = 5.34 A/mm2, band 1.40-1.51 (+/-4%)**, midpoint of the
  Maxwell ring average (1.45) and the co-energy route (1.40). Correction **-9%**
  (range -5% to -12%). The previously quoted 1.592 is retained only as the audit trail.
- **Also found:** the 25% envelope margin at J=6 is really **+20%** (1.920 N.m vs the
  2.00 N.m margin point).
- **Consequences at the 1.6 N.m target (DERIVED):** J = 5.62 A/mm2, i = 53.7 A at k=2,
  P_cu 26-28 W, efficiency 92.3%, terminal 13.5 V, speed ceiling ~5,860 rpm (was ~6,130),
  **S ~1.09 kVA, PF ~0.49-0.54**. Holding 51 A instead gives 454 W shaft at 92.1% and
  PF 0.53-0.58.
- **Voltage question closed:** at constant slot ampere-turns `S = P/PF` is invariant
  (`V ~ k`, `I ~ 1/k`, `R ~ k^2`, `P_cu` invariant, all pinned at 1e-12 in
  `tests/test_voltage_scaling.py`). 96 V at k=2 doubles the speed ceiling at the same
  51 A; 96 V at k=4 halves the current and leaves S at 999 VA. **96 V is not a PF fix**,
  so "accept ~1 kVA or go to 96 V" was a false binary (see
  `validation/voltage_and_angle/RESULT.md` s.4 for the real options).
- **Angle question closed as far as the data allows:** no measured current angle beats
  26.25 deg on both torque and equal-output PF (A2 gate, as declared). The sweep is too
  noisy to locate the true MTPA, so 26.25 deg is retained as the operating point, not
  proven optimal. PF is a rotor (saliency) property, not a controller setting.
- **Rule adopted:** any quotable absolute torque must be ring-averaged (`n_rings >= 5`,
  preferably 9) on a mesh with `n_gap_rows >= 10`. Single-circle torque is a diagnostic,
  never a quotable number. Ratios and torque-per-stack comparisons that share the bias
  are unaffected.
- **What does not change:** the frame choice (ratio-based), SRM vs SynRM (D-008), the
  thermal conclusion, iron loss, and the qualitative blocker (PF/current at 48 V).
- **Status:** PROPOSED.

## D-014 - Deep-barrier rotor: +16% torque, PF 0.633, adopted
- **Date:** 2026-10-21
- **Context:** D-012's blocker is PF 0.49-0.54 / ~1.1 kVA. PF in a SynRM is set by
  saliency, and the certified rotor measures xi = Ld/Lq = 1.85 - low for a multi-barrier
  machine. Gate C (D-011) had swept this family for torque, never for saliency.
- **Found:** the barrier stack occupies the outer 10.4 mm of a 64.5 mm rotor radius, so
  q-flux dives under it through ~37 mm of solid iron. Radial depth is the lever nobody had
  varied. Sweeping it (4 barriers, 25% ribs, 0.62 angular fraction, bridge 0.6 mm):
  span 10.4 -> 20.8 -> 31.2 -> 44.5 mm gives T 1.59 -> 1.71 -> 1.76 -> 1.80 N.m and
  PF 0.532 -> 0.596 -> 0.625 -> 0.644 at the same current. Widening the barriers instead
  (frac 0.68 at full depth) collapses torque by 47%: the d-axis iron wedge is the
  constraint, not the barrier area.
- **Candidate (S6):** 4 barriers, angular fraction 0.62, rib fraction 0.25, radial span
  **44.5 mm** (zone_in 19.3 mm, 2.4 mm above the shaft), bridge 0.6 mm. Ring-averaged at
  3072/10: **T = 1.751 N.m (+16.2% vs the 1.507 baseline at the same extractor), PF 0.635,
  S 903 VA at 102 A (k=1)**.
- **First consequence estimate (2026-10-21, SUPERSEDED):** scaling the screen gave J 5.10,
  48.8 A, P_cu 22-23 W, ~93.3%, ~6,900 rpm, S ~0.76-0.80 kVA. The measured point below is
  the number to quote; S did not fall as fast as torque rose, and it is 0.86 kVA, not 0.8.
- **Why it was not adopted on 2026-10-21:** mechanical stress (4 full-depth barriers,
  3.8 mm ribs, 0.6 mm bridge, 1.5-2.4 mm yoke) had not been checked, iron loss had not
  been re-run, ripple was unmodelled, and the +/-4% extractor band still applies. Both
  named gates were then run and passed (below).
- **Gate note:** the screen's declared candidate rule required xi >= 2.5 and the candidate
  lands at 2.41, so it FAILS as declared. The xi clause was a proxy; the data show xi is
  not monotonic in the objective (a 2.74-xi variant loses half its torque). Revised rule,
  recorded rather than silently retuned: candidate if PF >= BASE + 0.03 and T >= 0.95 x
  BASE. Both are met by a wide margin (+0.11, +13%).
- **Gate B (2026-10-22): PASS.** A validated plane-stress FE (solid-disk known answer
  within 0.17%) gives SF 16.6 at 6000 rpm and 12.2 at 7000 rpm on the declared p99.5
  rule, and 9.5/7.3 even on the absolute corner peak; airgap closure 3.8 um of 520.
  The old hand bound of ~420 MPa ("bridge carries the whole rim") is refuted: the three
  3.8 mm arc ribs share the rim load. `validation/rotor_stress/RESULT.md`.
- **Iron loss (2026-10-22): PASS.** 12.1 W median (7.5-21.2) at J=5.34, below the
  baseline 13.5 W, because the deep barriers remove 1.5 kg of rotor iron. The certified
  target point re-solved at J=5.21: ring-averaged 1.663 -> adopted 1.60, PF 0.633,
  S 0.861 kVA, Vhat 11.5 V at k=2, efficiency 93.4%, ceiling ~6,840 rpm.
- **Status:** ADOPTED (technical). This replaces the shallow-barrier rotor as the design
  of record; `STATUS.md` now quotes the deep-rotor numbers with the baseline in
  parentheses. Open risks that adoption does not close: torque ripple/NVH (unmodelled,
  the largest remaining), punching tooling for 16 barriers and 3.8 mm ribs, and the fact
  that the co-energy arbiter was not re-run on S6 (the baseline's -4% factor is applied,
  so the +16% ratio is stronger evidence than the absolute 1.685 N.m).

## D-015 - Slot binning followed the wrong angle convention; certified numbers frozen
- **Date:** 2026-10-23
- **Context:** auditing the torque-ripple model turned into a check of the torque-angle
  curve itself. `rajini_anchor`'s docstring (2026-10-21) states that delta = 0 and
  delta = 45 must both be torque-free by symmetry, and `synrm_geometry.stator_profile`
  centres slot k at k*pitch, which is why `synrm_mesh._in_slot` was corrected to that
  convention on 2026-10-20.
- **Found:** `split_slots` still binned with `floor(theta/pitch)`, so bin i spanned
  [i*pitch, (i+1)*pitch) and sat centred on (i+0.5)*pitch. Measured geometrically:
  **+0.513 pitch offset on every bin** (max 0.519), zero after the fix. The applied MMF
  was therefore rotated by half a slot pitch (5 deg mech, 10 deg elec), and every belt
  boundary averaged two phases into one current density.
- **Gate A1 (pre-existing invariant, not a new threshold):** T(0) and T(45) <= 5% of peak.
  As shipped 0.4386 and 0.4577 N.m (27% and 29%) -> **FAIL**, with the real zero displaced
  to 50 deg. Fixed: 0.0102 and 0.0296 N.m (0.6% and 1.9%) -> **PASS**.
- **Decision:** fix `split_slots` (one line, `+0.5*pitch`), keep the invariant as a
  regression test (`tests/test_rajini_winding.py`), and **freeze D-014's headline numbers
  rather than withdraw them**. They were computed self-consistently on the shipped
  binning, which describes a valid machine - just not the winding the labels and the
  drawing describe.
- **Why freeze and not re-quote:** the fix is not a relabelling. Torque at the same label
  moves 1.5761 -> 1.7897 N.m (+13.6%) because removing the belt-boundary phase mixing
  changes the machine. Torque, lambda, PF, S, efficiency and the speed ceiling are all
  affected and must be re-derived on the corrected winding.
- **Also found in the same audit, recorded here because it gates the re-certification:**
  the torque-angle curve has dips the 5 deg grid stepped over (T9 < 0.05 N.m over
  42.5-43.75 deg against 1.07 at 40 and 0.46 at 45), reproducible at 3072/10; and the
  Maxwell extractor cannot resolve torque below ~0.5 N.m (four radial gap bands spread
  10.7% at the certified point, 9x at the dip), because element-constant B gives an O(h)
  circle integral. A robust area-integral estimator (`fem_magnetics.torque_annulus`) was
  added and agrees at the certified point (1.536 vs 1.576 N.m) with an honest per-band
  error bar.
- **Status:** FIXED (winding), OPEN (re-certification, dips, low-torque extractor).
  `validation/torque_curve/RESULT.md`. Next: full 0.25 deg static sweep on the corrected
  winding with band error bars, then re-certify the operating point.

## D-016 - Re-certification: annulus estimator is standard, torque is 1.77 N.m, PF drops to 0.578
- **Date:** 2026-10-23
- **Context:** D-015 froze D-014's numbers pending re-certification on the corrected
  winding. That work is done: a 181-point 0.25 deg static sweep, four null/mechanism
  experiments, a four-mesh ladder, and re-runs of the certification scripts.
- **Gate declared before the sweep:** A1 (T(0), T(45) <= 5% of peak) already PASS from
  D-015; A2 (0.25 deg curve within 10% of the 5 deg interpolant) - **FAIL**, 102/181
  points, as expected once the dips are real.
- **Found 1 - the dips are torque reversals, not notches.** `torque_at` returns `abs()`,
  which hid a genuine sign change. Signed values from all three estimators agree: the
  torque is negative from ~1.5 to ~3.9 deg and crosses zero at 3.95 deg, with a -0.27 N.m
  lobe (15% of peak). Dips also at 12.5, 22.5, 33.0 and 41.75 deg (14-29% of peak).
- **Found 2 - four candidate mechanisms, all refuted.** Ray-merge slivers (tolerance
  1e-4 -> 2e-3 changes nothing; 5e-3 goes singular); material misclassification (barrier
  and rotor-iron areas constant to 1e-6 over 46 angles); extractor bias (the solid-rotor
  null is constant in angle, so it cannot create a dip); discretisation (three meshes at
  each dip agree to within ~25% on a value already 5x below the peak). Saturation is an
  amplifier, not the cause: dip/peak is 0.455 at J=1.05 (linear), 0.333 at 2.60, 0.292 at
  5.21. **The dips are converged features of this model.**
- **Found 3 - the solid-rotor null test condemns the single-circle extractor.** A rotor
  with no barriers must give exactly zero torque. Measured at four angles: single circle
  **+0.55 N.m** (33% of working torque), 9-ring -0.04, annulus -0.13, all constant in
  angle. `dq_model.solve_point` used the single circle, so it fed torque into PF and
  efficiency through `p_mech`.
- **Decision - estimator:** the gap area integral (`torque_annulus`) is the standard
  absolute-torque estimator. Evidence is convergence, not preference: over meshes
  1536/4, 2048/6, 3072/10, 4096/10 it reads 1.739 / 1.747 / 1.778 / 1.770 N.m (2.2%
  spread), against 9.0% for the single circle and 22.8% (non-monotone) for the 9-ring
  average. `solve_point` now returns `T_ann` and `T_ann_err`; `iron_loss`, `pf_check` and
  `saliency_screen` use them. The single circle is kept only for legacy comparison.
- **Re-certified numbers at delta = 26.0 deg** (the argmax of the corrected sweep;
  25.5-27.5 is a plateau within 1.5%):
  - torque **1.77 +- 0.14 N.m** (annulus, 2.2% mesh spread; the error bar is the
    solid-rotor null bias) versus D-014's frozen 1.60. A co-energy check at J=6 gives
    40.9 N.m/m against the annulus 46.4 (-12%), so the band is honest rather than tight.
  - iron loss median **16.3 W** (band 10.1-27.4) versus 12.1 W frozen - the corrected
    winding concentrates the same MMF and the rotor saturates harder (Bmax 2.83 T).
  - efficiency **93.2% (91.6-94.1%)** versus 93.4% frozen: unchanged within the band.
  - S6 at J=5.34, 3072/10, annulus: T = 1.873 N.m, **PF 0.578, S = 1059 VA** versus the
    frozen 0.633 / 903 VA. **PF moves down 0.055 and apparent power up 17%.**
- **What is NOT established:** the like-for-like baseline PF under the new estimator has
  not been re-run, so the *size* of S6's PF advantage is unknown; only its sign (above
  the 0.49-0.54 baseline) is plausible. Since PF was the reason to adopt the deep-barrier
  rotor, this is the next gate, not a footnote. The +24.3% torque figure printed by
  `saliency_screen --confirm` compares against a hardcoded 1.507 baseline ring number and
  is **not** quotable as a like-for-like gain.
- **Status:** torque and efficiency RE-CERTIFIED. PF OPEN pending a same-estimator
  baseline. Ripple still NOT ESTABLISHED at this point (superseded by D-018), with a
  corrected experiment design: this sweep
  holds the stator pattern fixed while the rotor turns, which makes it a load-angle
  curve. A running machine holds the current in the rotor frame, so ripple must be
  measured with the pattern rotated with the rotor. `validation/torque_curve/RESULT.md`.

## D-017 - PF re-certified like-for-like: D-014 survives its own gate (2026-10-23)

**Problem.** D-016 re-certified torque and efficiency with the annulus estimator but left
PF open: S6 read 0.578 / 1.06 kVA against D-014's frozen 0.633 / 0.90 kVA, and the
baseline had never been run through the same estimator, angle and winding. PF was the
reason the deep-barrier rotor was adopted, so the sign of the advantage was not enough.
A second defect sat in the same function: `saliency_screen.confirm_deep` compared the
candidate against a **hardcoded** `base = 1.507` ring-average torque and printed a
"+24.3%" that mixed extractors and angles.

**Gate declared before the run (G-PF1):** S6 survives D-014's adoption criterion iff
`PF(S6) - PF(BASE) >= +0.030` absolute, both solved at 26.0 deg, J = 5.34 A/mm2, mesh
3072/10, same annulus estimator.

**Change.** `confirm_deep` now calls a `certify()` helper for BASE and S6 in the same run;
the hardcoded constant is gone, so no stored number enters a comparison.

**Result** (3072/10, 26.0 deg, J=5.34, annulus; `saliency_screen --confirm`):

| rotor | T N.m | PF | S VA | i A | Vhat V |
|---|---|---|---|---|---|
| BASE (3 barriers) | 1.583 | 0.469 | 1111 | 101.9 | 7.27 |
| S6 (4 barriers) | 1.873 | 0.578 | 1059 | 101.9 | 6.93 |

- **G-PF1 PASS**: +0.109 against a +0.030 gate. Torque +18.3% at 4.7% *lower* apparent
  power; 1.768 vs 1.425 N.m/kVA (+24%).
- The baseline reproduces its certified torque (1.583 vs 1.592 frozen at 26.25), so the
  harness is not flattering S6 by breaking the baseline.
- Baseline PF is **0.469**, not the 0.532 quoted since Gate C. The 0.532 was measured on
  the uncorrected winding at 26.25 deg with a ring torque; the D-015 fix and the annulus
  estimator both move it. That is a correction of a superseded number, not a new
  uncertainty: BASE and S6 move together, so the difference is like-for-like.

**Consequences.**

1. D-014 stands on its original justification, with a larger margin than the frozen
   comparison implied. No geometry change is triggered.
2. The 1.06 kVA question changes owner. S6 needs *less* apparent power than the baseline
   (1059 vs 1111 VA); the frame and the 48 V rail set the kVA, not the rotor choice. D-012
   is now purely "fund a ~65-88 A class controller", and rejecting S6 would buy 4.7% less
   kVA for 18% less torque.
3. Ripple is the remaining electromagnetic risk and now the binding one (see
   `validation/torque_ripple/PLAN.md`, Gen 3).
4. `--confirm` costs two 3072/10 solves (~10 min) instead of one; that is the price of
   never comparing against a constant again.

## D-018 - Torque ripple established at ~100% p-p; the design fails its ripple gate (2026-10-23)

**Problem.** Ripple had been "NOT ESTABLISHED" for two turns of work. Gen 1 (stator-frame
current) was deemed the wrong excitation; Gen 2 (rotor-frame current) swung 60-90% and was
deemed inconsistent with a smooth static curve; the two were treated as irreconcilable.
D-017 also left open whether the dips in `torque_curve/` meant anything for a running
machine.

**What was actually wrong.** Two defects, both in the comparison rather than the field
solve. (1) The static curve Gen 2 was checked against was sampled every 5 deg, hence at
most two samples per 10 deg period: it could not have shown the modulation even if the
modulation were real. (2) `torque_at` returns `abs()`, which turned the sign reversal into
a notch. Neither defect is in `solve_raw` or the mesh.

**Gates** were frozen in `torque_ripple/PLAN.md` before Gen 3 ran (R1-R6, including R2'
band-spread limits and R6 reconciliation with the static curve).

**Result** (`sweep_gen3_0p5deg.csv`, 46 points, 15-37.5 deg at 0.5 deg, annulus):

| estimator | p-p |
|---|---|
| rings 1 / 5 / 9 | 78.9% / 90.1% / 98.7% |
| **annulus** | **100.2%** (1.30 +- 0.07 N.m) |

- R2' **partial**: the two end-window p-p agree to 1.0 pp (gate 2.0), but the estimator
  band spread is 14.3% median / 58.8% max (gates 10/20%). The fraction is therefore good
  to a few percent, not exact.
- R4' **pass**: extrema at 3072/10 give p-p 1.3045 vs 1.2982 coarse, 0.5 pp (gate 2 pp).
- R6 **pass, ratio 0.99**: static and synchronized sweeps give 91.4% and 90.2% over the
  same window. The two excitation models agree; the contradiction is closed.
- R3 **FAIL**: 100% p-p against a 15% threshold, robust across four estimators and two
  meshes.

**Locking, measured not assumed.** `T(delta+10)` differs by up to 0.371 N.m (26 pairs), so
the modulation is not at the 10 deg slot pitch. `T(delta+30)` is identical to four
decimals (2.00 vs 32.00). 30 deg mechanical = 60 electrical = one repeat unit of the 3-phase
winding (36 slots, 4 poles, q=3). The modulation is therefore **winding-locked**, which
matches the known 5th/7th mmf harmonics at 22.7%/18.5% of the fundamental, i.e. the
6th-electrical-harmonic family.

**Consequences.**

1. The certified 1.873 N.m at 26.0 deg is an **instantaneous peak-angle value**. The
   full-period sweep (46 points, 0-90 deg at 2 deg) measures a **running mean of 1.202 N.m
   at J = 5.21** (rings 5: 1.374), min 0.587 / max 1.739. The three 30 deg periods give the
   same mean to four decimals (1.1918 each). So the sizing number drops 32% and the design
   is **undersized on a mean-torque basis**: the 1.6 N.m target needs about J = 6.9, i.e.
   ~1.8x the copper loss (23-24.5 W -> ~42 W), ~89.6% efficiency and ~1.4 kVA. Those are
   linear planning estimates that ignore saturation (which makes them worse), not
   certified numbers; re-certification at the new J is required before they are quoted.
   Note this is a **stator-level** defect, so D-014's relative rotor advantage is
   untouched while the absolute design point moves.
   **Corrected by D-019 and D-021:** the mean is 1.2305 N.m (1.202 came from weighting the
   one physical point at 0/30/90 deg three times out of 46; 1.1918 was the 2 deg grid,
   itself biased 3.2% low); J for 1.6 N.m mean is 6.77; and the mechanism is slot-locked, not winding-locked, so the
   baseline inherits the *period* and almost exactly the *depth*, not just the former.
2. The R5 lever map frozen in the plan (slot opening or skew) does not cover the measured
   answer. ~~The first lever is the winding layout; skew of one slot pitch is designed to
   suppress slot-order ripple and will under-deliver on a 6th-electrical component.~~
   **Corrected by D-019, which measured it:** the dominant order is the slot order 36, and
   skew of *two* slot pitches (20 deg) takes p-p from 96.6% to 12.4%, inside the gate. The
   winding layout is the second-step lever on the residual order-12 component.
3. This does not reopen D-014's rotor choice: the baseline rotor has the same winding and
   would inherit the same mechanism. It reopens the **stator**, not the rotor.
4. Nothing here is experimental. It is a 2D current-source model with no skew, no
   eccentricity and no PWM. Magnitude is one order larger than a shippable 2W traction
   motor, which is the strongest reason to suspect the model over-predicts - but no test
   has yet shown that, and the burden is now on a declared slot-opening/skew study.

## D-019 - The ripple is slot-locked, not winding-locked; skew is the lever (2026-10-23)

**Problem.** D-018 established the modulation and its period (exactly 30 deg mech) but
named the wrong lever: "locked to the winding repeat unit, so the lever is the winding
layout". A period is a property of the *set* of harmonics present; it does not identify
which one dominates. Three questions were open: which order dominates, does the rotor
cause it, and what actually fixes it.

**What was found**, all from data already on disk (no new solves except the baseline
sweep):

1. **Order 36 dominates.** A least-squares fit of one exact period with only the
   harmonics a 30 deg period permits gives S6 amplitudes of 0.161, 0.088, **0.457**,
   0.014, 0.025 N.m at 0.5 deg (0.157, 0.087, 0.495, 0.009, 0.020 at 2 deg). Order 36 is
   one event per 10 deg slot pitch, 2.8x the phase-belt order 12. The 0.5 deg sweep puts
   the dips at 3.0, 12.5 and 22.5 deg - spacings 9.5 and 10.0 against a 10.0 deg slot
   pitch - and shows the dip is a notch, with real energy at orders 72 and 108.
2. **It is stator-side.** The baseline 2-barrier rotor (`sweep_base_2deg.csv`, J=5.62,
   same 30 deg span) dips at the *same angles* (12.0 and 22.0 deg), to the same depth
   within 0.10 N.m, with order 12 identical to 0.2% and order 36 within 6%. Two very
   different rotor geometries producing the same slot-order torque means the barriers are
   not the mechanism.
3. **Skew removes it, and skew must be an integer number of slot pitches.** Multi-slice
   2D skew applied to the measured curve (0.5 deg): 10 deg -> 23.1% p-p (from 107.2%),
   15 deg -> 25.9% (*worse* than 10 deg: 1.5 pitches does not cancel order 36), **20 deg ->
   12.9%, inside the 15% R3 gate**, 30 deg (one winding repeat) -> **2.7%**. The mean is
   unchanged in this model.
4. **A correction, twice over.** The D-018 mean of 1.202 N.m included both 0 and 90 deg on
   the 0-90 grid; 0, 30 and 90 are the same physical point (T = 1.6660), weighted three
   times out of 46. Over one exact period at 2 deg that gave 1.1918 N.m. The 0.5 deg sweep
   then showed the 2 deg grid was itself biased 3.2% low by quadrature across the notches:
   the mean is **1.2305 N.m** and p-p is 107.2%. See D-021, which supersedes this number.

**Decision.**
- The primary ripple lever is **rotor skew of two slot pitches (20 deg mech)**, not
  winding layout. Winding layout (q=3 -> q=4 / 48 slots) becomes a second-step lever on
  the order-12 residual left after skew.
- The baseline's measured mean makes D-014's advantage a **mean-basis** statement: +12% to
  +21% at equal current (T ~ J^1..J^2 bracket) against the +18.3% instantaneous figure.
  D-014 holds; its margin is not a ripple artefact.
- The mean torque remains the binding problem: 1.2305 N.m at J=5.21 means J=6.77 for the
  1.6 N.m target (~40 W copper, ~89.9% efficiency, D-021). Skew does not address that, and
  the two must not be conflated.

**Caveats.**
- Multi-slice 2D skew ignores axial flux redistribution. A real machine has one current
  vector, so the saliency is averaged along the stack: the skew factor for 40 deg
  electrical is sin(20 deg)/(20 deg in rad) = 0.980, i.e. ~2% mean torque, which the model
  does not charge. A skewed-rotor solve is required before this is a certified number.
- Order 36 at 0.495 N.m is 42% of the mean, and real SynRMs show single-digit slot-order
  ripple unskewed. The model is plausibly 2-4x high (no skew, no axial redistribution,
  sharp-edged 2D slots). Magnitude stays in-model until there is a bench; the mechanism
  and its remedy are now identified, which is what a zero-budget phase can deliver.
- The harmonic table ranks mechanisms; it does not reconstruct the curve. Residual rms is
  0.137 N.m (11.4% of mean) because the sharp dip shoulders are not spanned by five
  harmonics.

## D-020 - Mean torque sets the envelope; the 30% deficit is cheapest bought with stack length (2026-10-23)

**Problem.** D-018/D-019 moved the design point from an instantaneous 1.77 N.m to a
running mean of 1.2305 N.m at J = 5.21 A/mm2 (D-021). The 1.6 N.m target is therefore
30% short.
The earlier planning estimate met it by raising current to J = 6.99; that number was never
compared against the alternatives, and one of the affected quantities - efficiency - had
not been restated on a mean basis at all.

**What was found.**

1. **The certified 93.2% efficiency is a peak-angle figure.** In a synchronous-frame drive
   the current magnitude is constant over a revolution, so copper loss is constant while
   the torque is not. Energy-average efficiency therefore uses the mean torque:
   eta = T_mean*omega / (T_mean*omega + P_cu + P_fe). At J = 5.21, T_mean = 1.2305 N.m
   (D-021), omega = 314.16 rad/s: 386.6 / (386.6 + 23.75 + 16.3) = **90.6%** (90.5-90.8%
   over the copper band 23-24.5 W), not 93.2%. The 2.6 pp difference is the same
   peak-versus-mean error that D-018 found in torque.
2. **The deficit can be bought three ways, and they are not equivalent.**

| route | what changes | copper loss | efficiency | apparent power | voltage ceiling |
|---|---|---|---|---|---|
| A. current | J 5.21 -> 6.77 (+30%) | 23.75 -> 40.2 W | 89.9% | 1.06 -> **1.38 kVA** | 6840 rpm (unchanged) |
| B. stack length | L 50.4 -> **65.5 mm** (+30%) | 23.75 -> **30.9 W** | **90.6%** | **1.06 kVA** (unchanged) | 6840 -> **~5260 rpm** |
| C. larger bore | 130 -> ~150 mm | not evaluated | - | - | - |

   Torque is **exactly proportional to L in this model**: the 2D field solve does not
   depend on axial length, only the force integral does. So route B is the most reliable
   of the three estimates - it needs no new solve to be right within the 2D approximation.
3. **Route B does not change any loading.** At fixed J, copper loss per unit length is
   identical (0.471 W/mm in both cases), so thermal flux, current density and kVA are
   unchanged. It is a 30% longer machine working exactly as hard, not a machine working
   30% harder.
4. **Route B's cost is speed range.** Back-EMF scales with L, so the ~6840 rpm voltage
   ceiling falls to ~5260 rpm. At a 3000 rpm nominal that is ample headroom, but it is a
   real trade against route A, which keeps the ceiling.

**Decision.**
- **Route B (stack length 50.4 -> 65.5 mm, J held at 5.21) is the primary response** to
  the mean-torque deficit. It holds the two scarce resources - current density and 48 V
  kVA - fixed, and keeps efficiency at 90.6%.
- Route A is the fallback if stack length is capped by the application envelope.
- Route C is deferred until the frame is chosen; it needs the barrier geometry redesigned,
  so it is not a cheap option.
- **Efficiency is quoted as 90.6% (mean basis) from here on**; 93.2% is retained only as a
  peak-angle figure and must be labelled as such wherever it appears.
- Ripple no longer sets the envelope: D-019 gives 12.9% p-p in-model with a 20 deg skew
  at a cost of ~2% mean torque.

**Caveats.**
- End-winding resistance and end leakage do not scale with L, so route B's real gain is
  slightly below 1.343x; a longer stack also dilutes the end-loss fraction, which partly
  offsets that.
- Iron loss scaling with L assumes unchanged flux density and volume - correct to first
  order, end-region effects ignored.
- Route B changes the frame, so it re-opens the D-012 point design. It does not change the
  rotor or stator *geometry* decisions, which are scale-invariant in this model.
- All of it is a 2D current-source model: no skew (D-019), no PWM, no end effects.

## D-021 - Mean torque is 1.2305 N.m: a 2 deg grid reads it 3.2% low (2026-10-23)

**Problem.** D-018 through D-020 took the full-period mean and p-p on a 2 deg grid
(1.1918 N.m, 96.6%). D-019's central claim - that a 20 deg skew brings the ripple inside
the 15% gate - had only ever been tested on that grid.

**What was found.** A 0.5 deg sweep over one exact period (61 points,
`sweep_period_0p5deg.csv`, log `/tmp/opencode/m1/ripple_period_0p5.log`):

| grid | samples per period | mean | p-p |
|---|---|---|---|
| 2.0 deg | 15 | 1.1918 N.m | 96.6% |
| 1.0 deg | 30 | 1.2258 N.m | - |
| **0.5 deg** | **60** | **1.2305 N.m** | **107.2%** |

1. **This is a quadrature error, not noise.** The dips are V-notches about 3 deg wide with
   a bottom of 0.4268 N.m at 12.50 deg. With five samples per 10 deg slot period the 2 deg
   grid lands on the flank at 12.0 deg (0.5870) and misses the bottom by 0.16 N.m; across
   the period it over-samples the falling edges and under-samples the flat tops, so the
   estimate is systematically low. It converges: 1.0 -> 0.5 deg moves only 0.005 N.m.
2. **The harmonic picture is the same fact from the other side.** At 0.5 deg: order 36 =
   0.457, order 72 = 0.269, order 12 = 0.161, order 108 = 0.102, order 24 = 0.088. The
   residual only falls below 1% with harmonics to order 240. The notch needs the higher
   orders, which is why a grid that samples 5 points per slot period cannot integrate it.
3. **Skew is confirmed on the finer curve**: 10 deg -> 23.1%, 15 deg -> 25.9%,
   **20 deg -> 12.9% (PASS)**, 30 deg (one winding repeat) -> **2.7%**. D-019's conclusion
   holds; its numbers move by about half a point.

**Corrected numbers** (these supersede D-018, D-019 and D-020 wherever they differ):

| quantity | before | after |
|---|---|---|
| mean torque at J=5.21 | 1.1918 N.m | **1.2305 N.m** |
| p-p, unskewed | 96.6% | **107.2%** |
| deficit to the 1.6 N.m mean target | 34% | **30%** |
| J for 1.6 N.m mean (linear) | 6.99 | **6.77** |
| copper loss at that J | ~43 W | **~40 W** |
| efficiency at 1.6 N.m | 89.5% | **89.9%** |
| apparent power at 1.6 N.m | 1.42 kVA | **1.38 kVA** |
| efficiency at J=5.21, mean basis | 90.3% | **90.6%** |
| stack-length route | 67.7 mm, 90.3%, ~5100 rpm | **65.5 mm, 90.6%, ~5260 rpm** |
| order 36 / order 12 | 0.495 / 0.157 (3.2x) | **0.457 / 0.161 (2.8x)** |
| skew 20 deg p-p | 12.4% | **12.9%** |

**Decision.** The corrected numbers are the quotable ones. Every conclusion of D-018,
D-019 and D-020 survives: the ripple is slot-locked, skew-fixable and stator-side; D-014's
rotor choice holds; stack length remains the cheapest route to the target. Only the
magnitudes move, by 2-3%.

**Standing rule added.** Any mean or p-p of this torque curve must be computed at 0.5 deg
or finer, or carry an explicit grid-convergence check reported next to it. This joins the
standing list of statistics that looked settled and were not (the four poorly chosen pass
statistics; the FFT leakage; the aliased order-12 reading; the 6-pair period test).

**Why it was worth the 40 minutes.** The 20 deg skew claim was the whole basis for saying
the ripple risk is closed. It is, but it was closed on a 3%-wrong mean and a 10 pp
understated modulation. A gate that passes at 12.9% rather than 12.4% has less margin than
advertised, and the efficiency number the founder will read moved by 0.3 pp.

## D-022 - PF, kVA and the voltage ceiling are cycle quantities too (2026-10-23)

**Finding.** `dq_model.pf_check` evaluates PF at a single rotor angle, with the
torque of that same angle in the numerator. A sweep over one 30 deg mechanical
period (`pf_cycle.py`, 15 points, J=5.21) shows that the torque swings over that
period while the apparent power does not follow it down. Power factor therefore
carries the same peak-angle bias that D-018/D-021 found in mean torque and D-020 in
efficiency - the third instance of one error class.

| | quoted | cycle basis |
|---|---|---|
| PF (rail-sizing, mean P / max S) | 0.578 | **0.39 - 0.43** |
| PF (mean P / mean S) | 0.578 | 0.41 - 0.57 |
| S over the period | 1.06 kVA | 0.93 - 1.00 kVA (Faraday route) |
| V-hat at 3000 rpm, k=2 | 11.5 V | **12.5 - 14.0 V** |
| speed ceiling at 26.3 V | ~6,840 rpm | **5,200 - 6,300 rpm** |

**Decision 1.** Quote PF on a cycle basis, with the basis named. The rail-sizing
definition (mean real power over the largest apparent power in the period) is the
conservative one and is the default: **PF 0.40 (0.39 - 0.43)**.

**Decision 2.** Keep 1.06 kVA as the apparent-power sizing figure. S is turns-
invariant and, on the Faraday route, nearly angle-invariant (3.5% band), so the rail
budget does not change. What changes is the real power it buys: 409 W in for 387 W
of shaft, where the point PF implied ~556 W of shaft.

**Decision 3.** Restate the voltage ceiling as a bracket, 5,200 - 6,300 rpm, and
retire the 11.5 V point value. That value belongs to the superseded 0.86 kVA /
0.633 PF triplet; the current state recomputes to 12.5 - 14.0 V. Consequence for
D-020: the 65.5 mm stack route is worth roughly 4,000 - 4,800 rpm, not 5,260, and
any gear-ratio commitment should be made against the bracket.

**Decision 4.** D-017's conclusion is unaffected. S6 beats the baseline at equal
angle and current, and both numbers carry the same bias, so the like-for-like
comparison holds; only its absolute values are superseded.

**Loading anchor (new, independent of the PF question).** At the certified point the
air-gap shear is **0.89 kPa mean / 1.30 kPa peak** over a 669 cm3 rotor, against the
"a few kPa" band for small machines (Kirtley, MIT 6.685 ch.1) and the 3 - 7 kPa a
0.1 - 5 kW induction machine normally reaches. At 5.21 A/mm2 the winding sits at the
top of the normal TEFC range. The machine is **magnetically under-loaded and
electrically normal**: the iron is not the constraint, the 48 V rail is. This is an
independent argument for D-020's stack-length route over its current route.

**Reference band for PF (sourced).** Measured small SynRMs give 0.60 - 0.65
(Ozcelik et al., Energies 12(11):2190 Table 18: 0.647 / 0.60 / 0.60 at 2.2 / 4 /
5.5 kW) against 0.78 - 0.79 for the induction machines on the same stators; ABB
ACH550-PHPB11U-EN quotes 0.64 at 2 HP. Our 0.39 - 0.43 is far below that, which is
what a saliency ratio near 4 (8/6) rather than 7 - 14 would predict. The comparison
is not like-for-like in loading and is flagged as directional only.

**Open.** The 33% disagreement between the two V-hat routes (phase linkages vs
torque-implied) is now the dominant uncertainty on the ceiling and on the PF
bracket. It has been open since D-012 addendum 7 and is interpretation-limited; a
co-energy solve at two current levels would bound it.
