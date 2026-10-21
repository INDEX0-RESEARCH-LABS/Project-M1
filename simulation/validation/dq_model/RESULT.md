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

> **SUPERSEDED by section 7.** A PF *is* now published (0.55), from the measured flux
> linkage and torque rather than from Ld/Lq. The VA estimate is ~1.0-1.25 kVA, not ~4 kVA.

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

> **SUPERSEDED by section 7.** The 119 W / 45 K / 81% figures above came from a
> peak-current-density phase error in `thermal_first_order.py` (loss 2x high). Corrected:
> target point ~53 W hot, ~20 K rise, ~90% copper-only.

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

## 7. CORRECTION (D-012 addendum 6): two unit errors; PF = 0.55; thermal halved

Found by checking the energy balance `P_elec = P_cu + T*w_mech` instead of trusting the
printed PF. It did not close (PF > 1), which traced to **two independent factor-2 errors**:

1. `dq_model.py` multiplied the torque by the **electrical** angular speed
   (`w_e = p*w_m` = 628 rad/s) instead of the mechanical one (314 rad/s), so `P_mech` was
   2x high. `T = 1.5p(lam_d i_q - lam_q i_d)` pairs with `w_mech`; `w_e` belongs only
   inside the back-EMF.
2. `thermal_first_order.py` used the FEM's **peak** slot current density as if it were
   RMS, so `P_cu` was 2x high and every rise was 2x high. Correct form:
   `P_cu = rho*(J_peak^2/2)*V_cu`, which equals `3*I_rms^2*R_ph` identically (asserted in
   the script).

Both are fixed. An independent arithmetic audit of 14 identities (w_m/w_e placement,
peak/RMS, 3-phase factors, copper-volume route) passes with max deviation 0.08%.

### Terminal state, model-independent

`lam_par` is the flux linkage along the current vector from the slot stream function
(alpha-axis projection `(2/3)(lam_a - 0.5 lam_b - 0.5 lam_c)`; phase-A is 2.1-2.5% higher,
i.e. the winding harmonics are small). `lam_perp = T/(1.5 p i)` comes from the measured
torque, so **no failed dq model enters this table**.

| J [A/mm2] | T [N.m] | i [A] | lam_par | lam_perp | abs(lam) | Vhat | S | PF |
|---|---|---|---|---|---|---|---|---|
| 4.8 | 1.279 | 91.7 | 7.88 mWb | 4.65 | 9.15 | 5.90 V | 811 VA | 0.543 |
| **5.34 (target)** | **1.592** | **102.1** | **8.68** | **5.20** | **10.12** | **6.52** | **999 VA** | **0.549** |
| 6.0 (margin) | 2.022 | 114.7 | 9.64 | 5.88 | 11.30 | 7.29 | 1253 VA | 0.555 |

The target lands at 1.59 N.m (-0.5% of 1.6) at J=5.34, as `T ~ J^2` predicted.

- **PF = 0.54-0.56**, not the withdrawn 0.25 (too pessimistic, it was a VA upper bound)
  and not the L-based 0.49-0.50/0.93 pair (failed model). For reference the L-based
  voltage is retained only as a diagnostic: it gives PF 0.49-0.50, ~10% below the
  model-independent value, which brackets the answer honestly.
- **1.0 kVA at the target**, 1.25 kVA at the margin point - a single ~1.2 kVA controller,
  not a 4 kVA one.
- **Voltage is not the constraint** (6.5-7.3 V against 26.3 V); **current is** (~100 A at
  this winding). The ~3x turns increase remains the lever that cuts current to ~35 A at
  identical copper loss.

### Thermal (corrected, enclosed h=25)

| point | P_cu hot | rise | copper-only efficiency |
|---|---|---|---|
| J=6 (2.0 N.m) | 68 W | 26 K | 90.3% |
| J=5.34 (1.6 N.m) | 53 W | 20 K | ~90% |
| J=6, still air | 75 W | 55 K | - |

Previously reported 151 W / 57 K / 81%: that was the peak-as-RMS error. Still air is
marginal but not hopeless (55 K, not 131 K); enclosed is comfortable. Iron loss is still
excluded, so efficiency remains an upper bound.

### Honest limits of this PF

It uses the Maxwell torque (corroborated by co-energy to 10%) and a flux linkage from the
slot stream function. It is **not** a saturated dq decomposition, and it is an
**ESTIMATE**, not a bench measurement. The open item from section 5.2 (true
`lam_d = dW'/di_d`, `lam_q = dW'/di_q`) is now optional rather than blocking: it would
decompose the same physics, not change the terminal VA by more than the 10% torque spread.
