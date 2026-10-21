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
