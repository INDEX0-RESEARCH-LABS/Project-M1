# Project M1 — Phase 0 simulation & validation: freeze summary

**Date:** 2026-10-21 (final validation landing: `98d8f65`)
**Scope frozen here:** Gates A + B + C of `ROADMAP.md` — everything achievable with zero
budget and in-house simulation (D-009). Nothing below carries a purchase-dependent claim.

## What was promised → what was delivered

| Roadmap gate | Promise | Status |
|---|---|---|
| A. Feasibility | ≥30 verified sources, matrix, 3 falsifiable hypotheses, architecture comparison | ✅ 72 verified sources; HY-1/2/3; SRM-vs-SynRM scored matrix |
| B. Baseline | Working model + mesh convergence + **reproduce a published reference within a stated tolerance** | ✅ Full validation chain (analytic → nonlinear toroid → xfemm v3.0 cross-check); 23/23 tests green. The published-reference reproduction is **envelope-level only** (D-007/D-009: anchor geometry never published; absolute labels INDICATIVE ±25%) |
| C. Opportunity | Optimization loop + winner **independently re-verified** | ✅ machinery / ❌ declared +10% improvement gate fail — recorded honestly (D-011), no winner claimed |
| D–F | Prototype eng., build & test, scale readout | **open — budget-gated**, see Decision point below |

## The standing result chain (all numbers labelled)

| Finding | Verdict | Label |
|---|---|---|
| Solver chain valid (linear, nonlinear, xfemm parity) | 23/23 tests | CONFIRMED |
| SRM 12/8 loses to SynRM at equal Cu/J/fill | ratio **0.44 (single-extractor) / 0.33 (multi-extractor)**; SRM side extractor-robust (+0.6%) | RATIO-based, same-extractor both sides — strongest claim in the campaign; D-008 robust |
| Rajini anchor: our committed layout hits 7.5–8.5 N·m/m vs anchor-implied ~108 ×12.7 gap | excitation-level design discrepancy | INDICATIVE ±25% (final for Phase 0) |
| Barrier-rotor family ceiling | ~9.2–9.5 N·m/m @1536 (single-ring); +1–9% over v1 baseline best config | same-extractor deltas only |
| Absolute torque scale | **resolved by certification** (extractor study): single-ring certified the campaign standard for saturated SynRM gaps (8.34 N·m/m @ 3072/40); multi9-ring uncertifiable there (−46% swing), still fine on smooth gaps (SRM +0.6%) | CLOSED by `validation/extractor_convergence/RESULT.md` |

**Effective honesty rules (permanent):**
1. Only same-extractor ratios are quotable across machines/configurations.
2. Absolute N·m/m numbers carry their extractor name; on saturated SynRM gaps use
   single-ring (certified mesh-converged) — multi9-ring is uncertified there.
3. No purchase, no paid bench (D-009); anchor comparisons stay INDICATIVE ±25% (final for Phase 0).

## Open items at freeze

1. **Torque-extractor standardization** — RESOLVED as *certification asymmetry* by the
   post-freeze `validation/extractor_convergence/` study: single-ring is
   mesh-converged (−2.2% over a 10× gap-row refinement), multi9 fails certification.
   No relabelling of campaign numbers was needed — SynRM absolutes were already
   single-ring; the certified SRM/SynRM ratio is 0.44 (single-consistent).
2. **D-004 sign-off** — founder paperwork, blocks no work.
3. **Topology lever** (split pole shoes / bridge profiling) — not attempted: Gate C showed
   the barrier family is flat; new family = new phase.

## Decision point owed to the founder (blocks nothing yet)

**Paper freeze** (current): simulation-validation Phase 0 complete, all claims labelled,
report + artifacts + reproducible scripts in-repo → defensible as-is.
**versus** **bootstrap build**: prototype path needs budget outside D-009; the honest
framing is that everything up to Gate D pass criteria is already on paper, whether that
counts is the founder's call, not simulation's.
