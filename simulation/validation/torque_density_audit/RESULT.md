# RESULT — torque-density audit (one solve + post-processing)

**Script:** `simulation/scripts/torque_density_audit.py` (log: `/tmp/opencode/m1/torque_density_audit.log`).
**Method and interpretation rule:** frozen in `PLAN.md` before running.
**Point:** anchor frame (bore 92.10 mm, rotor 91.06 mm, gap 0.52 mm), delta = 26.25 deg,
3072 / rows4, M-43 Steel, J = 6 A/mm^2, fill 0.40.

## Measured

| quantity | value |
|---|---|
| solve | converged, 18 Newton iters, Bmax = 2.47 T (bridge saturation) |
| **T_fem** | **7.52 N.m/m** (depth 1 m) |
| MMF pattern | balanced (net AT = 0), \|AT\| sum = 1939 A |
| dominant MMF harmonic | **n = 2 pole pairs = MATCH** (4-pole); next: n=10 (10.1 A), n=14 (5.9 A) |
| fundamental MMF | Fhat_p = 222.2 A |
| electric loading | A1 = p*Fhat/r = **9.70 kA/m** |
| armature-only gap flux | mu0*Fhat/g = 0.537 T |
| measured gap flux | Bmean = 0.166 T, Bmax = 0.522 T, **Bhat_2 = 0.269 T** (about half the armature-only value: saturation + barrier/leakage) |
| textbook shear | sigma = 0.5*A1*Bhat_2 = **1.305 kPa** |
| textbook torque | T_sizing = (pi/2) D^2 sigma = **17.38 N.m/m** |
| **ratio** | **T_fem / T_sizing = 0.433** |

## Verdict (per the frozen rule)

1. **The excitation convention is correct.** The dominant MMF harmonic is the machine's
   pole-pair order (p = 2). The earlier worry that `d_pattern()` was not 4-pole is closed.
2. **T_fem / T_sizing = 0.43 >= 0.2** -> third branch of the rule: **no anomaly**. Classic
   sizing gives 17.4 N.m/m at the model's own A1 and B1; the SynRM delivers 7.5 N.m/m,
   i.e. 43% utilization. A reluctance machine with a partly-aligned field (delta = 26 deg)
   and a bridge-saturated rotor is expected to sit below the ideal quadrature product.
   There is **no order-of-magnitude solver/excitation defect** to chase.
3. **The ~100 N.m/m expectation that motivated this audit was an arithmetic error on my
   part** (I had used |AT|-sum/circumference as the fundamental electric loading, which
   double counts). The correct fundamental loading at this operating point is 9.7 kA/m,
   and it reproduces the FEM torque to within the normal utilization factor. Recorded
   here so the number is not re-invented later.

## What this does to the anchor gap

The anchor's 8 N.m at 74 mm needs **T/m = 108.1**, i.e. **14.4x** the torque this model
produces at the same stated J, fill and envelope (the campaign's own rotor-upgrade sweep
found 12.7x on its slightly better 8.53 N.m/m point, i.e. 76 A/mm^2 -- the two agree once
the same T/m is used, so this audit confirms that arithmetic from a different direction). Since T ~ A1*B1 and A1 ~ J, closing that
gap by excitation alone needs roughly J ~ 86 A/mm^2 at the stated 40% fill (B is already at
2.47 T in the bridges, so it cannot be recovered by flux alone).

Honest statement of what can and cannot be concluded:

- **Can conclude:** with the paper's *stated* parameters (6 A/mm^2, 40% fill, 74 mm, their
  derived bore) and *our* barrier layout, the parameter-consistent torque is 0.56 N.m, not
  8 N.m. So the campaign's 12.7x discrepancy is **not evidence of a solver defect**; it is
  at least in large part a source-parameter inconsistency (or an operating point far above
  the stated J).
- **Cannot conclude:** that their machine cannot make 8 N.m. Their unpublished rotor
  geometry may have far higher saliency/utilization than ours. D-004 (<5% replication)
  remains unexecutable and the INDICATIVE +/-25% label on their 8 N.m stays.

## Consequence for D-012

The "~4x density gap" narrative is re-scoped: at J = 6 A/mm^2 continuous the certified
machine sits at a **normal** utilization (0.43 of textbook shear), and the binding variable
is **electric loading (current density)**, not a mysterious loss. Torque density scales
with A1 ~ J; the continuous target is therefore a **thermal/current-density** question plus
a **frame-size** question, both of which are engineering choices, not blockers.

This also means the earlier 36-candidate scan was pessimistic on windability (series-only
winding model). See the amended `envelope_redesign_proposal.md` and the `paths` axis added
to `envelope_sizing.py`.
