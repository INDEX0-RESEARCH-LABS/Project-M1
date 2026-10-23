# PF and kVA over one torque period

**Status: DIAGNOSTIC, no gate claimed.** This sweep answers one question - is the
quoted power factor a property of the machine, or of the single rotor angle it was
measured at? It is the third quantity to be asked that question, after torque
(D-018/D-021) and efficiency (D-020).

No pass criterion was declared before running, so none is claimed here. That is a
deliberate omission, recorded rather than hidden: the sweep was framed as a bracket
exercise, not a certification.

Script: `simulation/scripts/pf_cycle.py`. Data: `/tmp/opencode/m1/pf_cycle.csv`,
log `/tmp/opencode/m1/pf_cycle.log`.

## 1. Why a cycle basis is required

`dq_model.pf_check` computes

    PF = (P_cu + T(delta_op) * omega_m) / (1.5 * Vhat(delta_op) * I)

All three quantities are taken at one rotor angle. In a drive the current magnitude
and angle are held constant by the controller while the rotor turns, so the
electromagnetic torque - and with it the real power - varies over the slot period,
while the apparent power does not fall with it. A single position therefore reports
the peak-angle PF, for the same reason a single position reports the peak-angle
efficiency: numerator and denominator do not peak together.

## 2. Method

15 points over the 30 deg mechanical period (2 deg step, 1536 rays / 4 gap rows,
J = 5.21 A/mm2, D-014 rotor). The phase currents are rotated with the rotor so the
current angle stays fixed (`torque_ripple.moving_pattern`). Per point: annulus
torque (D-016), `lam_alpha`, `lam_beta` from the slot stream function, and the two
V-hat routes already in use:

- `geo`: lam_beta from the phase flux linkages (Faraday, model-independent).
- `tq`: lam_perp implied by the torque, `lam_perp = -T / (1.5 p i)`.

`S = 1.5 * Vhat * I` and `PF = (P_cu + P_mech) / S`. Both S and PF are
turns-invariant (`Vhat` scales with N_c, `I` with 1/N_c), so the results do not
depend on which winding revision is being quoted.

Two corrections to the raw sweep before anything is read off it:

- The 2 deg grid reads the mean torque 3.1% low (1.1918 vs the certified 1.2305),
  the known D-021 quadrature error. `P_mech` is therefore evaluated at the certified
  mean, not at the grid mean. `P_cu` is grid-independent (22.75 W).
- Values labelled `k=2` multiply V-hat by two and divide current by two, to express
  the same solution at the D-013 winding.

## 3. Results

At the certified operating point: `P_mech` 386.6 W, `P_cu` 22.75 W, `P_in` 409.3 W.

| | route `geo` | route `tq` |
|---|---|---|
| V-hat over the cycle (k=1) | 6.22 - 6.68 V (mean 6.42) | 2.48 - 6.98 V (mean 4.82) |
| V-hat, point value at 26.0 deg (k=2) | 12.54 V | 13.46 V |
| V-hat, cycle maximum (k=2) | 13.35 V | 13.95 V |
| S over the cycle | 0.929 - 0.997 kVA | 0.371 - 1.042 kVA |
| instantaneous PF | 0.213 - 0.608 | 0.275 - 0.928 |
| **cycle PF, mean P_in / mean S** | **0.427** | **0.569** |
| **cycle PF, mean P_in / max S** | **0.410** | **0.393** |
| voltage ceiling from max V-hat | 5,910 rpm | 5,660 rpm |
| voltage ceiling from point V-hat | 6,300 rpm | 5,870 rpm |

Loading anchors, same state:

| quantity | value | basis |
|---|---|---|
| rotor volume | 669.0 cm3 | pi * r^2 * L |
| air-gap shear, mean | **0.89 kPa** | T / (2 * pi * r^2 * L) |
| air-gap shear, peak | **1.30 kPa** | same, at the torque maximum |
| current density | 5.21 A/mm2 | top of the 3-5 A/mm2 TEFC band |

## 4. What the sweep says

**F1. PF is a cycle quantity, and 0.578 is its peak-angle value.** On the rail-sizing
basis (mean real power against the largest apparent power in the period) PF is
**0.39 - 0.43**, not 0.578. The 0.578 figure appears at 26.0 deg - the angle chosen
for maximum instantaneous torque - where the machine is momentarily at its best ratio
of real to apparent power. This is the same error class as the 3.2% torque mean and
the 2.6 pp efficiency gap, and it is larger than either: **a factor of 1.35 - 1.48.**

**F2. The apparent-power number itself barely moves.** The Faraday route puts S in a
3.5% band over the whole period (0.929 - 0.997 kVA). The rail does not see a spiky
kVA demand, so "1.06 kVA" survives as a sizing figure. What does not survive is the
work it buys: 409 W of real input for 387 W of shaft, where the point PF implied
~556 W of shaft for the same kVA.

**F3. The voltage ceiling is lower than the quoted 6,840 rpm.** The 11.5 V / 6,840 rpm
pair traces to the target-point re-solve and the 0.86 kVA / 0.633 PF triplet - the
state D-017 superseded. Recomputed on the Faraday and torque routes at k=2, V-hat is
**12.5 - 14.0 V** at 3,000 rpm, and the worst rotor angle adds 4 - 6.5%. Against the
26.3 V ceiling that is **5,660 - 6,300 rpm**, with the cycle-maximum basis giving
**5,160 - 5,670 rpm**. The STATUS row still carries the superseded 11.5 V.

An independent check already in the repo agrees: `tests/test_voltage_scaling.py` pins
V-hat = 6.52 V at k=1 (that is 13.04 V at k=2), which gives a 6,057 rpm ceiling - so the
6,840 figure was inconsistent with the project's own voltage-scaling fixture.

**F4. The machine is magnetically under-loaded and electrically normal.** 0.89 kPa of
air-gap shear is below the "a few kPa" band MIT's 6.685 ch.1 quotes for small
machines, and 4 - 10x below a 0.1 - 5 kW machine's usual 3 - 7 kPa. Meanwhile 5.21
A/mm2 sits at the top of the normal TEFC range. The iron is not the constraint; the
48 V rail is. This is an independent vote for D-020's choice to buy the deficit with
stack length rather than current: more iron is free magnetically, more current is
expensive electrically.

**F5. The published SynRM comparison is unfavourable but not like-for-like.** Measured
small SynRMs run PF 0.60 - 0.65 (Ozcelik et al., Energies 12(11):2190, Table 18; ABB
ACH550-PHPB11U-EN gives 0.64 at 2 HP). Our cycle PF of 0.39 - 0.43 sits well below
that, consistent with a saliency ratio near 4 against the 7 - 14 of a good
transverse-laminated rotor. Caveat: those figures are at rated thermal load, ours at
0.89 kPa.

## 5. What this changes

- The founder's kVA question needs restating: ~1.0 kVA of apparent power for 387 W
  of shaft at PF ~0.40, not 0.578. The rail budget itself is unchanged; the
  efficiency of every kVA delivered is not.
- The speed ceiling is a **bracket 5,200 - 6,300 rpm**, not a point at 6,840. D-020's
  stack route inherits the same proportional penalty: 65.5 mm gives roughly
  **4,000 - 4,800 rpm**, not 5,260. Any gear-ratio commitment should be made against
  the bracket, and the voltage row in STATUS should stop quoting 11.5 V.
- D-017's *conclusion* stands. S6 beats the baseline at the same angle and current;
  both numbers carry the same peak-angle bias, so the like-for-like comparison is
  still valid. Only the absolute values are superseded.

## 6. Limits

- Absolute V-hat depends on the flux-linkage route, and the two routes disagree by
  33% at the point (D-017's open item). The bracket in F3 is that disagreement
  propagated, not a measured spread.
- Saturation is not varied with angle: the BH curve is applied pointwise, so
  `lam_alpha` is solved, not interpolated. The smooth Faraday V-hat is the more
  credible route for voltage; the torque-implied route inherits the torque notches
  into a quantity that should not have them. That is why F1 uses it only as the
  lower bracket.
- The cycle PF is a *drive* number assuming constant current magnitude and angle. A
  controller that varies the angle through the period could recover part of the gap;
  the size of that recovery is not modelled.
- 1536/4 mesh, 2 deg grid: good enough for ratios, not for quotable absolutes. The
  torque mean is carried over from the certified 0.5 deg curve.
- **The 33% flux-vs-torque gap was probed and remains unresolved.** A linear-material run
  should satisfy `lam_beta = -T/(1.5 p i)` exactly; over two permeabilities and two current
  levels the ratio came out 0.83 - 1.11 (sign flips with mu_r), while the annulus
  estimator's own four-band spread was 17 - 74%. The effect is smaller than the estimator's
  uncertainty at those torque levels, so the probe is inconclusive and was not pursued.
  Note it used the baseline geometry by mistake (`dq_model` has no CAND), so it is not
  evidence about S6 either way. The gap needs a certified torque error bar at the operating
  point (4096/20 plus co-energy), not more sweeps.
