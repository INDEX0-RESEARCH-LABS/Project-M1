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

A rotor skew of **two slot pitches (20 deg mechanical)** takes peak-to-peak from 96.6% to
**12.4% in-model, inside the 15% gate**, for an estimated **2% mean-torque** cost. One slot
pitch gives 21.9% and does not pass; 15 deg is *worse* than 10 deg, because skew must be an
integer number of slot pitches.

What this buys: the ripple risk no longer justifies a stator redesign. What it costs: a
lamination-stacking decision (skewed stacking, or a skewed key), which is a tooling
question rather than a design one.

## 2. Efficiency is 90.3%, not 93.2%

A synchronous-frame drive holds current constant over a revolution, so copper loss is
constant while torque is not. Energy-average efficiency is therefore set by the **mean**
torque. The previously quoted 93.2% used the peak-angle torque with the same losses, which
is the same peak-versus-mean error that produced the 1.77 N.m figure. The correct number is
**90.3%** (mean 1.1918 N.m at J = 5.21 A/mm2). 93.2% survives only as a peak-angle figure,
labelled as such.

## 3. The 1.6 N.m target is 34% short, and the cheapest fix is a longer stack

Mean torque at the certified current is 1.1918 N.m. Two ways to reach 1.6 N.m:

| | current route | stack route (recommended) |
|---|---|---|
| what changes | J 5.21 -> 6.99 A/mm2 | stack 50.4 -> **67.7 mm** |
| copper loss | 43 W | **32 W** |
| efficiency | 89.5% | **90.3%** |
| apparent power | **1.42 kVA** | **1.06 kVA** (unchanged) |
| speed ceiling | 6840 rpm | **~5100 rpm** |

The stack route holds current density, kVA and efficiency fixed and pays with speed range.
Torque is exactly proportional to stack length in the model, so this estimate needs no new
solve to be right within the 2D approximation.

## Decision needed from the founder

1. **Is a 67.7 mm stack acceptable** in the target envelope? This is the only question that
   determines which route is taken.
2. **Is a ~5100 rpm voltage ceiling acceptable** for a 3000 rpm nominal machine?
3. **Is the 48 V rail able to carry 1.06 kVA** at the chosen thermal design? (This figure is
   unchanged by the recommendation, and 1.42 kVA would be the alternative.)

If stack length is capped by the application, the current route is the fallback and the
efficiency figure drops to 89.5%.

## What is still not proven

- **No bench, no experimental evidence** (D-009). Every number here is a 2D
  current-source model: no skew in the field solve, no PWM, no end effects.
- The ripple *magnitude* is plausibly 2-4x high in-model (unskewed, sharp-edged 2D slots).
  The skew result is the quantitative version of that caveat: it is the missing physics.
- Rotor slot-harmonic loss (~1800 Hz) is bounded at 0.8-3.3 W but not modelled.
- Rotor punching tooling and BOM quotes remain F-class spend, founder-gated.

No money was spent to produce this note.
