# Current-angle study: torque per kVA, not torque per amp

**Status: PLAN, gates declared before the run (2026-10-23).**

## Question

D-022/D-023 established that apparent power per N.m is

    S / T = (omega + P_cu / T) / PF

so at 3,000 rpm the 48 V rail budget is set by power factor, and power factor depends on
the current angle. The current angle in every certification so far (26.0 deg) was chosen to
maximise torque per ampere. That is not the same objective: the d-axis current produces
flux, flux produces terminal voltage, and voltage is what the rail runs out of first. For a
voltage-limited machine the kVA-optimal angle is generally **below** MTPA - less d-axis
current, less flux, lower V-hat, at the cost of more current for the same torque.

So: at a fixed mean torque of 1.6 N.m, which angle costs the least apparent power, and what
does it cost in copper?

## Gates, declared before running

| id | gate | threshold |
|---|---|---|
| P1 | adoption | an alternative angle replaces 26.0 deg only if S at 1.6 N.m mean is **>= 5% lower** AND copper loss at 1.6 N.m stays **<= 40 W** (the current-route budget D-020 already accepted) |
| P2 | reproduction | the 26.0 deg case must reproduce the D-022 sweep: mean torque 1.1918 N.m and S_max 0.997 kVA (Faraday route), each within 1% |
| P3 | angle convention | mean torque must peak near 26 deg. If it peaks elsewhere or is monotone, the angle convention is wrong and the run is void |

Gate P1 is a decision gate; P2 and P3 are validity gates. A run that fails P3 is not
interpreted at all.

## Prediction (recorded so it can be wrong)

S/T is minimised **below** 26 deg, in the 18-24 deg region, because dropping the d-axis
current cuts the flux linkage roughly in proportion while the torque falls only as the
product i_d * i_q. If the minimum is at or above 26 deg, the prediction is wrong and the
reason matters: it would mean flux is not the binding term at this loading.

## Method

- `pf_cycle.py --delta-op <angle>`, 15 points over one 30 deg period at 2 deg, J = 5.21,
  D-014 rotor, 1536/4 mesh. S is turns-invariant, so the winding choice does not enter.
- Angles: 14, 20, 26, 32, 38 deg. 26.0 is already solved (D-022 sweep) and is reused.
- Scaling to 1.6 N.m uses the SynRM quadratic law at fixed angle, T proportional to i^2, so
  k = sqrt(1.6/T_mean), S scales as k^2 and P_cu as k^2. This is a linear-material
  extrapolation: labelled ESTIMATE, and the ranking is what is claimed, not the absolute.
- Reported per angle: T_mean, S_max, PF cycle, and S / P_cu at 1.6 N.m.

## Not claimed

- No new torque certification. The mean torque is a 2 deg figure (3% low) and is used only
  as a common basis across angles.
- Saturation is not re-fitted per angle; the quadratic scaling overestimates the current
  needed at low angles where the machine saturates harder.
- If the result points to an angle materially away from 26 deg, the follow-up is a 0.5 deg
  certification sweep at that angle, which is a separate run.

## Cost

4 new sweeps x 15 solves at ~45 s = ~11 min wall on 4 cores in parallel.
