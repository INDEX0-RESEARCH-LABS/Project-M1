# RESULT - load torque ripple of the deep-barrier rotor

**Verdict: NOT ESTABLISHED. No ripple number is quoted.**
The sweep is not reportable: two generations of the harness were built, and the second
one is internally inconsistent with the first. The discrepancy is documented below
rather than averaged away. What *is* established is the static torque-angle curve of
D-014, which independently confirms the certified operating point.

Gates were declared in `PLAN.md` before running. Disposition: **R1 pass, R2 fail,
R3 not applied, R4 partial pass, R5 not reached.**

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
| 180 deg current rotation (all currents negated) | identical torque to 4 decimals |
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
produced it. `delta = 78` is a single unexplained outlier (0.60 against 1.48 expected);
dropping it is what takes the RMS from 0.166 to 0.044, so it is worth one re-solve
before it is called a measurement artifact.

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

## 5. What is established, and what is not

- **ESTABLISHED**: the static torque-angle curve, its zeros, its peak, and therefore the
  D-014 operating point. No change to any quotable number in `STATUS.md`.
- **NOT ESTABLISHED**: torque ripple, peak-to-peak, dominant order, NVH. No number, not
  even a band.
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
