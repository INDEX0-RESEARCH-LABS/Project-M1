# PLAN - load torque ripple of the deep-barrier rotor

> **Amendment after execution.** Generation 1 of this plan swept the rotor with the
> current pattern fixed in the stator frame: that measures the static torque-angle
> curve, not ripple, and R3 was never applied to it. Generation 2 advanced the phase
> currents with the rotor (fixed current angle, the correct steady-state model) and
> failed adequacy: R2 disagreed by far more than 2 pp and the model contradicts the
> static curve of the same machine. **No ripple number is quoted.** See `RESULT.md`
> for the numbers and for what would settle it. The gates below are left as declared.

**Declared before running.** Script: `simulation/scripts/torque_ripple.py`.
Logs: `/tmp/opencode/m1/ripple_{a,b}.log`, CSV `/tmp/opencode/m1/ripple_{a,b}.csv`.
Geometry: D-014 S6 (4 barriers, span 44.5 mm, rib 0.25, bridge 0.6 mm), J = 5.21 A/mm2.

## What is being measured, and what is not

A SynRM has no permanent magnets, so there is **no cogging torque**. At zero current the
torque is zero at every angle. All ripple is load ripple: stator mmf space harmonics
interacting with the rotor anisotropy. That is why the sweep runs at the operating
current (J = 5.21), not at no-load.

This is a **shape** study. The extractor is the certified coarse mesh (1536 rays / 4 gap
rows, rings 5), whose absolute torque carries the known -9% bias. The ripple *fraction*
and the harmonic orders are the outputs; absolute torque is not quoted from here.

Method: rotor angle swept 0-20 deg mechanical in 0.5 deg steps, in two parallel halves.
0.5 deg resolves mechanical orders up to 180, so the 36th (one slot pitch = 10 deg) is
resolved with 20 samples/period. The window covers two slot periods, which gives the
periodicity check.

## Frozen gates

- **R1 no absolute claims**: only the ripple fraction and harmonic orders are quoted.
- **R2 adequacy**: the two 10 deg windows must agree in peak-to-peak fraction within
  **2 percentage points**. If they do not, the sampling or the extractor is not good
  enough and the number is not reported.
- **R3 decision rule**: at the target current, **<= 10% p-p = PASS** (acceptable for a
  2W traction motor), **10-15% = MARGINAL** (needs skew or a barrier-end chamfer before
  it can be called quiet), **> 15% = FAIL** (rotor/stator combination needs rework).
- **R4 extremum validation**: the three largest local extrema found by the coarse sweep
  are re-solved at 3072 rays / 10 gap rows, rings 9. The p-p must reproduce within
  **2 percentage points**, otherwise the coarse sweep over-states or under-states it.
- **R5 harmonic diagnosis**: report the dominant mechanical order. Slot order (36) means
  the lever is slot opening or skew; a low order (2/4/6) means the lever is barrier
  shape or the winding layout.

## Known limitations

- Current-source excitation, not a PWM voltage-source drive. Ripple from current
  harmonics is a controller question and is not modelled.
- No skew, no rotor eccentricity, no manufacturing tolerance.
- NVH is not predicted: torque ripple is a necessary input, not a sound level.

## Gen 3 amendment (declared before running)

Gen 1 sampled the static curve at 5 deg. A ~10 deg modulation cannot be represented at
5 deg sampling (two samples per period), so the "order-12 = 2.4%" fit in `RESULT.md` s.3
is an aliasing artefact and is withdrawn as evidence that ripple is small. That removes
the stated reason why Gen 1 and Gen 2 "cannot both be right".

What changes in Gen 3: the D-016 gap **area integral** replaces the ring average as the
measured quantity (rings 1/5/9 are still written for continuity), the window is 15.0-37.5
deg at 0.5 deg (22.5 deg = two observed dip spacings), and the current angle is pinned at
`DELTA_OP = 26.0`. Script `torque_ripple.py`, log `/tmp/opencode/m1/ripple_gen3.log`,
CSV `/tmp/opencode/m1/ripple_gen3.csv`.

Frozen gates:

- **R1 unchanged**: ripple fraction and orders only, no absolute torque claim.
- **R2' adequacy**: the two 11.25 deg end windows must agree in p-p within 2.0 pp, the
  median annulus band spread must be < 10% and its maximum < 20%. Either failing means no
  number is quoted.
- **R3 unchanged**: <= 10% p-p PASS, 10-15% MARGINAL, > 15% FAIL.
- **R4' extremum validation**: the three largest local extrema re-solved at 3072 rays /
  10 gap rows must reproduce the p-p within 2 pp.
- **R5 unchanged**: report the dominant mechanical order (slot order 36 -> slot opening or
  skew is the lever; low order 2-6 -> barrier shape is the lever).
- **R6 reconciliation (new)**: the synchronized p-p in the window centred on 26 deg
  (20.375-31.625) is compared with the static 0.25 deg sweep's p-p over the same window,
  where the envelope slope is near zero. Ratio outside **0.5-2.0** means the two
  excitation models still disagree and ripple stays unquoted. Inside means the Gen 1 vs
  Gen 2 discrepancy was sampling, and the static record is corrected.

Prediction, stated so it can fail: if the modulation is a real slot-locked torque, R6
lands inside 0.5-2.0 and R3 returns FAIL (> 15%), because the static dips alone are
14-29% of the local envelope.

## Post-result note (not a gate change; added 2026-10-23)

R5's frozen rule ("slot order 36 means the lever is slot opening or skew; a low order means
barrier shape or winding layout") was written to discriminate between mechanisms, and the
measurement did answer it, but the answer was not one of the two branches: **order 36
dominates at 0.495 N.m while order 12 is present at 0.157 N.m, so both levers are real and
they rank in that order.** R5 is therefore recorded as *answered, mapping incomplete* - not
as a failed gate. The gates R1-R6 and the R2'/R4'/R6 thresholds above were not changed
after the fact.
