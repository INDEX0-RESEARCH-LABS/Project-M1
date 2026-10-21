# SRM (12/8) vs SynRM — same-envelope indicative comparison: RESULT

Status: **gates PASS (G1–G4), comparison C1 recorded.** Script: `simulation/scripts/srm_model.py`
(the committed `main()` reproduces this protocol exactly). Logs in this directory.
This is an INDICATIVE ±25%-band result per `PLAN.md` (which carries the 4 recorded
amendments made during bring-up, all *before* any comparison was drawn).

## Machine setups (as run)

- **SynRM**: committed anchor geometry; reference number = corrected anchor MTPA
  **8.1235 N·m/m** (wrap-bug-fixed 2026-10-21 run) → **0.601 N·m @ 74 mm**.
- **SRM 12/8**: 12 stator slots (pole tip ≈15° arc), 8 rotor slots arc 25°, depth 12 mm,
  **open at the rotor surface** (bridge=0 after amendment 2; see boot story below);
  stator slot depth 7.39 mm ⇒ equal total copper area with the SynRM (101.1 mm²/slot);
  phase A wired N,S,N,S (amendment 3), one phase conducting,

## Gates

| gate | verdict | value |
|---|---|---|
| G1 all solves converge | ✅ | every one of 22 solves conv=True (3–18 iters) |
| G2 mesh areas ≤1% | ✅ | max 0.003% |
| G3 \|T\| ≤20%·peak at aligned & unaligned | ✅ | fine: aligned (30°) −0.17, unaligned (7.5°) −0.09 vs 0.2·3.467=0.69 |
| G4 refinement ≤10% at peak | ✅ | 3.2017 → 3.4670 = 8.3% |

## Curve (coarse 768-ray stack, per meter; exactly 45°-periodic)

| φ | 0/45/90 | 5/50 | 10/55 | 15/60 | 20/65 | 25/70 | 30/75 | 35/80 | 40/85 |
|---|---|---|---|---|---|---|---|---|---|
| λ (Wb/m) | 1.735 | 1.334 | 1.334 | 1.737 | 2.206 | 2.749 | 2.717 | 2.748 | 2.203 |
| T (N·m/m) | −3.04 | −1.21 | +0.58 | +2.54 | **+3.20** | +0.29 | −0.45 | −1.19 | −3.93 |

λ min plateau 5–10° (unaligned), max plateau 25–35° (aligned), torque thrusters +8.3…+27°.
The 45° periodicity is exact to printed precision (rotor pitch; the phase circuit spans
two rotor pitches). Positive and negative lobes are asymmetric (+3.20 / −3.93) — expected
for a saturated-reluctance structure; only the positive thrust window is used.

## C1 — the comparison

| | T/m | T @ 74 mm | T per active volume (1.437 L) |
|---|---|---|---|
| SynRM @ MTPA | 8.1235 N·m/m | 0.601 N·m | 0.418 N·m/L |
| SRM 12/8 @ peak (fine) | 3.467 N·m/m | 0.257 N·m | 0.179 N·m/L |
| **ratio** | | **SRM/SynRM = 0.43** | |

**Indicative claim:** at this envelope, with equal installed copper, equal slot fill and
current density, the SRM's single-phase peak torque is ~**43% of the SynRM's MTPA torque**
(declared ±25% band ⇒ 0.32–0.53). For the SRM to match the SynRM thermally it must run
its phase ⅓ of the time, so its *continuous-torque* ranking is even lower — the
instantaneous-peak comparison given here is the SRM's **best case**, and it still loses
by >2×. That is the envelope-level answer to M1's original question: **the SynRM is the
stronger machine in this frame**, and the anchor's remaining failures (unpublished rotor
geometry) do not flip this ordering: flipping 0.43→ >1 would need a >2.3× SRM redesign.

## Boot story (recorded for honesty; all artifacts kept)

1. Declared rotor slot depth 5 mm → gate-tested: negligible saliency (peak 0.0201 N·m/m).
   Amended to 12 mm (PLAN amendment 1). Failure artifact kept.
2. Still ~zero torque with 12 mm. Field map + λ diagnosis: the declared 2 mm rotor
   pole-tip `bridge` is a **continuous iron sleeve around the whole rotor surface**
   — the barrier machinery's band starts below it — which shunts the flux; the rotor
   presented a smooth cylinder (λ modulation ~1e-4). Slots moved to open AT the
   surface (bridge=0, amendment 2). `field_map_shallow5mm_broken.png`,
   `region_classification.png`, `flux_and_currents_diagnostic.png` keep the evidence.
3. Phase-A wiring was all-same-polarity; corrected to classic N,S,N,S (amendment 3).
   Precomputed "aligned at 37.5°" bookkeeping was also half a rotor pole off; aligned/
   unaligned are now measured (λ argmax/argmin), and G3 is declared against those.

## Caveats (declared)

- SRM result = single-phase instantaneous peak; its thermal continuous torque is ≤⅓ duty.
- SRM steel bracket (1006) was declared optional and not re-run; M-43 only.
- The SRM is a first-cut declared design, not an optimized SRM; the SynRM is the anchor's
  committed geometry (itself not the published design). Both share the same toolchain so
  the mesh bias cancels in the ratio (PLAN).
- R3-class mesh discretization: G4 at 8.3% (≤10% gate) is the torque extractor's
  resolution on this geometry; carried into the ±25% band.
