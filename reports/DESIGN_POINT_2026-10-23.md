# Design point has moved: three things the founder needs to know

**Date:** 2026-10-23 | **Decisions:** D-018, D-019, D-020 | **Spend:** zero

This note is the founder-facing summary of a week that changed the design point, not the
design. Full detail in `STATUS.md`, `DECISIONS.md` D-018/D-019/D-020.

## 1. Torque ripple was real, and it is fixable with skew - not with a redesign

Earlier work established a ~100% peak-to-peak torque modulation and read it as a
winding-layout problem, which would have meant redesigning the stator. A harmonic fit of
the measured curve shows the dominant component is **order 36 - once per slot pitch** - at
3.2x the winding order. The baseline 2-barrier rotor reproduces the same dips at the same
rotor angles and the same depth, so the effect is stator-side: the barriers are not the
mechanism.

A rotor skew of **two slot pitches (20 deg mechanical)** takes peak-to-peak from 107.2% to
**12.9% in-model, inside the 15% gate**, for an estimated **2% mean-torque** cost. One slot
pitch gives 23.1% and does not pass; 15 deg is *worse* than 10 deg, because skew must be an
integer number of slot pitches.

What this buys: the ripple risk no longer justifies a stator redesign. What it costs: a
lamination-stacking decision (skewed stacking, or a skewed key), which is a tooling
question rather than a design one.

## 2. Efficiency is 90.6%, not 93.2%

A synchronous-frame drive holds current constant over a revolution, so copper loss is
constant while torque is not. Energy-average efficiency is therefore set by the **mean**
torque. The previously quoted 93.2% used the peak-angle torque with the same losses, which
is the same peak-versus-mean error that produced the 1.77 N.m figure. The correct number is
**90.6%** (mean 1.2305 N.m at J = 5.21 A/mm2). 93.2% survives only as a peak-angle figure,
labelled as such.

## 3. The 1.6 N.m target is 30% short, and the cheapest fix is a longer stack

Mean torque at the certified current is 1.2305 N.m. Two ways to reach 1.6 N.m:

| | current route | stack route (recommended) |
|---|---|---|
| what changes | J 5.21 -> 6.77 A/mm2 | stack 50.4 -> **65.5 mm** |
| copper loss | 38.5 W | **25.8 W** |
| efficiency | 90.2% | **91.4%** |
| apparent power, rail-sizing | 1.32 kVA | **1.29 kVA** |
| speed ceiling | 5,200-6,300 rpm | **~4,500 rpm** (bracket 4,000-4,800) |
| cycle-basis power factor | ~0.41 | ~0.41 |

The stack route buys 1.2 pp of efficiency and 12.7 W of copper loss, and pays ~24% of the
speed range. **It does not buy apparent power** (D-023): S per N.m is fixed by speed, power
factor and efficiency, so both routes cost ~1.3 kVA for 1.6 N.m. Torque is exactly
proportional to stack length in the model, so the torque estimate needs no new solve. Copper
loss grows 13.5% rather than 30% because the end windings do not stretch (MTL = 2L + 1.2
tau_p) - this corrects the 31 W / 90.6% / 1.06 kVA row in the earlier version of this memo.

**Correction added after this memo (D-022).** The ceiling figures above were built on a
11.5 V terminal voltage that belonged to a superseded state; the machine's own flux
solution gives 12.5-14.0 V at 3000 rpm, which puts the ceiling at 5,200-6,300 rpm before
any stack change (5,900 above is the top of that bracket, 4,500 the stack route). Two
further consequences, both adverse but bounded:

- The quoted PF of 0.578 is a peak-angle value. On a cycle basis it is **0.40**, so ~1.0
  kVA buys **387 W** of shaft, not 556 W. The rail budget in question 3 below does not
  change; the work it delivers does.
- **The kVA for 1.6 N.m is ~1.3 kVA, not 1.06 (D-023).** Stack length scales torque and
  flux together, so it cannot reduce apparent power per N.m; both routes pay ~1.3 kVA.
  What the stack route actually buys is 1.2 pp of efficiency (91.4% vs 90.2%), against
  ~24% of the speed range.
- The air-gap shear is **0.89 kPa** against the "a few kPa" usual for a machine this size,
  i.e. the rotor is magnetically under-loaded and the 48 V rail, not the iron, is the
  binding constraint. This is why the stack route beats the current route: the iron is
  free, the current is not.

## Decision needed from the founder

1. **Is a 65.5 mm stack acceptable** in the target envelope? This is the only question that
   determines which route is taken.
2. **Is a ~4,500 rpm voltage ceiling acceptable** for a 3000 rpm nominal machine? (Was
   quoted as ~5,260 before D-022; the honest bracket is 4,000-4,800 rpm for the stack
   route, 5,200-6,300 rpm at 50.4 mm. This is the question most likely to change the
   answer, because it interacts with the gear ratio.)
3. **Is the 48 V rail able to carry ~1.3 kVA at PF ~0.41** at the chosen thermal design? This
   is the number for the 1.6 N.m target, and it is ~25% more apparent power than the 1.06 kVA
   in the earlier version of this memo. It is the same for both routes (D-023), so it does
   not decide between them - but it does decide whether 48 V can deliver 1.6 N.m at all.

If stack length is capped by the application, the current route is the fallback and the
efficiency figure drops to 89.9%.

## What is still not proven

- **No bench, no experimental evidence** (D-009). Every number here is a 2D
  current-source model: no skew in the field solve, no PWM, no end effects.
- The ripple *magnitude* is plausibly 2-4x high in-model (unskewed, sharp-edged 2D slots).
  The skew result is the quantitative version of that caveat: it is the missing physics.
- Rotor slot-harmonic loss (~1800 Hz) is bounded at 0.8-3.3 W but not modelled.
- Rotor punching tooling and BOM quotes remain F-class spend, founder-gated.

## Correction since the first draft of this note

The mean torque and peak-to-peak were first taken on a 2 deg grid (1.1918 N.m, 96.6%). A
0.5 deg rescan showed that grid reads the mean 3.2% low, because its five samples per slot
period land on the flanks of the narrow torque notches. The corrected values (1.2305 N.m,
107.2%) are used throughout this note; the conclusions are unchanged and the gate margin on
skew is 2 pp thinner than first written. See D-021.

No money was spent to produce this note.
