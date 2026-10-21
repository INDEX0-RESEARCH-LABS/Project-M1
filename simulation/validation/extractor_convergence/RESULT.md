# Extractor-convergence study — RESULT

Status: **E1/E2 PASS — E3 FAIL (per frozen rule), with decisive findings.**
Script: `simulation/scripts/gate_c_gap_rows.py`; runs `gate_c_gap_rows.log`,
`gate_c_gap_rows40.log` (copied here). Config: D-010 baseline (12/0.62/0.6 mm @
δ=26.25°), 3072 rays, `n_gap_rows` sweep; winner config ran once at rows=20.

## Data

| rows | T single-ring | T multi9-ring | spread | elements | solve time |
|---|---|---|---|---|---|
| 4 | 8.5265 | 12.1487 | +29.8% | 339k | 71 s |
| 10 | 8.4170 | 10.8270 | +22.3% | 416k | 95 s |
| 20 | 8.3872 | 11.3287 | +26.0% | 545k | 126 s |
| 40 (amendment 1) | 8.3414 | **6.1021** | **−36.7%** | 803k | 258 s |
| winner @20 | 9.0056 | 10.7896 | +16.5% | 545k | 139 s |

## Frozen-rule verdicts

- **E1 all converge:** ✅ every solve conv=True.
- **E2 areas ≤1%:** ✅ 0.107% at every level.
- **E3 standardization rule:** ❌ spread 26% (and then −37%) vs the ≤15% rule — no
  campaign standard adopted via the mean-form. Recorded exactly.

## Findings (evidence, not gate-editing)

1. **single-ring passes mesh-convergence certification.** Monotone over the whole
   4→40 sweep, −2.2% total, last step −0.5% — text-book convergence. Winner config
   agrees (9.2534 @4 → 9.0056 @20, −2.7%).
2. **multi9 fails certification decisively.** Non-monotone with a −46% swing between
   adjacent levels (12.15 → 10.83 → 11.33 → 6.10). At saturated SynRM gaps the 9-ring
   estimator does not have a defensible value at ANY rows level measured.
3. **Reframe of the Gate C C4 mystery:** the recorded "+25–30% single-vs-multi spread"
   was not symmetric estimator doubt — it was one certifiable extractor vs one
   uncertified one. The multi-ring upper numbers are not real; there is no multi9
   "truth" to converge to among the sampled values.
4. **Certified absolute (this geometry class):** SynRM baseline torque ≈ **8.34 N·m/m**
   (single-ring @ 3072/40; remaining self-convergence ≈0.5%). This carries the
   campaign's other labels (M-43 steel band, INDICATIVE anchor label) unchanged.
5. **Cross-machine consequence:** `srm_synrm_compare` C1 — the single-extractor ratio
   **0.44** is the certified number; the multi column (0.33) is downgraded to
   "uncertified" (formally same-extractor, but against an estimator later shown
   uncertifiable on the SynRM side). The ±25% band claim survives: 0.44
   sits inside it and is now the supported point.
6. **SRM usage of multi9 remains valid:** SRM's own multi vs single agreement at rows4
   was +0.6% (smooth open-slot gap) — the estimator is fine where the gap field is
   smooth; the certification failure is specific to steep saturated gap features
   (barrier corners/bridges).

## Cost record (for the honesty clause of the PLAN)

71–258 s per solve, 339k–803k elements, all single-machine local runs; affordability
judged per rule at the rows=20 stage, amendment to rows=40 recorded in PLAN before run.
