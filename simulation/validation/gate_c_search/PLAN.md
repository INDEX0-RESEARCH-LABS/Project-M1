# Gate C search — declared optimization pass over the v1 baseline neighborhood

Status: declared BEFORE running (house rule). Script (to add):
`simulation/scripts/gate_c_search.py`. Results → `RESULT.md` here.

## Objective (stated metric, frozen)

Maximize **|T| per metre of active stack at the declared excitation** (equal installed Cu,
equal fill 0.4, J = 6 A/mm², anchor envelope, M-43 Steel 1536-ray mesh) — the same metric
as D-008's comparison and the rotor-upgrade sweep, for consistency. Reported secondary
metric: T per active volume (1.437 L).

Baseline to beat (frozen, same mesh level): **9.0950 N·m/m** (D-010 v1 layout,
delta 26.25, 1536 rays; COMPLETED baseline = 8.1235 at 1536 for the v0 memory).

**Improvement gate: the winner must beat the v1 baseline by ≥ +10%** at the same mesh
level (i.e. ≥ 10.00 N·m/m at 1536).

## Declared search space (rationale: the rotor-upgrade sweep's monotone trends,
extended at their edges; NOT a random exploration)

- `barrier_radial_span` ∈ {12, 16, 20} mm   (sweep showed 6→12 monotone rise)
- `barrier_angle_frac` ∈ {0.62, 0.70}       (0.62 won; probed one step wider)
- `bridge` ∈ {0.6, 0.4} mm                  (thinner surface bridge = less q-shunt)
- `n_barriers` = 2 (frozen — 2 beat 3 in every member family)

12 configs. Per config: delta scan {10, 17.5, 25, 32.5, 40} at 1536 rays — wider than the
rotor-upgrade scan (its lesson: MTPA angles MOVE when the layout changes, so a 3-point
window understates iron-shifted families) — then ±3.75° refinement around each config's
best delta, and a 3072-ray solve at the winner's MTPA.

## Gates (frozen)

- **C1** every solve converges.
- **C2** region areas vs analytic ≤ 1% for every solve.
- **C3** winner's 3072 vs its 1536 value ≤ 10%.
- **C4** independent-extraction consistency on the winner: the multi-ring extractor
  (`n_rings=9, r_spread = 0.5·(r_bore − r_rotor)/2`) vs the search's single-ring values
  differ by ≤ 15%. NOT used for selection — verification only.
- **C5** independent re-check of the winner (ROADMAP gate-C language): the winner is
  re-solved with re-built mesh + 3072 rays + multi-ring extraction in a code path not
  used by the search loop; improvement claim is based on those numbers, not the
  search-loop numbers.

## Sanity / honesty notes (declared)

- All candidates keep the D-010 stator, envelope, Cu, excitation: wins are design-space,
  not excitation, improvements.
- The anchor-target lesson (×12.7 excitation gap) frames expectations: the search
  improves the phase-0 baseline, it does NOT close the anchor-paper gap; +10% is the
  gate, not +1200%.
- If C5 finds a materially higher torque than the search's, the search is re-run before
  any claim — no post-hoc swapping.
