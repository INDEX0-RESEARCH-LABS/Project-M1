# Gate C search — RESULT

Status: **declared gates: C1/C2/C3 PASS — C4 FAIL, C5 FAIL.** Script:
`simulation/scripts/gate_c_search.py` (values from `gate_c_search.log`; the search's own
JSON write crashed on a bookkeeping KeyError *after* all verdict prints — script fixed,
values here are from the log, nothing lost). The estimator arbiter:
`simulation/scripts/gate_c_extractor_ab.py`.

## Search outcome

| config | best \|T\| (1536) @ delta |
|---|---|
| span12 / frac0.62 / bridge0.6 (= D-010 baseline) | 8.5816 @ 28.75° |
| span12 / frac0.70 / bridge0.4 | 9.1133 @ 32.50° |
| span16 / frac0.62 / bridge0.4 | 9.2726 @ 28.75° |
| span16 / frac0.70 / bridge0.4 | 9.3750 @ 32.50° |
| span20 / frac0.62 / bridge0.4 | 9.2784 @ 28.75° |
| **span20 / frac0.70 / bridge0.4 (winner)** | **9.5396 @ 32.50°** |

Consistent inner trends: thinner bridge +2–3%; arc 0.70 slightly better; span saturates
beyond 16 mm. The family **saturates around 9.2–9.5 N·m/m (1536, single-ring)**.

## Winner verification (3072 rays, fresh mesh)

- single-ring: **9.2534** (3.0% below the search's 1536 value → C3 PASS)
- multi9-ring: **12.2935** — 24.7% **above** the single-ring value of the same solution

## C4/C5 — the failure and its resolution per the PLAN's honesty clause

The declared C4 gate (multi-ring vs single ≤15%) FAILED at 24.7%. The PLAN forbids
claiming any improvement while estimators disagree materially, so the arbiter script
re-solved **both** the D-010 baseline and the winner at 3072 rays with BOTH extractors:

| | single-ring | multi9-ring | estimator shift |
|---|---|---|---|
| baseline (12/0.62/0.6) @26.25° | 8.5265 | 12.1487 | +29.8% |
| winner (20/0.70/0.4) @32.5° | 9.2534 | 12.2935 | +24.7% |

**Improvement verdict under ONE extractor at a time:**

- single-consistent: **+8.5%**
- multi-consistent: **+1.2%**

Neither reaches the declared **+10% improvement gate → C5 FAIL**. The +25–30%
multi-ring-vs-single-ring discrepancy is roughly *proportional across configs* (it
largely cancels in ratios) — it is an estimator-systematics finding, not a physics
win: the winner's "12.29 N·m/m" must NOT be quoted against single-ring baseline numbers.

## What Gate C actually learned

1. **The barrier family is exhausted.** Every candidate lands within ~+1–9% of the v1
   baseline depending on extractor — below the declared decision threshold and below the
   extractor's own uncertainty. Further barrier tuning is not an optimization lever;
   the next lever is topology (e.g. split/flared pole shoes, bridge profiling), or a
   proper optimization objective that includes iron mass and losses.
2. **The torque extractor's spread (±25–30% between single-ring and 9-ring at deep
   saturation, same solution) is the campaign's dominant *numeric* uncertainty now** —
   it exceeds the R3 mesh-class 7–8% finding and is larger than any improvement any
   candidate in this family offers. The multi-ring averaging was adopted during the SRM
   work to cut noise, but its shift is systematic at these saturation levels. Any
   absolute torque number printed above must carry its extractor label; only
   same-extractor ratios are defensible.
3. **Gate C pass criterion (ROADMAP): not met as declared.** A candidate beat the
   baseline (+8.5% consistent single), but below the frozen +10% decision gate and
   inside the estimator uncertainty band. Declaring a winner on those numbers would be
   exactly the "post-hoc swapping" the PLAN forbids.

## Gates summary

| gate | verdict | value |
|---|---|---|
| C1 all converge | ✅ | 74/74 conv (12–21 iters) |
| C2 areas ≤1% | ✅ | 0.124% max |
| C3 refinement ≤10% | ✅ | 3.0% |
| C4 extractor consistency ≤15% | ❌ | 24.7% |
| C5 improvement ≥+10% | ❌ | +8.5% (single-consistent), +1.2% (multi-consistent) |

## Follow-up declared (next engineering task, this phase's real blocker)

Before any further candidate claims: settle the extractor. Smallest credible step:
a **co-energy torque cross-check** (`T = −∂W′/∂δ` from two converged solutions at
δ ± small) on ONE configuration — if it agrees with one of the two extractors (and it
is mesh-convergent), that extractor becomes the campaign standard, all absolute numbers
are re-labelled, and only then does Gate C re-open with a defensible ±.
