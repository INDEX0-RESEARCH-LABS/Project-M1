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
