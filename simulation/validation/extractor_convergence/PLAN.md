# PLAN — extractor-convergence study (gap-row disretization)

**Declared before running, frozen.** Script: `simulation/scripts/gate_c_gap_rows.py`.

## Question

D-011: single-ring and 9-ring Maxwell torque extractors disagree +25–30% on the SAME
solution at deep saturation (SynRM geometry). Probe: is the spread driven by airgap
disretization? Solve the D-010 baseline config (12/0.62/0.6 mm @ δ=26.25°) at 3072 rays
with `n_gap_rows` ∈ {4, 10, 20} and extract BOTH ways per solution.

Optional second config (winner 20/0.70/0.4 @ 32.5°) if the first materializes.

## Frozen evaluation rules (E1–E3)

- **E1 convergence:** every solve conv=True.
- **E2 mesh sanity:** area error ≤1% each mesh.
- **E3 standardization rule:** at the highest affordable rows level, if the
  single-vs-multi spread is **≤15%** → declare a converged absolute torque for that
  config as the mean of the two extractors with ±(spread/2) label, and the study
  PASSES (campaign absolutes may be relabelled afterwards). Otherwise the study
  FAILS per rule and only the *trend* is recorded: per-extractor change
  (rows 4 → 10 → 20) and whether each appears to converge, with no adopted standard.
- Honesty clause: whatever the outcome, RESULT.md must state the mesh sizes observed
  and the wall-clock cost — "affordable" is judged on cost at run time, before results
  are seen.

## Amendment 1 (2026-10-21, recorded after the 4/10/20 sweep, before any rows=40 solve)

The {4, 10, 20} sweep showed multi9 drifting non-monotonically (12.15 → 10.83 → 11.33).
One more level, rows=40, is affordable per the honesty clause (rows=20 cost 126 s/solve
at 545k elements; rows=40 bounded to a few minutes). It is recorded here as baseline-only
extra level before running: its purpose is to test whether the multi-ring oscillation
persists and to bound per-extractor drift one more octet. The E3 rule and its verdict
language are unchanged.
