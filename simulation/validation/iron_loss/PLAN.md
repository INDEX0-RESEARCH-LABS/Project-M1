# PLAN - first-order iron loss at the 130/50 point design

**Declared before running.** Script: `simulation/scripts/iron_loss.py`.
Log: `/tmp/opencode/m1/iron_loss.log`.

## Question

Efficiency is the only unquantified term in the 130/50 design (copper-only ~90%).
What does iron loss add, given that no measured loss curve exists for the candidate
steel and no purchase is allowed (D-009)?

## Method (chosen to avoid fabricating coefficients)

Public catalogs do **not** publish B-H curves for our grades, but they **do** publish
guaranteed loss (W/kg) by grade (`research/material_grades.md`, items 35-37). A grade
designation like M400-50A means **4.00 W/kg at 1.5 T, 50 Hz** by definition of
EN 10106, so the loss anchor is a *grade guarantee*, not an invented constant.

Electrical frequency at 3000 rpm with p=2 is **100 Hz** (3000 rpm = 50 Hz
*mechanical*), while the grade guarantee is at 50 Hz, so a frequency scale is needed.

> **CORRECTION made before any loss number was published (gates unchanged).** The first
> version of this plan said the electrical frequency was 50 Hz and skipped the frequency
> scale; that was the mechanical frequency. The first run (log kept) therefore understates
> iron loss by ~3x and is discarded. The scale needs the hysteresis/eddy split, which is
> not published, so it is declared as a band: eddy fraction at 50 Hz `s` in {0.3, 0.45, 0.6},
> giving a factor `(1-s)*2 + s*4` = 2.6-3.2 at 100 Hz.

    P_fe = sum over iron elements of  p_ref * [(1-s)*(f/50) + s*(f/50)^2]
                                       * (B_e / 1.5)^n * rho * A_e * L

with:
- `p_ref` in {3.3, 4.0, 5.3} W/kg  (M350-50A / M400-50A / M530-50A class guarantees -
  the candidate steel is unspecified, so the class range is the honest input)
- `n` in {1.6, 1.8, 2.0}  (hysteresis-dominated to eddy-dominated; a single exponent
  over 0.3-2.5 T is crude and is treated as a sensitivity, not a fit)
- `rho = 7650 kg/m3`
- `B_e` = per-element |B| from the same certified solve used for torque
  (J = 5.34 target, J = 6.0 margin, delta = 26.25 MTPA).

All 9 combinations are reported as a min/max band. A single point value is **not**
admissible output.

## Declared gates

- **F1 volume**: computed stator-iron area must match (stator annulus - 36 slot areas)
  within **5%**. Rotor-iron area must be less than its full annulus.
- **F2 functional**: the loss functional must reproduce `B^n` scaling exactly on a
  synthetic uniform field (rel. error < 1e-9) for each n.
- **F3 band**: report min/max over the 9 combos; the band width must be stated.
- **F4 interpretation rule (declared now, before the number is known)**:
  - if `P_fe(median) < 0.5 * P_cu` at the target, the efficiency claim becomes
    ">85% including iron" and the thermal conclusion stands;
  - if `0.5 <= P_fe/P_cu < 1.0`, efficiency falls to ~80-85% and iron loss must be
    carried in the thermal budget;
  - if `P_fe >= P_cu`, the efficiency story fails and the frame/steel becomes a
    design blocker, not a detail.

## Explicit non-goals / limitations

- **Rotor harmonic loss is not modelled.** In the rotor frame the fundamental flux is
  quasi-static; the real rotor loss is driven by slot-harmonic ripple at
  ~36 x 50 Hz. Applying the 50 Hz formula to the rotor's peak B is therefore an
  **upper bound**, not an estimate. Reported separately, never summed silently.
- No excess-loss (anomalous) term, no rotational-loss correction, no building factor.
  Real laminated cores typically lose more than the Epstein guarantee, so the result
  is a **lower bound on the steel's contribution** once assembled.
- The steel grade is a proxy (M-43 bracket vs M350/400/530-50A class); a real number
  requires the purchased steel's curve or a bench test (both F-class, D-009).
