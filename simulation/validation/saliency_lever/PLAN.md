# PLAN - can rotor geometry buy power factor? (saliency screen)

**Declared before running.** Script: `simulation/scripts/saliency_screen.py`.
Log: `/tmp/opencode/m1/saliency_screen.log`.

## Question

`STATUS.md` says the blocker is PF 0.49-0.54. PF in a SynRM is set by saliency
`xi = Ld/Lq`; the certified rotor measures **xi = 1.85**, which is low for a multi-barrier
SynRM (well-designed rotors reach 4-6). Gate C (D-011) swept this barrier family for
**torque** and found it flat, but it never reported saliency, and torque and PF are not the
same objective. So: does any configuration in this family raise xi enough to move PF, at
acceptable torque?

This is a screen, not a design: it exists to decide whether a rotor rework is worth
funding in compute, or whether PF is a topology dead end at this frame size.

## Method

Same certified solver and extractor as `dq_model.py` (1536 rays, 4 gap rows, single
circle), J = 5.34 A/mm2, three solves per configuration:

- delta = 45 deg -> Ld, delta = 0 deg -> Lq (the certified dq protocol),
- delta = 26.25 deg -> torque and PF (the certified operating point).

| id | barriers | angular frac | rib (iron) frac |
|---|---|---|---|
| BASE | 3 | 0.62 | 0.40 |
| V1 | 4 | 0.62 | 0.25 |
| V2 | 5 | 0.62 | 0.25 |
| V3 | 4 | 0.75 | 0.25 |
| V4 | 3 | 0.75 | 0.20 |

Span (10.4 mm at this bore) and bridge (0.6 mm) are held. Each variant trades d-axis iron
for q-axis blockage, which is exactly the saliency lever: more, thinner barriers should
raise Ld/Lq, but too much barrier area lowers Ld and torque.

## Declared gates

- **S1 regression**: BASE must reproduce xi = 1.85 +/-5% and T = 1.592 N.m +/-2% under
  the same extractor. If not, the harness is wrong and nothing else is reported.
- **S2**: report xi, Ld, Lq, T, PF for all five configurations.
- **S3 candidate rule (fixed now)**: a variant is a candidate only if
  **xi >= 2.5** AND **T >= 0.95 x BASE** AND **PF >= PF_BASE + 0.03**.
  If no variant qualifies, the honest output is "this barrier family is exhausted for PF
  as well", which closes the geometry route for the founder decision.
- **S4 no absolute adoption**: screen numbers share the -9% extractor bias
  (`torque_extractor/RESULT.md`). Only same-extractor comparisons are quoted; a candidate
  needs a ring-averaged, finer-gap certification solve before any absolute claim.
- **S5 saturation**: all comparisons are at the operating current. A variant that only
  wins at low current is not a win (the machine runs at J ~ 5.3-5.6).

## Non-goals

- No new topology (pole count, axial lamination, EESM). Those are real options, but they
  are outside this frame's certification and are listed for the founder, not solved here.
- No thermal or iron-loss update: both follow the torque and flux, and a candidate would
  be re-run through those scripts only if it passes S3.
