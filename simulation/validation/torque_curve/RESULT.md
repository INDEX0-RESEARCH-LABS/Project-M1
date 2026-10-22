# RESULT - the torque-angle curve is not what the record says

**Verdict: the half-slot defect is fixed (D-015). The 0.25 deg sweep on the corrected
winding is now done, and it shows the curve has deep, converged dips that are real
torque reversals, not notches. The extractor question is settled by convergence: the
gap area integral is the only mesh-stable estimator, and the single circle used by the
certification chain carries a +0.55 N.m bias on a solid-rotor null test.**

Sections 1-5 were written before the sweep. Sections 6-10 report it.

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

## 6. The 0.25 deg sweep on the corrected winding (item 1 of section 5, DONE)

181 points, 0-45 deg at 0.25 deg, 1536 rays / 4 gap rows, J = 5.21 A/mm2, corrected
binning. Each point carries the 9-ring average (T9), the gap area integral (ann) and
its 4-band spread. Raw data: `sweep_0p25deg.csv` in this directory.

| delta | what | T9 N.m | ann N.m |
|---|---|---|---|
| 0.00 | zero (q-alignment) | 0.010 | 0.022 |
| 4.00 | dip | 0.006 | 0.031 |
| 9.25 | shoulder minimum | 0.766 | 0.751 |
| 12.50 | dip | 0.354 | 0.308 |
| 22.50 | dip | 0.529 | 0.513 |
| **26.00** | **peak** | **1.813** | 1.739 |
| 33.00 | dip | 0.251 | 0.213 |
| 41.75 | dip | 0.073 | 0.136 |
| 45.00 | zero (d-alignment) | 0.030 | 0.021 |

Peak annulus is 25.50 deg (1.753). The peak is a plateau: 25.5-27.5 deg stays within
1.5% of the maximum, so an operating angle of 26.0 vs 26.25 is not a meaningful choice.

Mean torque over 0-45 deg is 0.833 N.m, so peak/mean = 2.18. An ideal synchronous
reluctance curve `sin(4*delta)` has peak/mean = 1.57. The curve is substantially
lumpier than the fundamental it is supposed to be.

Gate A2, restated on the corrected winding: **still FAILS**. 102 of 181 points lie more
than 10% from the 5 deg interpolant.

## 7. The dips are torque reversals, and `abs()` was hiding it

`torque_at` returns `abs()`, so a genuine sign reversal looks exactly like a notch.
Signed values, 1536/4, same solutions:

| delta | 1.0 | 2.0 | 2.5 | 3.0 | 3.5 | 4.0 | 4.5 | 5.0 |
|---|---|---|---|---|---|---|---|---|
| single circle | +0.010 | -0.107 | -0.143 | -0.112 | -0.017 | +0.183 | +0.396 | +0.542 |
| 9-ring average | -0.029 | -0.223 | -0.265 | -0.228 | -0.144 | +0.006 | +0.237 | +0.361 |
| gap annulus | -0.043 | -0.245 | -0.273 | -0.245 | -0.168 | -0.010 | +0.219 | +0.325 |

All three estimators agree in sign and magnitude. The torque is genuinely negative
between about 1.5 and 3.9 deg and crosses zero at 3.95 deg. That is not a numerical
notch to zero: it is a 0.27 N.m negative lobe, 15% of the peak.

A negative lobe is physically admissible in a *static* sweep, because the stator
current pattern is fixed in space while the rotor turns, so the current-versus-rotor
angle sweeps a full cycle. The lobe means the flux is non-sinusoidal enough for a
4th-order torque harmonic to dominate near the q-axis. It does not by itself violate
any invariant: the curve is odd in delta by the 45 deg mirror symmetry, and the
winding pattern is antisymmetric under that mirror by design.

## 8. Four candidate mechanisms tested; all four refuted

Declared before running: each test is a null result if the dip survives it.

1. **Ray-degeneracy slivers.** `synrm_mesh` merged rays closer than 1e-4 rad, and the
   barrier-edge rays land on that floor exactly in the 3.5-4.0 deg band. `RAY_MERGE_TOL`
   was made a module constant and varied. At 4.0 deg: 0.0063 (1e-4), 0.0067 (5e-4),
   0.0396 (2e-3) N.m; 5e-3 produced zero-area elements and a singular matrix. The dip
   survives a 20x tolerance change. **Refuted.**
2. **Material misclassification.** Barrier and rotor-iron areas were integrated at 46
   angles. Both are constant to 1e-6 relative and equal to the analytic values. The
   classification does not move with delta. **Refuted.**
3. **Extractor bias.** A rotor with no barriers must give exactly zero torque at every
   angle. Measured at 0 / 12.25 / 26.25 / 33 deg: single circle **+0.540 / +0.548 /
   +0.570 / +0.551 N.m**, 9-ring -0.046 / -0.043 / -0.019 / -0.045, annulus -0.140 /
   -0.138 / -0.115 / -0.141. The biases are constant in angle, so they cannot create a
   dip. **Refuted as the cause; but this test also condemns the single circle, which is
   the estimator the certification chain uses (`dq_model.solve_point`).**
4. **Discretisation.** Mesh refinement at the dips, T9 (1536/4 -> 1536/8 -> 3072/8):
   delta 33 gives 0.251 / 0.157 / 0.196; delta 22.5 gives 0.529 / 0.481 / 0.489. The
   dips are stable at ~1/5 of the peak. **Refuted.**

Saturation is an amplifier, not the cause: dip/peak at 22.5 vs 26.0 is 0.455 at
J = 1.05 A/mm2 (essentially linear), 0.333 at 2.60, 0.292 at 5.21. The structure is
geometric and survives into the linear regime.

**Conclusion: within this model the dips are converged features of the field solution.**
No claim is made that the model represents a real laminated rotor; the 2D model has no
laminations, no end effects and a single-valued B-H curve.

## 9. The estimator question is settled by convergence, not by argument

Mesh ladder at delta = 26.0, J = 5.21, S6 geometry:

| mesh (rays/rows) | single circle | 9-ring average | gap annulus | 4-band spread |
|---|---|---|---|---|
| 1536/4 | 2.036 | 1.813 | 1.739 | 13.0% |
| 2048/6 | 1.898 | 1.571 | 1.747 | 12.4% |
| 3072/10 | 1.900 | 1.930 | 1.778 | 6.7% |
| 4096/10 | 1.855 | 1.823 | **1.770** | 8.7% |
| spread | 9.0% | 22.8% | **2.2%** | |

The ring average is not monotone in the mesh at all, which is what an estimator that
samples element-constant B on a few circles should look like. The area integral
converges to 1.77 N.m.

Error bar from the solid-rotor null: -0.14 N.m on the annulus. **T_peak = 1.77 +- 0.14
N.m.** D-014's frozen 1.60 sits just under the lower edge of that band, so the
re-certified torque is higher, but not by more than the estimator uncertainty.

## 10. What this changes in the record

- **D-016**: the gap area integral is the standard absolute-torque estimator. The
  single circle is retired for absolute torque (it carries a +0.55 N.m bias and does
  not converge); the 9-ring average is retired as well (23% mesh sensitivity).
  `dq_model.solve_point` now returns `T_ann` and `T_ann_err`, and the certification
  chain (`iron_loss`, `pf_check`) uses them. Torque feeds PF and efficiency through
  `p_mech`, so those move too.
- The operating point moves from 26.25 to **26.0 deg**, the argmax of the corrected
  sweep. The plateau makes this a small change.
- **Ripple is still NOT ESTABLISHED, but the reason is now better understood.** This
  sweep holds the stator current pattern fixed while the rotor turns, which makes it a
  *load-angle* curve, not a running-torque curve. A running machine under field
  orientation holds the current fixed in the **rotor** frame, so a ripple measurement
  must rotate the pattern with the rotor and vary delta: then only slot-locking
  remains. That is a new experiment, declared before it runs, not an inference from
  this curve.
- The dips must be resolved before any NVH or control claim: the operating point sits
  3.5 deg from a dip that costs 70% of the torque.

## 11. What the dips are, as far as the data goes (2026-10-23)

Three cheap tests on the committed sweep, all run after the mechanisms in section 8 were
refuted. None of them requires a new field solve.

1. **The dip pattern respects the geometry's symmetry.** Torque is odd in delta, so
   `|T|` is symmetric under `delta -> 45 - delta`. The minima pair up exactly as that
   requires: 4.00 with 41.64, 12.50 with 33.00, and 22.50 with itself. A mesh or
   ray-orientation artefact would not reproduce a symmetry that comes from the
   geometry, so this is evidence against a numerical cause, on top of the three meshes
   already tested.
2. **They are not one harmonic.** The dips are broad (2-3 deg) and irregularly spaced:
   8.50 / 10.00 / 10.50 / 8.64 deg. A window test kills the obvious candidates: the
   Fourier amplitude at the 36-slot order (10.0 deg) is 0.010 N.m, and the 32/rev or
   order-8 amplitude of 0.344 N.m found over 5-45 deg collapses to 0.038 N.m when the
   5-10 deg shoulder is excluded. That spike is leakage from the shoulder, not a
   stationary component. **No single order explains the dips.**
3. **Consequence.** The right description is a smooth envelope with an absolute
   modulation of roughly 0.25-0.3 N.m superimposed. Near the peak that is 14-29%; where
   the envelope itself is ~0.3 N.m (1.5-3.9 deg) the same modulation reverses the sign.
   That is consistent with the saturation result in section 8 (dip/peak 0.455 at low
   current, 0.292 at J=5.21): saturation amplifies a modulation that is present in the
   linear solution too.

Status: **origin UNCONFIRMED, reality supported.** It is stable across meshes and
estimators, symmetric as the geometry requires, and absent from the solid-rotor null
test - which is what a slot-locked or tip-saturation modulation should look like. It is
not a slot-order effect, and it is not resolved by any mesh change tried.

A fourth mechanism is now excluded on arithmetic rather than by a solve. The 5 deg
static curve in `validation/torque_ripple/RESULT.md` s.3 fitted "order 12 = 2.4% of
order 4" and offered that as proof that ripple must be small. Order 12 is a 7.5 deg
period, sampled every 5 deg: 1.5 samples per period. That fit could not have detected a
10 deg modulation at all, so it is withdrawn as evidence. It does not by itself prove the
modulation is real, which is what the Gen 3 ripple experiment is for.
