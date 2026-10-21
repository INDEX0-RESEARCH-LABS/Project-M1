# Anchor rotor-geometry upgrade — declared sweep (torque ceiling of OUR topology)

Status: declared BEFORE running (house rule). Gate list frozen below.
Script (to add): `simulation/scripts/rajini_rotor_upgrade.py`. Results → `RESULT.md` here.

## Question

The anchor sweep (corrected 2026-10-21 run) delivered 8.12 N·m/m at MTPA with the declared
barrier layout (3 q-centred barriers/pole, arc frac 0.62 of pole pitch, span 8.4 mm,
bridge 0.6 mm) — 13× below the anchor's implied 108 N·m/m (8 N·m @ 74 mm). Before blaming
the paper's claim, we must know: **is the deficit OUR declared layout, OUR excitation
interpretation, or the paper's number?** This sweep answers the design-space part.

## Declared rationale (from physics, before data)

Our declared barrier arc 0.62 (≈56° of the 90° pole pitch) is roughly DOUBLE the arc used
in high-performance SynRM designs (typically 25–40%). Wide barrier arcs choke the direct
(d)-axis pole iron; we expect torque to rise strongly as `barrier_angle_frac` drops.
Bmax at MTPA is already 2.45 T (deep saturation), which caps how much iron we can trade.

## Declared sweep (fixed: envelope, stack, steel M-43, excitation I_R as committed)

- `barrier_angle_frac` ∈ {0.30, 0.40, 0.50, 0.62}   (0.62 = the committed anchor layout)
- `barrier_radial_span` ∈ {6, 8.4, 12} mm           (8.4 = committed)
- `n_barriers` ∈ {2, 3}
- per config: delta ∈ {22.5, 26.25, 30}° (MTPA neighborhood from the anchor sweep), 1536 rays
- outputs per config: T/m, rotor iron fraction, Bmax, iters
- the best 2 configs by |T| get the full 7-point delta scan + a 3072-ray refinement (gates)

24 configs × 3 solves + refinements. n_barriers=2 uses the committed gap_frac (0.40).

## Gates (frozen)

- **U1** every solve converges.
- **U2** mesh region areas vs analytic ≤ 1%.
- **U3** refinement (3072 vs 1536 rays, same config & delta) ≤ 10% for the best configs.
- **U4** declared monotonicity observation: |T| increases as angle_frac decreases toward
  the iron-rich end (physics rationale above). Recorded as observation — if violated, we
  report it and investigate, it does not fail the run.

## Deliverable C (comparison back to the anchor)

For the best config: T/m, T @ 74 mm, iron fraction, Bmax, and the **excitation multiplier**
needed to reach 108 N·m/m (with the implied current density) — stated as a design
statement: "the declared topology reaches/does not reach the anchor target at declared
excitation; closing the gap requires X".
