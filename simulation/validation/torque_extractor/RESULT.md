# RESULT - torque extractor: 1.592 -> 1.45 N.m (-9%), with a band

Log: `/tmp/opencode/m1/torque_mesh.log`. Gates: `PLAN.md` (fixed before the run).
Commit order: script + gates, then run, then this file.

## 1. What was found

Torque at the certified operating point (delta = 26.25 deg, J = 5.34 A/mm2) is
**not converged at 1.592 N.m**. The value depends on where the Maxwell-stress circle is
sampled and on the mesh:

| mesh (rays / gap rows) | rings = 1 | rings = 5 | rings = 9 | ring effect |
|---|---|---|---|---|
| 1536 / 4 (certified mesh) | **1.592** | 1.518 | 1.412 | -11.3% |
| 3072 / 10 | 1.472 | 1.568 | 1.507 | +2.3% |
| 4096 / 10 | 1.461 | 1.499 | 1.436 | -1.7% |

`rings` averages the stress integral over several radii inside the 0.52 mm airgap.
The solver's B is element-wise constant, so a single sampling radius sits on whichever
element it lands in; the exact integral is radius-independent in a current-free annulus,
so the ring average is the better quadrature. At the coarse mesh the single-circle answer
is the **highest** of the nine, i.e. the certified 1.592 N.m was a high-side sample.

Independent route: co-energy `dW'/d(delta)` at 3072 / 10 gives **1.399 N.m**, 7.1% below
the Maxwell ring average (1.507) at the same mesh.

## 2. Gates

- **E1 convergence (3%)**: as written, PASS (+1.7% finest-vs-coarsest at rings = 9).
  **This gate was badly designed** and the pass is not evidence: it compared two single
  noisy samples whose own scatter is +/-5%. The correct statistic is the ring scatter,
  which is **11%** at the coarse mesh and 2-5% at the finer ones. Recorded as written,
  then overruled by E2/E3. Same pattern as the F4 note in `iron_loss/RESULT.md`.
- **E2 ring averaging (>3%)**: **FAIL at the coarse mesh (-11.3%)** -> the single-circle
  value is superseded. Any future absolute torque must be ring-averaged.
- **E3 arbitration**: Maxwell 1.507 vs co-energy 1.399 -> 7.1% apart, inside the 10%
  allowance. **Adopted: 1.45 N.m, band 1.40-1.51 (+/-4%).** Correction **-9%**
  (range -5% to -12%).
- **E4 consequence**: T(J=6) ring-averaged, 3072/10 = **1.920 N.m** against the declared
  2.00 N.m margin point -> **the 25% envelope margin does not hold at J=6**; the margin
  is **+20%**. Stated in `STATUS.md` in the same commit.

## 3. Consequences at the 1.6 N.m target (all DERIVED from the adopted torque)

`T ~ J^2` (measured exponent 1.9-2.0 on the three certified current levels), so the same
torque now needs more current. Two honest responses, and the choice is a product decision:

| | hold the 1.6 N.m target | hold the 51 A winding current |
|---|---|---|
| shaft power | 500 W | **454 W** (-9%) |
| current density | **5.62 A/mm2** | 5.34 |
| phase current (k=2) | **53.7 A** | 51.0 A |
| copper loss | **26-28 W** | 24-26 W |
| efficiency (with iron) | **92.3%** (was 92.7%) | 92.1% |
| terminal voltage @3000 rpm | **13.5 V** | 12.9 V |
| speed ceiling, no FW | **~5,860 rpm** (was ~6,130) | ~6,130 rpm |
| apparent power | **~1.09 kVA** | ~0.99 kVA |
| PF | **~0.49-0.54** | 0.53-0.58 |

The PF drop in the left column is not a modelling change: holding torque on a weaker
estimate raises both V and I, so S rises while shaft power stays fixed. **The founder
decision (D-012) therefore faces a 1.0-1.1 kVA bracket, not 0.99 kVA**, and D-013's
6,130 rpm ceiling becomes ~5,860 rpm at the target torque - still above the 5,600 rpm
operating point, but with only ~4% envelope left.

## 4. What this does and does not invalidate

**Does not change:**
- the frame choice (bore selection was torque-per-stack, a ratio that shares the bias),
- SRM vs SynRM (extractor-consistent ratio, D-008),
- the thermal conclusion (rise scales with copper loss, still <20 K),
- iron loss (volume integral of B^n, far less sensitive to gap sampling than a surface
  integral - but this is reasoning, not a measurement),
- the qualitative blocker: PF/current at 48 V.

**Does change:** every absolute torque, current, PF and kVA figure, including the ones in
`winding_spec_v1.md` and `STATUS.md`. They are restated from the adopted value, not
re-derived by hand.

## 5. Open, with the fix named

1. **Extractor standard.** Ring-averaged torque (`n_rings = 9`, rows >= 10) becomes the
   rule for any quotable absolute torque; the single-circle call in `dq_model.py`,
   `rajini_anchor.py` and `envelope_point_design.py` is the source of the bias.
2. **True MTPA angle.** The angle sweep is too noisy to locate it (next section), so
   26.25 deg is retained as the operating point, not because it is proven optimal.
3. **Residual band.** +/-4% after arbitration. A single fully converged point
   (4096 rays / 20 rows / rings 9, plus co-energy at the same mesh) would tighten it; it
   is ~15 min of compute and is the cheapest way to restore a quotable point value.
4. **State-jumping hypothesis.** The angle sweep's 40% swings are too large for sampling
   noise alone. A saturated Picard solve started from zero at each angle can land on a
   different flux pattern. Untested; the fix would be continuation (start each angle from
   the previous solution) - not implemented.
