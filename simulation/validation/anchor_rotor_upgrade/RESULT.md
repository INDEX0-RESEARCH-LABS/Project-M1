# Anchor rotor-geometry upgrade — torque ceiling of our declared topology: RESULT

Status: **gates U1/U2/U3 PASS; U4 declared expectation VIOLATED (recorded, investigated
briefly).** Script: `simulation/scripts/rajini_rotor_upgrade.py`; log: `rotor_sweep.log`;
JSON: `simulation/scripts/validation/anchor_rotor_upgrade/rotor_sweep.json`.
Per `PLAN.md` (declared before running). M-43 Steel primary bracket only.

## Headline

**No layout in the declared 24-config barrier family comes close to the anchor's implied
torque.** Best (fine-mesh 3072 rays): **8.53 N·m/m** at `frac0.62_span12.0_nb2`,
vs the 108.1 N·m/m the paper's "8 N·m @ 74 mm, 6 A/mm²" implies. Reaching the target
inside this family needs **×12.7 excitation → 76 A/mm² slot current density** — not
thermally plausible in copper slots at this fill. The committed anchor layout
(8.4 mm span, 3 barriers) at 8.12 N·m/m is within ~5% of this family's ceiling: the
committed layout was already near-optimal, and the 13× deficit is a **design-level
discrepancy, not a solver or layout-tuning problem.**

## Sweep results (best |T| per config, 1536 rays, MTPA-neighborhood sampling)

| family (angle_frac) | best config | best \|T\| sampled | iron frac |
|---|---|---|---|
| 0.62 (committed arc) | span 12 mm, nb 2 | **9.0950** → 8.5265 fine | 82.0% |
| 0.50 | span 12 mm, nb 2 | 8.3013 | 85.5% |
| 0.40 | span 12 mm, nb 2 | 7.9678 | 88.4% |
| 0.30 | span 12 mm, nb 2 | 7.1237 | 91.3% |

Clear within-family trends: **nb=2 > nb=3** (consistent ~+6%), **span 12 > 8.4 > 6 mm**
(monotone). Across families: torque *decreases* iron-fraction-ward.

## Gates

| gate | verdict | value |
|---|---|---|
| U1 all solves converge | ✅ | 74/74 conv=True (12–19 iters) |
| U2 region areas ≤1% | ✅ | every config |
| U3 refinement ≤10% | ✅ | 9.0950→8.5265 (6.3%), 8.6979→8.0532 (7.4%) |
| U4 \|T\| rises toward iron-rich layouts | ❌ **violated** | data shows the opposite (0.62 wins) |

**U4 post-lesson:** my declared rationale ("wide arc-frac barriers choke the d-axis pole
iron") was wrong at these field levels. The physics that actually shows up: at 2.5 T
deep saturation the machine is q-flux-blocking-limited — the wide 0.62 barrier arc
blocks q-flux best and still has enough iron wall to carry d-flux, so MORE narrow-iron
(frac 0.30, 95% iron) gives *less* torque, not more. Declared-before-run meant this was
caught as an observation, not quietly rationalized.

## Declared-limitation note (honesty items)

1. **MTPA window:** each config was sampled at the committed MTPA neighborhood
   (delta 22.5/26.25/30°). For frac ≤ 0.50 families the torque profile shows a dip at
   26.25 (e.g. 7.29 / 3.75 / 7.45 for frac 0.50) — their true MTPA angle has MOVED out
   of the sampled window, so their sampled ceilings understate them. The data bound
   still holds: the highest value any iron-rich family showed was 8.30 (1536), which is
   where the 0.62 family's *non-peak* angles sit — even granting each family a generous
   peak at an unsampled angle, no config plausibly exceeds ~1.3× its sampled best, and
   the gap to 108 N·m/m remains ~10×.
2. **Span trend unexplored above 12 mm** — the monotone rise 6→8.4→12 mm continues at
   the sweep edge. Extrapolated ceiling maybe 10–13 N·m/m, still ~9–11× under target.
   Not chased: the anchor's *implied* iron fraction (62% iron) would need ~2.6× more
   barrier air than the committed layout, far outside this family's plausible range,
   and the torque-per-air trend flattens with saturation.
3. One steel bracket only (M-43), per PLAN.

## Deliverable C (comparison back to the anchor)

| | value |
|---|---|
| Family ceiling (fine) | **8.53 N·m/m** → 0.63 N·m @ 74 mm |
| Anchor target | 108.1 N·m/m → 8 N·m @ 74 mm |
| Excitation multiplier needed | **×12.7 (6 → 76 A/mm²)** |
| Verdict | the paper's figure is **not reproducible within this declared topology at
  declared excitation**; at our ceiling it corresponds to a 74 mm stack delivering
  0.63 N·m, or a ~980 mm stack delivering 8 N·m (the anchor's own I2 finding) |

This closes the "is it our layout?" question from `PLAN.md`: no — the committed layout
was already within ~5% of the family optimum; the 13× deficit is attributable to the
anchor's claimed design point, which remains unverifiable without the unpublished rotor
geometry (and, per D-009, without purchases). Doors this leaves open: (a) the paper's
claimed torque rests on design details outside our declared family (e.g., a much deeper
barrier arrangement with tiny bridges, or higher transient current density than their
stated 6 A/mm²); (b) the claim itself may be optimistic. We cannot distinguish (a) and
(b) with the published data — recorded as the campaign's honest residual.

## What this validates for Gate C

The topology family is now mapped well enough that a Gate C optimization loop has a
defensible baseline (span 12 mm, nb 2, frac 0.62 — worth ~+5% over the committed layout
for free) and a defensible torque-density context (~0.42 N·m/L peak, vs typical
high-performance SynRM literature at 1–2 N·m/L) to compare candidates against.
