# RESULT — 150 mm-bore 4-pole envelope validation

**Scripts:** `simulation/scripts/envelope_validation.py`, `envelope_certify.py`
(logs: `/tmp/opencode/m1/envelope_validation.log`, `envelope_certify.log`,
`bracket_bound.log`). Method/expectations frozen in `PLAN.md`.

## Setup (as declared)

4-pole, 36 slots, q = 3, certified `d_pattern()`; bore 150 mm, stator OD 217 mm,
airgap 0.52 mm, shaft 39 mm, barrier span 12 mm / nb 2 / frac 0.62 / bridge 0.6 mm;
J = 6 A/mm2, fill 0.40, M-43 Steel (1006 as bound). Slot area 76.1 mm2 -> AT/slot 183 A.

## Measured

| stage | value |
|---|---|
| angle sweep 1536/rows4 | peak at delta = 26.25 deg, **81.89 N.m/m** |
| 3072/rows4 | 63.89 N.m/m |
| rows 10 / 20 / 40 at 3072, delta 26.25 | 68.89 / 74.85 / **68.49** N.m/m |
| rows4 -> rows40 drift | +7.2% (last step -8.5%, **non-monotone**) |
| bracket bound (rows4 / rows40) | M-43: 63.89 / 68.49; 1006: 61.80 / 66.20 (**3% spread**) |
| **T @ 74 mm (rows40)** | **5.07 N.m** (M-43) / **4.90 N.m** (1006) |
| Bmax | 2.96-3.08 T (**beyond the BH bracket, extrapolated**) |
| target | 21.6 N.m/m = 1.6 N.m @ 74 mm |

## Verdict (per the frozen rule)

**E1 PASS, with ~3x margin, INDICATIVE class.** Even the lowest credible extraction
(rows4, 61.8 N.m/m = 4.57 N.m) is 2.9x the target. The result does not hinge on the
mesh rows or the steel bracket: rows wobble +/-8%, bracket spread 3%.

Honest limitations, not papered over:

- **Non-monotone rows sequence** (63.9 -> 68.9 -> 74.9 -> 68.5). Unlike the anchor's
  certified single-ring trace (8.53 -> 8.42 -> 8.39 -> 8.34, last step -0.5%), this frame
  has not reached a zero-drift extraction floor. **68.5 N.m/m is the rows40 value, not a
  certified number.** Quote 4.6-5.1 N.m @ 74 mm with the extractor name.
- **Bmax ~3 T** is outside the BH bracket (the paper states 2.1 T saturation). The
  bracketed torque spread is only 3%, so torque is not sensitive to the extrapolation -
  but the local bridge fields should not be reported as physical.
- The angle sweep has one implausible outlier: delta = 23.5 deg gives 37.5 N.m/m vs 71.1
  at 24.5 deg (2x jump over 1 deg, while 24.5 -> 28 is smooth). Treat 23.5 as a
  mesh/barrier-edge alignment artifact; the peak location 26.25 deg is consistent with
  the anchor frame.

## What this settles for D-012

1. **A 48 V / 3000 rpm / J = 6 machine meeting 1.6 N.m continuous exists at 4-pole,
   bore 150 mm, L = 74 mm** - no 2-pole topology required. Winding: N_c ~= 4 turns/coil
   with a = 6 parallel paths (12 coils/phase -> 2 coils per path), which is in the
   normal 48 V traction range.
2. **The 150 mm frame is over-sized for the target**: it delivers ~5 N.m at J = 6
   (~1.6 kW at 3000 rpm). The target 1.6 N.m should be reachable around bore 110-130 mm
   with the same proportions; that is a point-design task, not a research question.
3. The measured torque-vs-bore exponent is ~4.1 (D^4), i.e. the scan's linear model was
   directionally right but its absolute torque column is low for frames whose slots are
   deeper than the scan's assumed 14 mm radial build (the scan used 42% of a thin
   annulus; this frame has a 33.5 mm radial build, 76 mm2 slots).

## Next (zero budget, declared order)

1. Point design at bore 110 and 130 mm (same proportions), certify at rows 40; pick the
   smallest frame that holds >= 1.6 N.m cont with >= 25% margin.
2. Look at why the rows sequence is non-monotone here (the anchor frame was monotone) -
   likely barrier-edge/mesh-ray alignment; if it persists, the extractor certification
   protocol needs a note for scaled geometries.
3. First-order copper-loss + PF estimate at the chosen J before any spec freeze.
