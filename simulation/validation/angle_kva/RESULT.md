# Current angle: torque per kVA vs torque per amp

**Status: RESULT. Gates P1-P3 were declared in `PLAN.md` before the run.** Measured
2026-10-23, S6 rotor, J=5.21, 2 deg grid over the 30 deg period, 1536/4 mesh.

## Verdict

**26.0 deg is already the right angle, and the angle is not a free lever on the 48 V
constraint.** The VA-optimal angle is far below MTPA, but buying kVA there costs current:
at 14 deg the apparent power at 1.6 N.m falls 20% while the phase current rises 28%.
Since a 48 V traction rail is limited in amps (wiring, MOSFET conduction, copper) rather
than in volt-amperes, that trade is a loss. No angle change is adopted.

Two things are nevertheless answered and were open before this run:

- **26.0 deg is mean-torque-optimal**, not just instantaneous-optimal. The mean torque
  peaks at 26 within the 6 deg sampling (1.192 N.m at 26 against 1.164 at 20 and 1.029 at
  32). Choosing the angle on an instantaneous basis happened to give the mean-optimal
  angle.
- **Power factor can be raised by ~26% with the current angle** (0.398 -> 0.502) and
  apparent power per N.m still only falls 20%, because the copper loss per N.m rises with
  it. PF and current trade against each other almost one-for-one. This is the same
  statement as D-023's `S/T = (omega + P_cu/T)/PF`.

## Gate outcomes

| id | gate | result |
|---|---|---|
| P2 | 26 deg reproduces the D-022 sweep (T 1.1918, S_max 0.997 kVA, 1%) | **PASS**: 1.1918 and 0.997 kVA, exact |
| P3 | mean torque peaks near 26 deg | **PASS**: 26 > 20 > 32, peak inside the sampled span |
| P1 | adopt an angle only if S at 1.6 N.m drops >= 5% and P_cu <= 40 W | **PASSES ON PAPER (14 deg, 20 deg), REJECTED ON THE MERIT** - see below |

P1 as written was a VA gate, and it fires. It is overridden deliberately, not silently:
the gate did not ask which rail quantity binds. That omission is the finding.

## Measurements

All figures scaled to 1.60 N.m mean at 3000 rpm by the fixed-angle SynRM law
(T proportional to i^2; S and P_cu proportional to i^2). ESTIMATE on the absolute values,
measurement on the ranking.

| current angle | T_mean at J=5.21 | i / i(26) | P_cu at 1.6 N.m | S mean | S max | cycle PF | S vs 26 deg |
|---|---|---|---|---|---|---|---|
| 14 deg | 0.977 N.m | 1.280 | 37.2 W | **1.025 kVA** | **1.076 kVA** | **0.502** | **-19.6%** |
| 20 deg | 1.164 N.m | 1.172 | 31.3 W | 1.094 | 1.141 | 0.468 | -14.8% |
| **26 deg** | **1.192 N.m** | 1.000 | **30.5 W** | 1.287 | 1.339 | 0.398 | 0.0% |
| 32 deg | 1.029 N.m | 1.247 | 35.4 W | 1.707 | 1.757 | 0.306 | +31.3% |
| 38 deg | 0.564 N.m | 1.684 | 64.5 W | 3.329 | 3.411 | 0.166 | +154.8% |

Cross-check: the 26 deg row scaled to 1.6 N.m gives 1.29 mean / 1.34 max kVA, which
reproduces D-023's independent estimate (1.29 / 1.32) to 1.5%. Two different routes to the
same number.

## Why the low-angle corner is a trap

At 14 deg the flux linkage is smaller for the same torque, so the terminal voltage drops
and with it the apparent power. That is field-weakening, and it is the correct move when
the inverter has run out of volts while current is still available. It is the wrong move
here, because:

- the current rises 28% and copper loss 22% for the same shaft power;
- the machine is already at 5.21 A/mm2, the top of the normal TEFC band (D-022);
- a 48 V rail's practical limit is amperes, not VA - the VA number is a convenient
  summary, not the physical constraint.

The ratio that matters for the rail is therefore **amps per N.m**, and it is minimised at
26 deg by construction: that is what MTPA means. The mirror-image statement is that
apparent power per N.m can only be improved by raising saliency (a rotor change), not by
retuning the controller.

## Trend and what was not chased

S/T falls monotonically from 26 deg down to 14 deg, so the VA-optimal angle is somewhere
below 14 deg. It was not chased: the current penalty at 14 deg (+28%) already exceeds the
VA benefit (-20%), and the penalty only steepens as the angle drops further. A 8 deg run
would locate a minimum that is worse on the binding constraint.

## Limits

- 2 deg grid. Means are 3% low (D-021) and the comparison is like-for-like across angles,
  so the ranking stands; the absolutes inherit that bias and are labelled ESTIMATE.
- Linear scaling to 1.6 N.m ignores saturation, which is heavier at low angles. That
  *understates* the current penalty at 14 deg, so it strengthens the conclusion.
- Only mean torque and apparent power are compared. Torque ripple at other angles was not
  examined; if an angle were adopted, ripple would have to be re-certified there.
- The 48 V rail's constraint was assumed to be current. If the chosen inverter is in fact
  VA-rated, the 14 deg row becomes attractive and P1 as written should be revisited.
