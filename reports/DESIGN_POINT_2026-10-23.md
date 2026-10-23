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
| copper loss | 40 W | **31 W** |
| efficiency | 89.9% | **90.6%** |
| apparent power | **1.38 kVA** | **1.06 kVA** (unchanged) |
| speed ceiling | 5,900 rpm | **~4,500 rpm** (bracket 4,000-4,800) |
| cycle-basis power factor | ~0.40 | ~0.40 |

The stack route holds current density, kVA and efficiency fixed and pays with speed range.
Torque is exactly proportional to stack length in the model, so this estimate needs no new
solve to be right within the 2D approximation.

**Correction added after this memo (D-022).** The ceiling figures above were built on a
11.5 V terminal voltage that belonged to a superseded state; the machine's own flux
solution gives 12.5-14.0 V at 3000 rpm, which puts the ceiling at 5,200-6,300 rpm before
any stack change (5,900 above is the top of that bracket, 4,500 the stack route). Two
further consequences, both adverse but bounded:

- The quoted PF of 0.578 is a peak-angle value. On a cycle basis it is **0.40**, so ~1.0
  kVA buys **387 W** of shaft, not 556 W. The rail budget in question 3 below does not
  change; the work it delivers does.
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
3. **Is the 48 V rail able to carry ~1.0 kVA at PF ~0.40** at the chosen thermal design?
   (The kVA is unchanged by the recommendation, and the PF figure is lower than the 0.578
   previously quoted, so the rail must deliver more current per watt of shaft than the
   earlier memo implied.)

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
