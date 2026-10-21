# PLAN — envelope point design (110-140 mm bore), declared before running

**Script:** `simulation/scripts/envelope_point_design.py`.
**Basis:** validated 150 mm-bore frame, `.../envelope_validation/RESULT.md`.

## Question

What is the **smallest** self-similar 4-pole frame that holds **>= 1.6 N.m continuous at
J = 6 A/mm2** with **>= 25% margin** (i.e. >= 2.0 N.m @ 74 mm-equivalent), at 3000 rpm /
48 V, and stays windable?

## Method (declared)

- Geometry self-similar to the validated 150 mm frame: stator OD = 1.4467 x bore,
  shaft = 0.26 x bore, barrier span = 0.08 x bore, frac 0.62, nb 2, bridge 0.6 mm,
  airgap 0.52 mm, 36 slots. Only the bore changes.
- The 2D solve is stack-length independent: screen bores {100, 110, 120, 130, 140} mm
  at 1536/rows4, delta = 26.25 deg (the validated peak angle).
- For each bore: required stack for 2.0 N.m and for 1.6 N.m = target / (T/m).
  Windability from the same winding model as `envelope_sizing.py`
  (N_c = a * N_ph / n_coils, a in {1,2,4,6}).
- The chosen bore is then certified at 3072 rays, rows 4/20/40.

## Declared prediction

From the measured exponent (T/m ~ D^4.13 at the 150 mm point = 68.49 N.m/m):

| bore | predicted T/m | stack for 2.0 N.m |
|---|---|---|
| 110 mm | 18.4 | ~109 mm (rejected: too long) |
| 120 mm | 26.0 | ~77 mm (borderline) |
| 130 mm | 37.9 | ~53 mm (expected pick) |

## Pass criteria

- **P1:** chosen frame holds >= 2.0 N.m at a stack <= 74 mm and is windable (a <= 6,
  4 <= N_c <= 20).
- **P2:** certification rows4->rows40 drift <= 15% (this frame family showed +7.2%;
  the anchor frame was -2.2%).
- **P3:** report the smallest candidate meeting P1 with its own rows40 number and
  extractor name; do not mix with the 150 mm result.

## Interpretation rule

If the rows40 value at the chosen bore falls below 2.0 N.m, step to the next bore up.
If the rows sequence is non-monotone again, record the range and keep the number
INDICATIVE -- no spec freeze on an uncertified extraction.
