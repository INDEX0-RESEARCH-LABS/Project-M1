# RESULT - dq model attempt: torque corroborated, two-parameter dq falsified, PF withdrawn

**Script:** `simulation/scripts/dq_model.py` (log `/tmp/opencode/m1/dq_model.log`).
**Declared method/gates:** `PLAN.md` (before running).

## 1. What was measured (130 mm bore, 50.4 mm stack, M-43 bracket)

Apparent phase inductance from the slot stream function, and the Maxwell torque, at
J = 6 A/mm2 (3072-ray certification in section 3):

| delta [deg] | L_app [mH] | T [N.m/m] |
|---|---|---|
| 0 (q-align) | 0.0616 | 7.35 |
| 26.25 (MTPA) | 0.0862 | 40.12 |
| 45 (d-align) | 0.1152 | 21.58 |
| 67.5 | 0.1016 | 3.44 |
| 90 (q-align again) | 0.0616 | 7.35 |

- **D1 PASS**: L(d) > L(q) at both current levels. Ratio at the alignment extremes
  **1.87** (J=6), 1.84 (J=4.8).
- **D3 PASS**: 1536 -> 3072/rows10 drift **+0.0% (Ld), +0.1% (Lq)**. The extraction is
  converged; the failure below is not numerical.

## 2. D2 FAILED - the model class, not the data

`T_dq = 1.5 p (Ld - Lq) i_d i_q` gives **0.643 N.m vs 2.022 N.m** from the solve
(-68%, factor 3.1). It fails the same way at J=4.8 (-68%), so it is systematic.

Before blaming the solve, an independent arbiter was run: **T = dW'/d(delta) from the
co-energy** (no Maxwell integral involved), same solution, +/-0.5 deg:

| point | T_co-energy | T_Maxwell | gap |
|---|---|---|---|
| delta 26.25 (operating point) | **36.08** | **40.12** | **-10.1%** |
| delta 0 (q-axis) | -11.13 | +7.45 | sign and size disagree |
| delta 45 (d-axis) | +8.13 | 15.76 ... 23.15 | disagree 2-3x |

**Conclusion 1: the torque at the operating point is corroborated by two independent
methods** (within the extractor's known ~10% re-mesh floor). Every envelope number
built on the MTPA torque survives this test.

**Conclusion 2: the two-parameter dq model is invalid for this machine.** The machine's
co-energy is dominated by saturated iron (bridges/webs), not by the airgap saliency, so
`0.5 I^2 dL/ddelta` and `1.5p(Ld-Lq)id iq` do not describe it. Two further symptoms:
the co-energy has a *minimum* at the torque peak (curvature +203 J/m/rad2, which a
single-mode model cannot produce), and the torque does not vanish at either alignment
axis (7.4 and 21.6 N.m/m).

**Conclusion 3: the phase-flux probe is not a clean dq probe.** L(26.25) = 0.0862 mH but
L(63.75) = 0.1016 mH (-18%) - a mirror pair that must be equal for a symmetric rotor.
The barrier polygons are symmetric by construction (checked in `synrm_geometry.py`), so
the cause is the **discrete single-layer 36-slot winding**, which is not mirror-symmetric
about the MMF axis. Consequence: `L_app` is a converged but interpretation-limited
quantity; it is not the machine's saliency.

## 3. Retraction: the PF / inverter-VA claim

The earlier `PF ~ 0.25, ~4 kVA inverter` figure was an upper bound on VA from the design
phase voltage. The dq route that was supposed to replace it is now falsified (section 2),
so **no PF is published**. What survives, because it depends only on the measured flux
linkage scale and on geometry:

- **Phase current is the real constraint**: ~115 A at J=6 with the current 48 V winding
  (N_c = 1.25, a=1), ~102 A at the 1.6 N.m point.
- **Voltage is not the constraint**: `omega * lambda` with the measured lambda = 10-13 mWb
  gives `Vhat ~ 6-8 V` against a 26.3 V peak ceiling. The winding is under-turned for the
  flux this machine actually produces.
- **Turns rescale ~3x** (N_c ~ 3.7 at a=1, or 15 turns at a=4) cuts the phase current to
  ~35 A at **identical copper loss** (same slot AT, same J) and stays inside the 48 V
  ceiling. That is the actionable inverter-cost lever, and it does not depend on the
  failed model.

## 4. Correction found by this run: torque scales as J^2 here

| J [A/mm2] | T [N.m] |
|---|---|
| 4.8 | 1.279 |
| 6.0 | 2.022 |

Ratio 1.581 vs `(6/4.8)^2 = 1.5625` (+1.2%): the machine is in the **quadratic
(unsaturated) torque regime** over this range, so the earlier `T ~ J` interpolation was
wrong. The 1.6 N.m target therefore sits at **J = 5.34**, not 4.8:

- copper loss **~119 W** (not ~97 W), winding rise **~45 K** (not ~37 K),
- copper-only efficiency **~81%** (not ~84%),
- phase current ~102 A at the design winding.

The 25% margin point (2.0 N.m) remains at J=6: 151 W, 57 K. The thermal verdict is
unchanged in kind - viable enclosed at the target, needs airflow at the margin point -
but the target point is 8 K hotter than previously reported.

## 5. Open issues (declared, not fixed)

1. **Maxwell vs co-energy disagree at the alignment axes** (and Maxwell changes 47% over
   1 deg at delta=45). Irrelevant to the MTPA number, but any cogging/ripple/torque-angle
   claim near the axes is unsupported until this is resolved.
2. **A real PF needs a saturated dq model**: perturb the current along each axis at the
   operating point and take `lambda_d = dW'/di_d`, `lambda_q = dW'/di_q` (4 extra solves
   with a pattern whose current angle is settable). That is the correct next analysis;
   the constant-L shortcut is dead.
3. The winding-probe asymmetry (section 2) should be removed by probing with a
   symmetric excitation (e.g. a two-phase equivalent) before any future inductance claim.

## 6. What this does not change

The envelope result (130/50 = 2.0 N.m at J=6; 120/74 = 2.0 N.m) rests on the Maxwell
torque, which the co-energy arbiter independently corroborates at -10%. The bridge-thickness
falsification and the Gate C family ceiling are untouched.
