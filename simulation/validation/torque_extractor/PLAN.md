# PLAN - is 1.592 N.m converged? (torque extractor check)

**Gates fixed before the run** (they were written in the script docstring at creation,
then this file; the run happened after both). Script:
`simulation/scripts/torque_mesh_convergence.py`. Log: `/tmp/opencode/m1/torque_mesh.log`.

## Trigger

The PF-vs-angle sweep (`validation/voltage_and_angle`) produced a torque curve that no
SynRM of this type should have: 1.592 N.m at 26.25 deg, 0.881 at 32 deg, 1.761 at 36 deg,
with 4-degree steps. A 40-50% swing in 4 deg is not torque ripple (q = 3 gives a few
percent). Re-solving the operating point on a finer mesh moved it -7.5%. So the headline
torque may be a mesh artifact, which would propagate into every absolute number
(P_cu at fixed torque, efficiency, PF, kVA, current).

## Method

At delta = 26.25 deg, J = 5.34 A/mm2 (the certified target), solve the same problem on a
mesh ladder and extract torque two ways:

- **Maxwell stress** on a circle in the airgap, as used everywhere so far
  (`torque_maxwell`, single sampling circle, 2880 points). Then repeated with
  `n_rings` in {1, 5, 9} and `r_spread = 0.16 mm`. Rings exist in the code precisely
  because the solver's B is element-wise constant: a single sampling radius can land on a
  high or low element, while the exact integral is radius-independent in a current-free
  annulus. Rings de-correlate that sampling noise.
- **Co-energy** `dW'/d(delta)` at fixed current (central difference, +/-0.5 deg,
  3072 rays / 10 gap rows). No gap-circle sampling at all, so it is the arbiter.

Mesh ladder: (1536 rays, 4 rows) = the certified mesh, (3072, 10), (4096, 10).

## Declared gates

- **E1 convergence**: torque must be stable within **3%** across the ladder. If not, the
  extractor is not converged and every absolute torque inherits the spread. (Ratios and
  torque-per-stack trends share the bias and are not invalidated by it.)
- **E2 ring averaging**: if rings change the answer by **>3%** at fixed mesh, the
  single-circle value is superseded by the ring average; a single-circle number is then
  not quotable.
- **E3 arbitration**: the adopted torque is the midpoint of the Maxwell ring average and
  the co-energy derivative. Neither route is adopted on mesh refinement alone. If the two
  routes disagree by more than 10%, the adopted value carries that as its band.
- **E4 consequence**: if the arbitrated torque at J=6 falls below **2.00 N.m**, the
  declared 25% envelope margin no longer holds at that current and `STATUS.md` must say
  so in the same commit.

## Non-goals

- No geometry change and no re-design. This is a measurement correction.
- No claim that the correction is exact: the deliverable is a best estimate plus a band,
  and a named fix (ring-averaged torque as the standard extractor).
