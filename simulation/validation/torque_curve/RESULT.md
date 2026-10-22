# RESULT - the torque-angle curve is not what the record says

**Verdict: two defects, one fixed and one open. The certified operating point must be
re-derived before D-014 is quoted again.**

This section started as a ripple investigation. It became a check of the torque-angle
curve itself, and the curve failed. Nothing here was found by tuning; every number below
came from an experiment declared in advance or from a pre-existing invariant.

## 1. The half-slot offset (D-015, FIXED)

`rajini_anchor.py`'s own docstring, written 2026-10-21, states the invariant that makes
the winding checkable without any FEM:

> delta = 0  -> winding lobe sits on the rotor Q-axis: torque zero by mirror symmetry
> delta = 45 -> poles under the lobe (d-aligned): torque zero again

And `synrm_geometry.stator_profile` centres slot `k` at `k*pitch`, which is why
`synrm_mesh._in_slot` was corrected on 2026-10-20 to test `min(a, pitch-a)`.

`split_slots` did not follow. It binned cells with `floor(theta/pitch)`, so bin `i`
spanned `[i*pitch, (i+1)*pitch)` and was physically centred on `(i+0.5)*pitch`.

Measured offset of each bin centre from the geometry slot it is named after, 36-slot
mesh, no FEM:

| binning | mean offset | max abs offset |
|---|---|---|
| `floor(theta/pitch)` (as shipped) | **+0.513 pitch** | 0.519 |
| `floor((theta + 0.5*pitch)/pitch)` (fixed) | 0.000 | 0.002 |

Two consequences, not one. The applied MMF was rotated by half a slot pitch
(5 deg mechanical, 10 deg electrical); and because each bin spans the halves of two
adjacent slots, the two phases meeting at every belt boundary were averaged into a
single current density.

FEM confirmation at the two angles that must be torque-free (1536 rays / 4 gap rows,
rings 9, J = 5.21 A/mm2):

| delta | as shipped | fixed | invariant |
|---|---|---|---|
| 0 deg | 0.4386 N.m (27% of peak) | **0.0102** (0.6%) | zero |
| 45 deg | 0.4577 N.m (29%) | **0.0296** (1.9%) | zero |

The shipped model's actual zero sat at 50 deg, i.e. displaced by exactly the half-slot.
`DELTA_OP = 26.25` was chosen as the peak of a curve whose angle axis was off by that
same 5 deg, so the certified current angle is mislabelled by 10 deg electrical.

**The torque at the same label also changed**: 1.5761 -> **1.7897 N.m** at delta = 26.25
(+13.6%). The fix is not a translation of the curve - removing the belt-boundary phase
mixing changes the machine. So this is not a relabelling: **every certified quantity
(torque, flux linkage, PF, efficiency, and the derived ceiling) has to be re-derived on
the corrected winding.** D-015 records the fix; the numbers stay frozen until
re-certification.

Regression test added: `tests/test_rajini_winding.py::
test_split_slots_bins_are_centred_on_geometry_slots` fails with the old binning to
0.513 pitch and passes at 0.000.

## 2. Undetected dips in the torque-angle curve (OPEN)

Gate A2, declared before the run: *a 5 deg grid must not miss structure - sampled at
0.25 deg, the curve must stay within 10% of the 5 deg interpolant over 40-46 deg.*

It does not. Static curve, corrected winding not applied yet (shipped binning,
1536/4, rings 9):

| delta | 40.0 | 40.5 | 41.0 | 41.5 | 42.0 | 42.25 | 42.5 | 43.0 | 43.5 | 43.75 |
|---|---|---|---|---|---|---|---|---|---|---|
| T9 N.m | 1.072 | 1.019 | 0.928 | 0.654 | 0.191 | 0.065 | 0.007 | 0.041 | 0.022 | 0.025 |

The 5 deg samples at 40 (1.07) and 45 (0.46) both sit well above the dip, which bottoms
below 0.05 N.m over 42.5-43.75 deg. **Gate A2 fails.** The audit found the same
structure at delta = 78 and at its mirror, and both are reproducible at 3072 rays /
10 gap rows (0.528 against 1.48 expected), so it is not a coarse-mesh artifact and not a
narrow numerical spike.

Three independent estimators agree the torque really is low there, so it is in the
field and not in the extraction: single circle 0.41, ring-averaged 0.065, gap area
integral 0.02-0.13. What is not established is the *depth* - see section 3.

The physical reading is still open. A torque collapse to ~2% of the smooth-curve value
at a fixed current angle is not a SynRM phenomenon at 7 deg from d-alignment, so the
leading suspect is saturation of the thin iron path combined with a discretisation that
cannot represent it, not a real machine feature. **No claim is made either way.**

## 3. The extractor cannot resolve low torque (OPEN, quantified)

Gate A3, declared before the run: *four equal radial bands across the gap must give the
same torque to within 5% - in a current-free annulus the Maxwell integral is exactly
radius-independent.*

At `delta = 26.25` (the certified point) the four bands give 1.585 / 1.579 / 1.556 /
1.421 N.m: a **10.7% spread, gate fails**. Across the annulus with single circles the
spread is worse: 1.328 to 1.858 N.m (+-16%, where the ring average is 1.576).

At `delta = 42.25` the bands give 0.073 / 0.065 / 0.028 / 0.242 - a 9x spread on a
0.02 N.m mean. The error is roughly constant in absolute terms (~0.2-0.3 N.m) because
the torque is a near-cancellation of large positive and negative contributions, so the
relative error explodes as the true torque approaches zero. **Angle-resolved torque
below ~0.5 N.m is not resolvable by this model**, and the +-4% in STATUS applies to the
certified point only, not to the curve.

Cause: `field_at` samples element-wise-constant B from a P1 solution, so a sampling
circle carries an O(h) error that does not average out however many rings are used
inside the same set of elements.

New estimator added, `fem_magnetics.torque_annulus`: in a current-free annulus the
circle integral is radius-independent, so its radial average is exactly the area
integral `depth/(mu0*(r_out-r_in)) * integral r*Br*Bt dA` over the gap. That uses every
gap element (~12k) instead of a few rings. At the certified point it gives **1.536 N.m**
against the ring-averaged 1.576, and it returns a per-band array whose spread is an
honest error bar instead of a single number with no uncertainty.

## 4. What this changes in the record

- **D-014's headline numbers are frozen, not withdrawn.** They were computed
  self-consistently on the shipped binning, which is a valid machine - just not the
  winding the labels describe, and not the one the drawing will say. Re-certification
  is required and is the next piece of work.
- The static curve is `ESTABLISHED at 5 deg resolution only`, and it has holes between
  the samples. Statements resting on its smoothness are provisional, including the
  4/8/12 harmonic fit in `torque_ripple/RESULT.md` (which was fitted to notch shoulders
  by luck, not design).
- **Ripple stays NOT ESTABLISHED**, now for a stronger reason than before: the curve it
  would be computed from is unresolved below 0.5 N.m and its angle axis is off by 5 deg.
- `torque_at` returns `abs()`, so no torque-sign claim is possible until there is a
  signed path.

## 5. Next, in order

1. Re-run the static curve at 0.25 deg over the full 0-45 deg on the **corrected**
   winding, with `torque_annulus` bands alongside the circle values. That single sweep
   re-locates the peak, maps every dip, and gives every point an error bar.
2. Re-certify the operating point at the corrected angle convention: torque, lambda,
   PF, S, efficiency, ceiling. Update D-014, STATUS and the winding/controller inputs.
3. Only then re-open ripple, on a curve whose sampling and angle axis are both sound.
4. If a dip survives all of that, it needs a saturation diagnostic (Bmax and the order-2
   gap-field spectrum per angle) before it can be called physical.
