# PLAN - the 48 V / 96 V decision, and whether current angle can buy PF

**Declared before running.** Scripts: `simulation/scripts/pf_angle_sweep.py`,
`tests/test_voltage_scaling.py`. Log: `/tmp/opencode/m1/pf_angle.log`.

## Why this exists

D-012 is blocked on one founder call: accept PF 0.53-0.58 (a ~1 kVA controller for
0.5 kW of shaft at 48 V), or move the pack to 96 V. The question was being asked as a
two-way choice. Before it is put to the founder, two things must be separated:

1. **What voltage actually buys.** Turns scaling at fixed slot AT is exact
   (`lambda ~ k`, `R ~ k^2`, `I ~ 1/k`), so apparent power `S = P/PF` is invariant.
   If that is true, 96 V buys *current* and *speed headroom*, not kVA, and the
   "1 kVA or 96 V" framing is a false binary. This is algebra on solved quantities,
   not a new field solve.
2. **Whether PF is a control choice.** All certified results sit at one rotor angle
   (delta = 26.25 deg, near maximum torque). PF is a function of the current angle,
   and nobody has checked whether another angle gives the same 0.5 kW for less
   apparent power. If it does, it is free: a controller setting, no hardware change.

## Method

Same certified field solve as `dq_model.py` (`solve_point`, 1536 rays, 4 gap rows),
J = 5.34 A/mm2 held fixed, rotor angle swept 12-44 deg in 10 steps (26.25 included).

Per angle, from that one solution:
- `T`, `lam_par` (slot stream function), `lam_perp = T/(1.5 p i)` (torque route),
- `Vhat`, `P_cu`, `PF = (P_cu + P_mech)/(1.5 Vhat i)` - identical to `dq_model.py`.

**Equal-output correction (the trap this plan is written to avoid).** PF at a lower
torque is trivially different because the power is lower. So every angle is also
scored at the *same* 0.5 kW shaft: required current from the measured `T ~ J^2`
(verified at 4.8/5.34/6.0), `lam_par ~ i^0.90` (fitted on the three certified points
at this angle), `lam_perp ~ i`, then `Vhat'`, `P_cu'`, `S' = 1.5 Vhat' i'`.
All equal-output numbers are **ESTIMATE** (exponent scaling), the fixed-J numbers are
**SOLVED**.

The pack/voltage table is arithmetic on the winding table (`winding_spec_v1.md`
section 3): `k` turns multiplier, `Vhat ~ k`, `I ~ 1/k`, `R ~ k^2`, speed ceiling
`~ 1/k`, `S` invariant. No prices are invented; only cell counts and currents are
reported.

## Declared gates

- **A1 regression**: at delta = 26.25 deg the sweep must reproduce
  `T = 1.592 N.m +/- 2%` and `PF` inside 0.53-0.58. If not, the sweep harness is
  wrong and nothing below is reported.
- **A2 angle lever (rule fixed now)**: an angle change is **adopted** only if
  `PF(at 0.5 kW) >= PF(ref) + 0.03` **and** `T(J=5.34) >= 0.98 * 1.592 N.m`.
  Otherwise the honest output is "no control-angle lever; PF is a rotor property",
  and the answer to the founder is a topology decision, not a setting.
- **A3 band**: the PF gain must exceed the 0.05 width of the published PF bracket
  (0.53-0.58) to be called real. If it lands inside the bracket, it is recorded as
  "not resolvable at this model fidelity", not as a win.
- **V1 scaling identities**: `V ~ k`, `I ~ 1/k`, `R ~ k^2`, `P_cu` invariant,
  speed ceiling `~ 1/k`, `S` invariant, each pinned at 1e-12 in
  `tests/test_voltage_scaling.py`.
- **V2 no silent rewind**: any 96 V column that halves current must state the turns
  count and the wire it implies, and must state that slot fill is unchanged only if
  the copper area is unchanged.

## Explicit non-goals

- No new rotor geometry. Raising saliency is the other PF lever, but it is a barrier
  re-design with its own certification and is **not** run here; if A2 fails, it is
  proposed, not assumed.
- No cost figures. Controller and pack prices are quotes (F-class, D-009).
- No claim about field weakening beyond the speed ceiling already derived; this
  SynRM is a poor field-weakening machine and that is unchanged.
