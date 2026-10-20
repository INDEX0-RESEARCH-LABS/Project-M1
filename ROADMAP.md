# Roadmap — Phase 0 → prototype (2026-11-12)

Dates are planning targets. Every gate is pass/fail; failure triggers a documented revision in
`DECISIONS.md`, not silent slippage.

| Gate | Window | Deliverables | Pass criteria | Tranche |
|---|---|---|---|---|
| **A. Feasibility** | Week 1–2 | Literature review (≥30 verified sources), research matrix, 3 evidence-backed hypotheses, architecture comparison | Sources verified (DOI/URL real); no inaccessible source claimed as read | Milestone A |
| **B. Baseline** | Week 3–5 | Baseline selection matrix, target spec v0, working FEMM/Elmer model, mesh-convergence study, comparison vs published reference | Model reproduces a published reference case within a stated tolerance | Milestone B |
| **C. Opportunity** | Week 6–9 | Optimization loop running on baseline, ≥1 candidate design beating baseline on a stated metric, independent re-check of the winner | Winner re-verified with a model/run not used to search it | Milestone C |
| **D. Prototype eng.** | Week 9–12 | Drawings, rotor stress check, winding spec, BOM with quotes, test plan, safety review | Design review signed off by a qualified reviewer (external if needed) | Milestone D |
| **E. Build & test** | Week 12–15 | Manufactured prototype, calibrated instrumentation, test results vs acceptance criteria | 5-point success definition in `PROJECT_CHARTER.md` met or falsified honestly | Milestone E |
| **F. Scale readout** | Post-test | Application fit for 2W/3W, cost model, investor brief separating measured/projected/assumed | Independent lab data available | Milestone F |

## Seven-day execution checklist (from today)

- [x] Day 0 — Inspect environment, create workspace, init version control, Python env
- [x] Day 1 — Literature search pass 1 (SRM, SynRM, 2W/3W India context); fill `research/research_matrix.csv`
- [x] Day 2 — Literature pass 2 (torque ripple, control, thermal, AI-optimization); `bibliography.bib`
- [x] Day 3 — Prior-art pass (Google Patents / PATENTSCOPE); `ip/patent_search_log.md` (landed in `research/prior_art.md`)
- [x] Day 4 — Architecture comparison matrix scored; baseline shortlist (SynRM provisional, founder approval pending)
- [ ] Day 5 — Toolchain: attempt FEMM/OpenFemm install; record blockers honestly
- [ ] Day 6 — Baseline geometry + first mesh (even if unsolved/incomplete); mesh plan
- [ ] Day 7 — Gate A review: hypotheses, gaps, smallest credible experiment defined

## Smallest scientifically credible experiment (preview)

Before any prototype: build a 2D FEM model of one candidate architecture, run a mesh-convergence
study, and reproduce one *published* torque-vs-current or flux-vs-current curve from an independent
source within a declared tolerance. If that cannot be reproduced, no optimization result is
trustworthy. Full definition lands in `requirements/acceptance_criteria.md` at Gate B.
