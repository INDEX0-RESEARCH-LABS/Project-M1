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
