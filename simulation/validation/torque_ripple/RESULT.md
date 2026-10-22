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

## 9. Consequence for the certified operating point

The 1.873 N.m certified at 26.0 deg (D-016) is an **instantaneous value at one rotor
position inside a ~100% p-p modulation**, not a running average. The full-period sweep
(`torque_ripple.py --start 0 --stop 90 --step 2`, 46 points, log
`/tmp/opencode/m1/ripple_period.log`) gives the running number:

| quantity | J = 5.21 A/mm2 |
|---|---|
| **mean torque, annulus** | **1.202 N.m** |
| mean, rings 5 (continuity) | 1.374 N.m |
| min / max | 0.587 / 1.739 N.m |
| p-p at 2 deg sampling | 95.8% (100.2% at 0.5 deg over the window) |
| peak at 26.0 deg / mean | 1.45 |

The three 30 deg periods give the same mean to four decimals (1.1918 N.m each), which
confirms the period independently of the shift test. The co-energy bias measured in
section 7 (+7% at the peak, -3% at the dip) puts the true mean within a few percent of
1.20-1.25 N.m; it does not move it toward 1.77.

**So the design is undersized on a mean-torque basis.** The 1.6 N.m target was met at
J = 5.21 against an instantaneous 1.77 N.m; against a mean of 1.202 N.m the same target
needs about J = 6.9 A/mm2, which is roughly 1.8x the copper loss (23-24.5 W -> ~42 W) and
a first-order efficiency of ~89.6% rather than 93.2%. Apparent power scales with current,
so ~1.4 kVA rather than 1.06 kVA. Those are linear extrapolations that ignore saturation,
which will make them worse rather than better, so they are a **planning estimate, not a
certified number** - a re-certification at the new J is required before any of it is
quoted.

Two clarifications that keep this proportionate:

- The mechanism is **winding-locked**, and the baseline rotor uses the same winding, so
  this is a stator-level defect that both rotors inherit. It does not overturn D-014's
  rotor choice, but it does move the whole design point.
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
