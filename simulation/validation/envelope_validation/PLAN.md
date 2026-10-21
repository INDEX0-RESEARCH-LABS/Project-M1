# PLAN — envelope validation at 150 mm bore (4-pole fallback), declared before running

**Script:** `simulation/scripts/envelope_validation.py`.

## Why

The revised D-012 sizing scan (ESTIMATE, T ~ D^4 from slot-AT scaling) says a 4-pole frame
with bore ~150 mm and L = 74 mm reaches the 1.6 N.m continuous target at J = 6 A/mm2.
That D^4 scaling is optimistic once saturation caps Bhat. Before the number enters any
spec decision, one real solve must confirm it on the actual barrier topology.

## Setup (declared)

- 4-pole, 36 slots, q = 3, same winding pattern as the certified anchor (`d_pattern()`).
- bore 150 mm, stator OD 217 mm (anchor radial-build ratio), airgap 0.52 mm, shaft 39 mm
  (anchor ratio), barrier span 12 mm, nb 2, frac 0.62, bridge 0.6 mm.
- J = 6 A/mm2, fill 0.40, M-43 Steel, slot AT = J*fill*A_slot (no tuning).
- delta sweep {22.5, 26.25, 30} deg at 1536/rows4; best angle re-solved at 3072/rows4.

## Declared expectation and pass criteria

- Scan ESTIMATE at this frame: T_cont = 1.63 N.m @ 74 mm -> **T/m = 22.0**.
- **E1 PASS:** the 3072/rows4 solve at the best delta gives **T/m >= 21.6**
  (= 1.6 N.m / 0.074 m) -> the continuous target is met on real geometry.
- **E2 CLOSE:** 15 <= T/m < 21.6 -> target reachable with a modest L/D increase; record
  the measured scaling exponent (T vs D) instead of assuming D^4.
- **E3 FAIL:** T/m < 15 -> the D^4 estimate is materially optimistic; the frame must grow
  further and the scan's torque column gets an explicit correction factor.
- All solves must converge; region areas <= 1%; Bmax reported (saturation audit).

## Interpretation rule

Whatever E1/E2/E3 lands, the measured T/m - not the linear model - becomes the number
quoted for this frame, with the extractor name (single-ring, 3072/rows4, rows=40 not run
here so the number is "rows4" class and must be certified at rows=40 before any final
commitment).
