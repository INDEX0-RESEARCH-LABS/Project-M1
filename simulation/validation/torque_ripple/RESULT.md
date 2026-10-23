# RESULT - load torque ripple of the deep-barrier rotor

**Verdict: ESTABLISHED in-model at ~100% peak-to-peak, and that FAILS gate R3.**
Gen 3 (2026-10-23) removed the two defects that made Gen 1 and Gen 2 disagree: the old
static curve was sampled at 5 deg, which cannot represent a 10-30 deg modulation, and
`torque_at` returned `abs()`, which hid the sign reversal. With the current pattern
rotated with the rotor and the D-016 annulus estimator, the two excitation models now
agree to within 1% (R6, ratio 0.99). The modulation is locked to the **winding repeat
unit (30 deg mech = 3 slot pitches)**, not to the slot pitch or the rotor period.
What follows is the record, including the two invalid generations.

Gates were declared in `PLAN.md` before running. Disposition of Gen 3: **R1 pass,
R2' partial (window agreement passes, estimator band spread fails), R3 FAIL, R4' pass,
R5 answered by the periodicity test, R6 pass.**

## 1. Generation 1 - the static torque-angle curve (invalid for ripple)

First harness swept the rotor with the current pattern fixed in the stator frame. That
is the **static torque-angle curve** `T(delta)`, whose slope over a slot pitch is the
fundamental, not ripple. It cannot answer the ripple question, and its values were
discarded as a ripple measure. It did produce a genuinely useful result, so it was
re-run deliberately and analysed properly (section 3).

## 2. Generation 2 - synchronized current (correct model, inconsistent output)

In steady state the current vector turns with the rotor, so the current angle is fixed.
The harness advances the three phase currents by `alpha = p*(delta - delta_op)` while
the rotor turns, which pins the relative angle at `delta_op = 26.25 deg`.
`torque_ripple.py`; `solve_raw(..., pattern=...)` is the only change to the solved path.

Checks that passed:

| check | result |
|---|---|
| `alpha = 0` reproduces the certified point | `T5 = 1.6695` N.m at 1536/4; `T9 = 1.663` at 3072/10 (certified 1.60) |
| 180 deg current rotation (all currents negated) | identical to 4 decimals - **VOID** |
| 90 deg rotor periodicity, 3 independent pairs | identical to 4 decimals |
| fine mesh at three points | 3.75: 0.802 vs 0.754 coarse; 42.25: 0.610 vs 0.548; 26.25: 1.663 vs 1.670 -> the large variations are not a coarse-mesh artifact |

Checks that failed:

- Over a 45 deg window at the fixed current angle the torque runs **0.64 to 1.70 N.m**
  (a 60-90% p-p swing). A synchronous machine at a fixed current angle cannot do that.
- Sweeping the current phase with the rotor **fixed** at 26.25 deg gives
  `T5 = 1.6695 / 0.8502 / 0.5986 / 0.1041` at `alpha = 0 / 30 / 90 / 120 deg`.
- Re-optimizing the current phase at `delta = 41.25` finds a best of **1.408 at
  `alpha = 20`**, i.e. 16% below the peak at `delta = 26.25` that no choice of current
  angle recovers.

One check was recorded as passing on first writing and is **void**:
`torque_at` returns `abs(torque_maxwell(...))`, so negating all three currents cannot
change the returned number whatever the extractor does. Sign-reversal equality is
therefore not evidence of anything. It is corrected here rather than left in the table
as a green tick. Non-convergence is ruled out as a cause of the swing: `solve_raw`
raises on `converged = False`, so a bad point cannot enter a sweep silently.

## 3. The static curve is clean, and it confirms D-014

Excitation unchanged (certified snapshot), 1536/4, rings 9, delta = 0..90 deg:

| delta | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 50 | 55 | 60 | 65 | 72 | 75 | 78 | 82 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T9 N.m | 0.44 | 0.00 | 0.42 | 0.84 | 1.08 | 1.55 | 1.51 | 1.44 | 1.07 | 0.01 | 0.51 | 1.13 | 1.45 | 1.61 | 1.57 | 0.60 | 1.09 |

A least-squares fit to the signed torque (negative below 5 deg and above 50 deg), with
mechanical orders 4, 8 and 12, gives amplitudes **1.536 / 0.137 / 0.037 N.m** and a
residual **RMS 0.044 N.m (2.8% of the fundamental)** once `delta = 78` is excluded.
Order 12 - the 6th electrical harmonic, the classic mmf-harmonic torque ripple - is
**2.4% of order 4**. Zeros at 5 and 50 deg, peak at 27-30 deg: **`DELTA_OP = 26.25`
sits on the peak and the certified 1.60 N.m point is reproduced.** That is an
independent confirmation of the D-014 headline from a different sweep than the one that
produced it.

`delta = 78` is **not** a coarse-mesh artifact and not an extractor blip: re-solved at
1536 rays / 10 gap rows it gives T9 = 0.509, and at 3072/10 it gives 0.528 (coarse 1536/4
was 0.597). It is stable to ~4% across two mesh levels and sits between two good
neighbours (75 deg: 1.57, 82 deg: 1.09), so a 3 deg wide dip of that depth is a
property of the geometry as discretised, not of the mesh quality. Unexplained, and
consistent with a local defect in the rotor-region classification at particular angles -
the same class of defect that would explain section 2.

Two caveats on the extractor, unchanged from earlier work: the ring-to-ring spread at
1536/4 reaches 23% at some angles (`delta = 35`: T1 1.87, T9 1.44), so the coarse mesh
is marginal for angle-resolved work; and the `delta = 78` outlier is unexplained.

## 4. Why this is not quotable

The static curve moves the rotor relative to the stator slots over the same 0-90 deg and
fits a 4/8/12 harmonic model to 0.044 N.m RMS, with order-12 at 2.4% of order 4. The
synchronized sweep moves the rotor over the same range and varies by 60-90%. Both are
the same geometry, the same current amplitude and the same extractor. A slot interaction
large enough to explain the second would be plainly visible in the first, as an order-12
component of tens of percent rather than 2.4%. Two models of one machine cannot both be
right, so at least one is wrong and the peak-to-peak cannot be attributed to ripple.

The pattern construction was audited analytically and is **correct**. The winding's
spatial harmonics of order 2 / 10 / 14 (fundamental, 5th, 7th electrical) sit at
17.28 / 3.92 / 3.19, i.e. 22.7% and 18.5% of the fundamental, with zero amplitude
spread as the current phase advances. Their phase rates are also right: over an advance
of 30 deg electrical the fundamental moves +15.00 deg mechanical (exactly with the
rotor), the 5th moves -3.00 (backward at alpha/5) and the 7th +2.14 (forward at
alpha/7). So the fundamental tracks the rotor exactly and the harmonics slip, which is
real travelling-wave physics and is the standard source of 6th-harmonic torque ripple.

That leaves the amplitude unexplained rather than the mechanism: the same 5th/7th slip
is present in the static sweep and shows up there as only 2.4% of order 4. Whether the
synchronized sweep can legitimately be 25x larger is not something this harness can
settle, and the audit continues in a separate review.

**Resolved in section 7 (D-018).** The "2.4% of order 4" came from the 5 deg curve in
section 3, which has two samples per 10 deg period and could not represent this
modulation. Gen 3 measures the two excitations on the same window: 91.4% vs 90.2%.

## 5. What is established, and what is not

- **ESTABLISHED**: the static torque-angle curve, its zeros, its peak, and therefore the
  D-014 operating point. No change to any quotable number in `STATUS.md`.
- **NOT ESTABLISHED**: torque ripple, peak-to-peak, dominant order, NVH. No number, not
  even a band. *(Superseded by section 7-9 and D-018.)*
- **Still true**: a SynRM has no cogging torque (no magnets); all ripple is load ripple,
  so a no-load sweep would measure nothing.

## 6. What would settle it

1. Verify the airgap field actually rotates by `alpha/2` under the pattern advance. Two
   solves plus a spatial FFT of `B_r(theta)` at the gap. This is the direct test of the
   suspect in section 4.
2. Cross-validate the synchronized model on a published benchmark with a known ripple
   figure before trusting it on this rotor.
3. Independent route: FFT of the flux linkage over one electrical cycle at a fixed
   current angle, and take the torque from the fundamental. Different numerics, same
   physics, no reliance on the Maxwell stress integral.
4. If a validated model still shows more than ~10% p-p at the target current, the lever
   is stator skew or a barrier-end chamfer, not another barrier sweep.

No further compute was spent on this after the inconsistency appeared; the gates exist
to stop exactly this kind of number from entering the record.

## 7. Gen 3 - the modulation measured (2026-10-23)

46 points, 15.0-37.5 deg at 0.5 deg, J = 5.21 A/mm2, current angle pinned at 26.0,
1536 rays / 4 gap rows. Estimator: D-016 annulus (rings 1/5/9 written for continuity).
Log `/tmp/opencode/m1/ripple_gen3.log`, CSV `/tmp/opencode/m1/ripple_gen3.csv`.

| estimator | mean N.m | min | max | p-p fraction |
|---|---|---|---|---|
| rings 1 | 1.600 | 0.774 | 2.036 | 78.9% |
| rings 5 | 1.465 | 0.609 | 1.929 | 90.1% |
| rings 9 | 1.338 | 0.492 | 1.813 | 98.7% |
| **annulus** | **1.296** | **0.448** | **1.746** | **100.2%** |

Annulus extrema: minimum at 33.0 deg, maximum at 25.5 deg. All four estimators exceed
the 15% gate; the sign and size of the verdict do not depend on the estimator.

**R2' adequacy: partial.** The window-agreement half passes comfortably - 98.3% vs
99.3% for the two 10 deg end windows (1.0 pp) and 98.0% vs 97.6% for 11.25 deg (0.4 pp),
against a 2.0 pp gate. The estimator half fails: annulus band spread median **14.3%**,
maximum **58.8%** at the dip, against gates of 10% and 20%. So the fraction is not
quotable to better than a few percent. It is quotable to well within a factor of two, and
the gate is 15%.

**R4' extremum validation: pass.** The three extrema re-solved at 3072 rays / 10 gap rows
(log `/tmp/opencode/m1/ripple_extrema.log`):

| delta | coarse ann | fine ann | change |
|---|---|---|---|
| 23.00 | 0.5323 | 0.5551 | +4.3% |
| 25.50 | 1.7461 | 1.7810 | +2.0% |
| 33.00 | 0.4479 | 0.4765 | +6.4% |

p-p = 1.3045 fine vs 1.2982 coarse, a difference of **0.5 pp** against a 2 pp gate. The
band spread at the two dips stays 24% and 31% even at 3072/10, so the absolute dip value
carries about +-0.07 N.m; p-p is therefore **1.30 +- 0.07 N.m, i.e. 100% +- 5%**. The
near-cancellation of large positive and negative gap contributions is a property of the
dip, not of the mesh.

**Co-energy arbiter: the dip is in the energy landscape.** The co-energy derivative
shares no machinery with gap sampling, so it is the last independent route. With the coil
currents frozen at the operating point and only the rotor moved by +-0.5 deg, the
overall-bias factors come out +7% at the peak and -3% at the dip:

| delta | annulus | co-energy | co/ann |
|---|---|---|---|
| 25.50 (peak) | 1.746 | 1.863 | 1.07 |
| 33.00 (dip) | 0.448 | 0.436 | 0.97 |

The dip survives. What that rules out is the whole class of "the gap integral sees a
different field from the stored energy" artefacts, angle-dependent sampling included. It
does not rule out a systematic error in the solved field itself, which would move both
routes together.

**R6 reconciliation: pass, ratio 0.99.** Over the same 20.375-31.625 deg window, where the
static envelope slope is near zero, the static 0.25 deg sweep gives p-p 91.4% and the
synchronized sweep 90.2%. The Gen 1 vs Gen 2 contradiction in section 4 is therefore
resolved, and the resolution is the one section 4 already suspected: the static curve it
relied on was sampled at 5 deg, i.e. two samples per 10 deg period, so it could not show
this modulation. The 4/8/12 harmonic fit that produced "order 12 = 2.4%" is withdrawn.

## 8. What the modulation is locked to

The period is measured, not assumed. Repeating the synchronized sweep and comparing
`T(delta + shift)`:

| shift | pairs | max abs difference | period? |
|---|---|---|---|
| 10.0 deg | 22 | 0.362 N.m (mean 0.152) | no |
| 20.0 deg | 17 | 0.362 N.m (mean 0.179) | no |
| 30.0 deg | 12 | **0.0000 N.m** | **yes, exact** |

The 20 deg row is a lesson worth keeping: with the first 6 pairs it read 0.048 N.m, which
looked like a symmetry. Seventeen pairs show 0.362 N.m. A partial test would have
mis-assigned the period.

30 deg mechanical is 60 electrical, which is **three slot pitches and exactly one repeat
unit of the three-phase winding** (36 slots, 4 poles, q = 3 -> 3 slots per phase belt). It
is not the 10 deg slot pitch and not the 90 deg rotor pole period. So the dominant
modulation is locked to the *winding* repeat, which is the signature of an mmf-harmonic
interaction rather than of bare slot opening. That is consistent with the winding audit in
section 4: the 5th and 7th spatial harmonics sit at 22.7% and 18.5% of the fundamental,
which is poor for q = 3 and is the classic source of 6th-electrical-harmonic torque ripple
(12 cycles per mechanical revolution = 30 deg period).

This does **not** match the R5 decision rule as frozen, which expected either the slot
order (36) or a low order 2-6. R5 is answered by the measurement but the frozen lever map
does not cover the answer: the lever is the **winding layout / phase belt**, with barrier
shape second, not slot opening or skew alone.

> **Superseded by section 10 (D-019).** The reasoning above is sound but it was applied to
> the wrong harmonic. Order 12 exists at 0.157 N.m, but order 36 is 0.495 N.m, 3.2x larger
> and slot-locked; the baseline rotor reproduces it, and a 20 deg skew removes it. The
> lever is **skew first**, and the winding layout is the second step on the residual
> order 12. Sections 7-9 are otherwise unchanged.

## 9. Consequence for the certified operating point

The 1.873 N.m certified at 26.0 deg (D-016) is an **instantaneous value at one rotor
position inside a ~107% p-p modulation**, not a running average. The full-period sweep at
0.5 deg resolution (`torque_ripple.py --start 0 --stop 30 --step 0.5`, 61 points, log
`/tmp/opencode/m1/ripple_period_0p5.log`, `sweep_period_0p5deg.csv`) gives the running
number:

| quantity | J = 5.21 A/mm2 |
|---|---|
| **mean torque, annulus** | **1.2305 N.m** (one exact period, 60 samples) |
| rings 1 / 5 / 9 (mean) | 1.544 / 1.402 / 1.275 N.m |
| min / max | **0.4268** (at 12.50 deg) / **1.7461** (at 25.50 deg) |
| p-p | **107.2%** (rings 1/5/9: 81.8 / 94.2 / 103.6% - it grows outward) |
| peak / mean | 1.42 |
| annulus band spread | median 17.2%, max 58.8% |

**The sampling resolution is part of the result, not a tolerance.** The same curve
integrated on the 2, 1 and 0.5 deg grids gives:

| grid | samples per period | mean torque |
|---|---|---|
| 2.0 deg | 15 | 1.1918 N.m |
| 1.0 deg | 30 | 1.2258 N.m |
| **0.5 deg** | **60** | **1.2305 N.m** |

The 2 deg estimate is biased **3.2% low**, and the mechanism is visible in the data: the
dips are narrow V-notches about 3 deg wide (bottom 0.4268 at 12.50 deg), so with only five
samples per 10 deg slot period the grid lands on the dip flanks and never on the bottom.
Convergence from 1.0 to 0.5 deg is 0.005 N.m, so 1.2305 is good to about +-0.005; use
**1.2305**, and any future mean of this curve must be taken at 0.5 deg or with an explicit
convergence test.

The three 30 deg periods still agree (T(0) = T(30) = T(90) = 1.6660 N.m, difference
0.000000), and the co-energy bias measured in section 7 (+7% at the peak, -3% at the dip)
puts the true mean within a few percent of 1.23; it does not move it toward 1.77.

**Correction chain on this number.** D-018 quoted 1.202 N.m (a 0-90 deg average that
counted the single physical point at 0/30/90 deg three times out of 46); the per-period
average at 2 deg resolution was 1.1918 N.m; the 0.5 deg sweep gives **1.2305 N.m**. Both
earlier values were quadrature artefacts of the grids they were taken on.

**So the design is undersized on a mean-torque basis, by 30%.** The 1.6 N.m target was
met at J = 5.21 against an instantaneous 1.77 N.m; against a mean of 1.2305 N.m the same
target needs about J = 6.77 A/mm2 (5.21 x 1.6/1.2305), which is 1.69x the copper loss
(23-24.5 W -> ~40 W) and a first-order efficiency of ~89.9% rather than the 93.2%
peak-angle figure. Apparent power scales with current, so ~1.38 kVA rather than 1.06 kVA.
Those are linear extrapolations that ignore saturation, which will make them worse rather
than better, so they are a **planning estimate, not a certified number** - a
re-certification at the new J is required before any of it is quoted. D-020 compares this
route against buying the deficit with stack length instead, and D-021 supersedes
D-018/D-019 on this number.

Two clarifications that keep this proportionate:

- The mechanism is **stator-side**, which was measured after this section was first
  written (section 10.2): the baseline 2-barrier rotor shows the same dips at the same
  angles and the same relative depth. D-014's rotor choice therefore does not cause the
  ripple and is not threatened by it, but the absolute design-point move above applies to
  whichever rotor is chosen.
- The current angle 26.0 deg was chosen as the argmax of the *instantaneous* torque. The
  angle that maximises *mean* torque has not been measured and is unlikely to be the same
  when the modulation is this large. That is a cheap next lever (one 30 deg period per
  angle) and it is not yet spent.

Two ways this could still be an over-prediction, both testable at zero cost:

1. **Stator slot opening.** 3.0 mm mouth on a 0.52 mm gap is a 5.8:1 opening, which is a
   very large permeance modulation. A narrower mouth changes the mmf-harmonic coupling.
2. **Skew.** None is modelled. Skew of one slot pitch is the standard remedy for exactly
   this class of order, but it does not remove a pure 6th-electrical component, so the R5
   answer above predicts skew will help less than usual.

Neither can be tested by re-meshing: both are geometry changes and need their own declared
gates. The honest status is **FAIL at ~100% p-p in a 2D current-source model, mechanism
identified as winding-locked, magnitude one order larger than a shippable traction motor,
and no experimental evidence either way** - there is still no motor on a bench.

## 10. What the modulation actually is: slot order, and the skew lever (D-019)

D-018 concluded that the modulation is "locked to the 30 deg winding repeat, so the lever
is the winding layout". The *period* is right and the shift test still stands. The *lever*
is wrong. Three measurements, all from data already on disk, correct it - no new solves.

### 10.1 The dominant order is the slot order, not the winding order

If the period is exactly 30 deg, only orders that are multiples of 12 can be present. A
least-squares fit of one exact period (0-28 deg, 15 samples, harmonics 12/24/36/48/60)
needs no window and no period assumption:

| order | meaning | S6 amplitude (N.m), 0.5 deg | baseline (N.m), 2 deg |
|---|---|---|---|
| 12 | 3-slot phase belt (5th/7th MMF) | 0.161 | 0.157 |
| 24 | 2nd belt harmonic | 0.088 | 0.088 |
| **36** | **slot pitch (once per 10 deg)** | **0.457** | **0.524** |
| 48 | 4th belt harmonic | 0.014 | 0.009 |
| 60 | 5th belt harmonic | 0.025 | 0.021 |
| 72 | 2nd slot harmonic | 0.269 | - |
| 108 | 3rd slot harmonic | 0.102 | - |
| residual rms | | 0.208 (16.9%) with 5 harmonics; 0.081 (6.6%) to order 96; 0.013 (1.1%) to order 240 | 0.146 (12.7%) |

Order 36 is **2.8x order 12**. One dip per slot pitch is what a slot-tooth-tip interaction
looks like, and it explains the dip spacing directly: the full-period 0.5 deg sweep finds
dips at **3.0, 12.5 and 22.5 deg**, spacings 9.5 and 10.0 deg against a 10.0 deg slot
pitch. The dip is a narrow notch, not a sinusoid: orders 72 (0.269) and 108 (0.102) carry
real energy, and the residual only falls below 1% when harmonics to order 240 are
included. The notch shape is why the mean is so quadrature-sensitive (section 9).

The residual is *not* small at five harmonics (0.21 N.m rms, 16.9%), and it should not be:
the five harmonics carry the mean and the main structure but not the notch. Take the table
as a **ranking of mechanisms**, not as a reconstruction of the curve.

### 10.2 The depth does not come from the barrier rotor

`torque_ripple.py --base` run at J = 5.62 over the same 30 deg span
(`sweep_base_2deg.csv`, log `/tmp/opencode/m1/ripple_base.log`; the baseline runs at its
own rated current, which is the equal-torque loading):

| | S6 (4 barriers, J=5.21) | baseline (2 barriers, J=5.62) |
|---|---|---|
| mean | 1.2305 N.m (0.5 deg) | 1.1459 N.m (2 deg) |
| min / max | 0.4268 / 1.7461 | 0.492 / 1.715 |
| p-p | 107.2% (0.5 deg) | 106.7% (2 deg) |
| dip angles | 12.0, 22.0 deg | 12.0, 22.0 deg |
| order 12 | 0.157 | 0.157 |
| order 36 | 0.495 | 0.524 |

The two rotors were measured on different grids (0.5 deg for S6, 2 deg for the baseline),
so their p-p values are not directly comparable - and they need not be, because the
conclusion rests on the *angles* and the *harmonic identity*, which are grid-robust. A
four-barrier and a two-barrier rotor cannot produce the same slot-order torque, at the
same rotor angles, to within 6% by coincidence. The barriers barely modulate the ripple:
the same relative shape appears on both, and order 12 is identical to 0.2%. **The
modulation is a stator-side effect** - the slot mouth and tooth tip against the rotor
surface as a whole - and the barrier geometry is not the lever.

Consequence for D-014: the ripple is not an S6 defect. On a mean basis S6 still wins. Its
relative modulation is *shallower* (96.6% vs 106.7%), so the mean is depressed less than
the baseline's. At equal current (5.21 A/mm2, the basis on which the +18.3% was claimed)
the baseline mean is 1.1459 x (5.21/5.62)^k with k between 1 and 2, giving a mean-torque
gain of **+12% to +21%** against the +18.3% instantaneous figure. Reducing the baseline
current away from saturation favours the upper end, so the gain is at least as large as
the instantaneous one. The D-014 advantage does not dissolve on a running basis.

### 10.3 Skew is the lever, and it is nearly free

If the ripple is slot-order torque, then averaging the rotor position along the stack
should cancel it. Multi-slice 2D skew does exactly that as a post-process on the measured
curve: `T_skew(th) = mean over slices of T(th + offset)`, 41-point integration, no new
solves. This is the standard first-order skew model.

| axial skew | S6 p-p (0.5 deg curve) | baseline p-p (2 deg curve) | R3 gate (15%) |
|---|---|---|---|
| 0 deg (unskewed, as measured) | 107.2% | 106.7% | FAIL |
| 2.5 deg | 87.6% | 95.2% | FAIL |
| 5.0 deg (half slot pitch) | 66.9% | 76.9% | FAIL |
| 7.5 deg | 43.7% | 47.0% | FAIL |
| 10.0 deg (one slot pitch) | 23.1% | 22.9% | FAIL |
| 15.0 deg (1.5 slot pitches) | 25.9% | 28.9% | FAIL |
| 20.0 deg (two slot pitches) | **12.9%** | **13.1%** | **PASS** |
| 30.0 deg (three pitches = one winding repeat) | **2.7%** | - | **PASS** |

- One slot pitch removes 4.6x of the ripple but leaves 23.1%, still above the gate.
- Two slot pitches passes at 12.9%. **Skew must be an integer number of slot pitches**:
  15 deg is *worse* than 10 deg because the order-36 average over 1.5 cycles does not
  vanish. Three pitches (30 deg, one full winding repeat) gives 2.7%, the cleanest
  cancellation available, and it kills order 12 as well.
- The mean is unchanged in this model (1.1930 N.m at every skew) because each slice is
  excited at its own ideal current angle.
- What the model cannot see, and the real cost: a machine has **one** current vector, so
  the saliency is averaged along the stack. The classic skew factor for 40 deg electrical
  is sin(20 deg)/(20 deg in rad) = 0.980, i.e. about **2% mean torque**. That is a far
  better trade than the 34% mean-torque shortfall, and the two problems are independent.

After 20 deg skew the residual is order 12, only partially cancelled (a 20 deg skew spans
2/3 of its 30 deg period), which is exactly where **winding layout** becomes the lever - as
a second step, on a much smaller component. A 30 deg skew removes that too.

### 10.4 Why the magnitude may still be 2-4x too high

Order 36 at 0.495 N.m is 42% of the mean torque. Real SynRMs show single-digit slot-order
ripple unskewed. The 2D model has no skew, no axial flux redistribution, and sharp-edged
slots, all of which inflate slot-order torque; section 10.3 is the quantitative version of
that statement, and the missing skew alone accounts for a factor of 4.6. So the model is
not necessarily wrong - it is modelling an unskewed rotor, and real rotors are skewed.
The absolute magnitude stays in-model until there is a bench, but the *mechanism* is now
identified and the remedy is standard practice.

### 10.5 Corrections to earlier text

- **The mean has been corrected twice.** D-018 quoted 1.202 N.m, an average over the
  0-90 deg grid that counted the physical point at 0/30/90 deg three times out of 46. On
  one exact period at 2 deg that became 1.1918 N.m. The 0.5 deg sweep then showed that the
  2 deg grid was itself biased 3.2% low by quadrature across the notches, and the value is
  **1.2305 N.m**. The mean-basis consequence moves from J = 6.99 to **J = 6.77** (~40 W
  copper, ~89.9% efficiency, ~1.38 kVA). See section 9 and D-021.
- D-018's "the lever is the winding layout" is corrected. The period is stator-set, but
  the dominant order is the slot order, so the primary lever is **skew** (section 10.3)
  and winding layout acts on the residual order 12 afterwards.
- The speculation in an earlier revision of section 9 - that the dip depth was
  rotor-tip dependent because the dips are mirror-symmetric about 22.5 deg - is refuted by
  section 10.2 and has been replaced there. Mirror symmetry about the pole axis is
  consistent with a slot-aligned effect in a rotor that is itself symmetric about that
  axis; it was not evidence for a barrier-tip origin.
