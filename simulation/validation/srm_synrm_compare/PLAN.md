AMENDMENT 3 (2026-10-21, after amendment 2's smoke runs):
the phase-A winding was all-poles-same-polarity; classic 12/8 wiring is N,S,N,S per
phase (flux closes pole -> rotor -> opposite pole). Fixed before any comparison too.
Also, the precomputed "aligned at 37.5 deg" phase bookkeeping was wrong (half a rotor
pole off); aligned/unaligned are now defined EMPIRICALLY as argmax/argmin of the
measured phase flux-linkage curve lambda(phi) over one 90 deg period, and gate G3 is
re-declared as |T(phi_lmax)| <= 20% peak and |T(phi_lmin)| <= 20% peak. The full
coarse-mesh lambda+torque scan (0..90 deg, 5 deg steps) runs BEFORE the fine sweeps;
the fine multi-ring runs happen only at the empirically located peak and zeros.

AMENDMENT 2 (2026-10-21, after the 12 mm re-run ALSO produced ~zero torque):
root cause diagnosed from the field map + flux linkage: the declared 2 mm rotor pole tip
(bridge) is a CONTINUOUS iron sleeve around the whole rotor surface (the barrier band
starts below it), which shunts the flux laterally — the rotor saw from the gap is a smooth
iron cylinder; lambda varies by ~1e-4 with rotor angle. For an SRM the rotor slots must
open AT the surface: pole-tip bridge removed (bridge=0), slot depth 12 mm kept. Both
failed sweeps are kept on record; nothing from them is used in the comparison.

AMENDMENT (2026-10-21, made after the first sweep, BEFORE any comparison was drawn):
the declared rotor slot depth 5 mm produced negligible saliency (peak 0.0201 N·m/m —
shallow slots barely perturb the rotor flux path, so L_a ≈ L_u). Amended to 12 mm
(typical for a 45.5 mm rotor). The failed-declaration sweep is kept on record in
`first_sweep shallow5mm.log`; nothing from it is used in the comparison below.

# SRM vs SynRM — same-envelope indicative comparison

Status: plan declared BEFORE running (house rule). Results will be written to RESULT.md
here once gates are evaluated. Script: `simulation/scripts/srm_model.py`.

## Scope & honesty labels

INDICATIVE comparison (±25%-class gates). Not a D-004 replication. Both machines are
our declared designs; the comparison ratio is the deliverable, not absolute torque.

## Declared common envelope

| quantity | value | note |
|---|---|---|
| stator OD | 159.0 mm | Rajini anchor envelope (committed) |
| bore | 92.075 mm | anchor value |
| airgap | 0.52 mm | anchor value |
| shaft OD | 24 mm | anchor value |
| stack L | 74 mm | anchor value |
| steel | M-43 bracket (1006 optional) | anchor bracket |
| conductor | J_CU = 6 A/mm², fill 0.40 | anchor values, energized slots only |

## Declared machines

- **SynRM**: exactly the committed anchor geometry (36 slots, 3 q-centred barriers/pole,
  span 8.4 mm, bridge 0.6 mm, I_R excitation). Reference numbers come from the completed
  anchor sweep (MTPA T/m = 7.6911 → 0.569 N·m @ 74 mm). No re-run needed.
- **SRM 12/8**: 12 stator slots with salient poles, 8 rotor poles modelled as rotor
  slots (the "barrier" machinery with rotor_n_poles=8 — a rotor slot *is* the air
  region in the rotor; semantic reuse, not a new classifier).
  - stator pole tip: opening 12 mm arc at bore ⇒ pole tip ≈ 15° arc (= half pitch).
  - stator slot half-angle at bottom: 0.55·pitch (same slot code as SynRM).
  - stator slot depth: solved so TOTAL slot (copper) area = SynRM's total slot area
    ⇒ equal installed copper per 74 mm stack. Declared, not tuned after results.
  - rotor slots: arc 25° (frac 0.556 of 45° pitch), depth 12 mm, slots OPEN at the
    rotor surface (pole-tip bridge removed; amendment 2 above).
  - excitation: ONE phase (4 stator poles, slots (0,1),(3,4),(6,7),(9,10)) energized,
    ±J_CU·FILL in 8 of 12 slots — the true instantaneous SRM snapshot.
- **Declared caveat (thermal):** the SRM runs this excitation 1/3 duty in continuous
  operation; at equal installed copper its thermal torque is represented by the
  single-phase snapshot only for peak-torque purposes. This is printed with results.

## Gates (all pass criteria frozen before the sweep)

- **G1** all SRM solves converge (Newton, every rotor position).
- **G2** SRM mesh region areas vs analytic ≤ 1% (same check class as anchor R1).
- **G3** torque curve symmetry: |T(aligned)| ≤ 20%·T_peak and |T(unaligned)| ≤ 20%·T_peak.
- **G4** mesh refinement: T_peak within 10% between n_theta 1536 and 3072 stacks.
- **C1** comparison reported with an uncertainty band of ±25% (declared from the known
  1.22× field-scale factor and the ~4% multi-ring torque-extraction noise). The deliverable
  is the ratio SRM(T_peak)/SynRM(T_peak) with that band and the ordering claim.

## Method notes

- Same solver (damped Newton), same mesh family, same torque extractor with multi-ring
  averaging (n_rings=9, r_spread = half of half-gap) for BOTH machines ⇒ known shared
  bias cancels in the ratio.
- Sweep: rotor phase φ from unaligned (15°) through aligned (37.5°) and back, in 5°
  steps over one rotor pitch [15°, 52.5°].
