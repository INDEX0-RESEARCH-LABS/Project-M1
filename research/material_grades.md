# Material grades in the Gate B validation anchors

Recorded 2026-10-20. Both entries are **quoted from full text**, not inferred.
Purpose: prevent silently substituting our local library steel (M-19) for the
steel an anchor actually used, which would make a "torque match" meaningless.

## Kachapornkul et al. 2022 — SRM anchor (L14)

**DOI:** 10.3390/en15030694 · Energies 15(3):694 · full text (CC BY)

> "The silicon steel with a thickness of 0.35 mm (35A300) was used and its BH
> curve was used for analysis in the simulation. […] the 35A300 in JIS, i.e., a
> general low-loss silicon steel, was used. This steel has a thickness of
> 0.35 mm and is equal to 36F168, 300, and V300-35A in AISI, BS, and DIN,
> respectively." — p. 6

- **Grade:** 35A300 (JIS)
- **Equivalent designations:** AISI 36F168 · BS 300 · DIN V300-35A
- **Thickness:** 0.35 mm
- **Airgap used:** 0.30 mm
- **Stated loss class:** "general low-loss", 3.00 W/kg at 50 Hz / 1.5 T (the
  "300" in JIS 35A300 denotes loss ×100; **not** independently verified here)
- **Machine:** 3.5 kW, 3-phase 6/4 pole SRM, benchmarked on a test rig to ~82%
  system efficiency. Note this is 3.5 kW — **above** our 0.5–1 kW target band.

## Rajini et al. 2024 — SynRM anchor (L18)

**DOI:** 10.3934/energy.2024049 · AIMS Energy 12(5):1027–1053 · full text (CC BY)

> Stator/rotor core material … M1000-65A
> "The flux saturation is 2.1 T, for the chosen electromagnetic steel,
> M1000-65A. Space factor/slot fill factor is kept at 40%." — §4.1

Also, on fabrication:

> "…to cut Cold-Rolled Non-Grain-Oriented (CRNO) steel." — §5

- **Grade:** M1000-65A (CRNO)
- **Thickness:** 0.65 mm (implied by the grade designation; **not** stated in text)
- **Loss class:** 10.00 W/kg at 50 Hz / 1.5 T (implied by designation, not stated)
- **Assumed saturation:** 2.1 T
- **Machine:** 1.2 kW FASRM (ferrite-assisted SynRM) prototype, 159 mm stator OD,
  64 mm stack, 8 N·m, 6 A/mm² continuous, 40% slot fill, Indian drive cycle.
  Same power class as our target — the closer anchor.
- The paper compares 6 topologies; **SyncRelM and FASRM were judged superior**,
  and the prototype built was the FASRM (ferrite-assisted), *not* the pure
  SynRM. A pure-SynRM result is FEA-only in that paper.

## The finding that matters

The two anchors do **not** use the same steel. 35A300 (0.35 mm, low-loss, thin)
and M1000-65A (0.65 mm, high-loss, thick) differ by roughly a factor of 3 in
loss class and by 2× in lamination thickness. Thinner, lower-loss steel is the
higher-performance material.

Consequences for Gate B:
1. A torque match must be run per-anchor with that anchor's own steel. One curve
   cannot validate both machines.
2. Neither grade's B-H curve exists in our local FEMM library. M-19 was used for
   solver validation only and must not be substituted.
3. M1000-65A is a *low-grade, high-loss* steel — worth noting that Rajini's
   1.2 kW result was achieved with it. Any prototype cost model should ask
   whether 35A300-class steel is affordable at our volume, because it is both
   better and (in India, at low volume) plausibly harder to source.

## Status
- [x] Grades confirmed from full text for both anchors
- [ ] Citable B-H curve for 35A300
- [ ] Citable B-H curve for M1000-65A
- [ ] Confirm the JIS loss-class readings against a standards source (do not
      rely on the grade-number convention alone)
