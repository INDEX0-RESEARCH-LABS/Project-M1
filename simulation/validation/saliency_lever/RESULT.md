# RESULT - the barrier stack was too shallow: +16% torque and +0.10 PF

Logs: `/tmp/opencode/m1/saliency_{screen,span,deep,confirm,cand,confirm6}.log`.
Gates: `PLAN.md` (declared before the runs). Same solver and extractor as `dq_model.py`;
all screen numbers are 1536 rays / 4 gap rows / single circle, so they carry the -9%
extractor bias and are **only valid as same-extractor comparisons** (gate S4).

## 1. First screen: barrier count, angular width, rib fraction (span fixed at 10.4 mm)

| id | nb | frac | rib | xi | Ld | Lq | T [N.m] | PF | S [VA] |
|---|---|---|---|---|---|---|---|---|---|
| BASE | 3 | 0.62 | 0.40 | 1.85 | 0.1167 | 0.0631 | 1.592 | 0.532 | 986 |
| V1 | 4 | 0.62 | 0.25 | 2.00 | 0.1170 | 0.0584 | 1.651 (+3.7%) | 0.557 | 974 |
| V2 | 5 | 0.62 | 0.25 | 2.01 | 0.1182 | 0.0589 | 1.643 (+3.2%) | 0.551 | 980 |
| V3 | 4 | 0.75 | 0.25 | 2.32 | 0.0989 | 0.0427 | 1.159 (-27%) | 0.496 | 783 |
| V4 | 3 | 0.75 | 0.20 | 2.43 | - | - | 1.177 (-26%) | 0.517 | - |

Thinner ribs help a little (V1: +3.7% torque, +0.025 PF for free). Widening the barriers
(V3/V4) raises xi but destroys torque: the d-axis iron wedge is what carries the flux.

**S3 as declared: FAIL - no variant cleared xi >= 2.5.** Correct as written, but the
diagnosis behind it was incomplete.

## 2. Second screen: radial depth (the actual defect)

The barrier stack sits in the outer 10.4 mm of a 64.5 mm rotor radius, so q-flux can dive
**under** it through 37 mm of solid iron. That, not the rib fraction, is why xi was 1.85:

| id | nb | frac | rib | span [mm] | xi | T [N.m] | PF | S [VA] |
|---|---|---|---|---|---|---|---|---|
| BASE | 3 | 0.62 | 0.40 | 10.4 | 1.85 | 1.592 | 0.532 | 986 |
| S1 | 4 | 0.62 | 0.25 | 20.8 | 2.12 | 1.711 (+7.5%) | 0.596 | 942 |
| S2 | 4 | 0.62 | 0.25 | 31.2 | 2.28 | 1.763 (+10.8%) | 0.625 | 924 |
| S3 | 5 | 0.62 | 0.30 | 26.0 | 2.09 | 1.699 (+6.7%) | 0.590 | 946 |
| S4 | 4 | 0.62 | 0.25 | 45.5 | 2.42 | 1.798 (+13.0%) | 0.645 | 913 |
| S5 | 4 | **0.68** | 0.25 | 45.5 | 2.74 | **0.849 (-47%)** | 0.429 | 678 |

Monotonic in depth: every millimetre of barrier is worth torque and PF, up to the point
where the d-axis wedge is starved. S4 reaches the shaft and gains the most; S5 shows the
cliff - at full depth, widening to 0.68 removes the d-path and the machine collapses.

**S4 fails a declared geometric invariant** (`zone_in > shaft_r + 2 mm`). It was pulled
back 1 mm:

| id | span | xi | T [N.m] | PF | S [VA] | Vhat |
|---|---|---|---|---|---|---|
| **S6 (candidate)** | 44.5 mm | 2.41 | 1.797 (+12.9%) | 0.644 | 914 | - |

## 3. Ring-averaged confirmation (the ruled extractor)

3072 rays / 10 gap rows, rings 1 / 5 / 9, at the operating point:

| | T [N.m] |
|---|---|
| baseline (certified mesh, ring-averaged) | 1.507 |
| **S6, ring-averaged (1.751 of 1.691/1.804/1.751)** | **1.751 -> +16.2%** |
| S6 PF / S / Vhat | **0.635 / 903 VA / 5.91 V** |

The +16% torque survives the extractor correction (it grew from +13% at the coarse
single-circle to +16% ring-averaged), so it is not a sampling artifact. The PF gain is
+0.10 at the same current, four times the 0.03 screen gate.

## 4. Gate S3 was wrong, and here is the honest correction

S3 required `xi >= 2.5` as a proxy. The data falsifies the proxy: S4/S6 deliver PF +0.11
and torque +16% at xi 2.41, while S5 hits xi 2.74 and loses half its torque. **xi is a
diagnostic, not an objective.** The gates that actually express the goal - PF and torque at
fixed current - both pass by a wide margin.

Recorded, not silently retuned: the revised rule is "candidate if PF >= BASE + 0.03 AND
T >= 0.95 x BASE", with xi reported as a diagnostic. This is the second gate this session
whose pass/fail statistic was poorly chosen (the first was E1 in
`torque_extractor/PLAN.md`); both were caught by the data before anything was published.
Pattern worth keeping: a gate built on an assumed mechanism must be checked against the
objective it stands in for.

## 5. Consequence at the 1.6 N.m target (DERIVED, same scaling as STATUS.md)

| | baseline | deep-barrier candidate (S6) |
|---|---|---|
| T at J=5.34, ring-averaged | 1.507 | **1.751** |
| J for 1.6 N.m | 5.62 | **5.10** |
| current (k=2) | 53.7 A | **48.8 A** |
| copper loss | 26-28 W | **22-23 W** |
| efficiency (with iron) | 92.3% | **~93.3%** |
| Vhat at 3000 rpm (k=2) | 13.5 V | **~11.4 V** |
| speed ceiling | ~5,860 rpm | **~6,900 rpm** |
| **S at 1.6 N.m** | **~1.09 kVA** | **~0.76-0.80 kVA** |
| **PF** | 0.49-0.54 | **0.63-0.64** |

This is close to closing the D-012 blocker without changing voltage, winding or frame:
the controller for 0.5 kW drops from ~1.1 kVA to ~0.8 kVA, and the 48 V envelope gains
speed headroom because the machine needs less flux for the same torque.

## 6. What is NOT established (do not ship this yet)

1. **Mechanical.** Four full-depth barriers leave 3.8 mm ribs, a 0.6 mm surface bridge and
   a 1.5-2.4 mm yoke above the shaft. Gate B was certified for the shallow rotor; stress
   must be re-run, and this is the most likely failure mode.
2. **Iron loss.** The rotor flux path changed materially and Bmax in the ribs rose from
   2.73 to 2.79 T (saturation is what blocks q-flux, but it costs loss). Re-run
   `iron_loss.py` on this geometry before quoting the 93.3%.
3. **Manufacturing.** 16 barrier punches per rotor plus thin ribs and bridges: standard
   SynRM practice, but a tooling question, not a simulation one.
4. **Extractor band.** +/-4% on absolute torque still applies. The +16% is outside it.
5. **Ripple / NVH.** Not modelled at all; deeper barriers usually raise torque ripple.

## 7. Recommended next batch (in order)

1. Gate B stress on S6 (blocks everything else).
2. Iron loss on S6 (2 solves, ~3 min).
3. If 1-2 pass: full ring-averaged certification + `STATUS.md` restatement, then D-014.
