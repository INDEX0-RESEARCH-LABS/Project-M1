# Candidate Architectures — Comparison Matrix (Gate A desk review)

**Date:** 2026-10-20 · **Basis:** verified literature (`../research/literature_review.md` IDs L-nn,
prior art P-nn). **Scores are desk estimates from cited evidence, NOT measurements.** Scale 1–5
(5 = best for M1's context). Weights reflect the 0.5–1 kW, 24–48 V, Indian e-2W/e-3W use case.

| Criterion (weight) | SRM | SynRM | PMSM (benchmark) | IM |
|---|---|---|---|---|
| Efficiency across operating range (15%) | 3 — ~82% max at 3.5 kW prototype (L14); ripple control raises it (L33) | 4 — IE5 class in industry (L10); drive-cycle optimized (L13, L43) | 5 — reference benchmark | 3 — rotor losses at part load |
| Torque/torque density (12%) | 4 — +13.2% torque for 6/4 vs 8/6 (L14); no magnets needed | 3 — saliency-limited (L10, L11) | 5 | 3 |
| Max speed / field weakening (8%) | 4 — robust simple rotor | 2 — **poor flux weakening, forces oversizing at high perf** (L12); benign at low-speed 2W/3W | 4 | 5 |
| Torque ripple (12%) | 2 — dominant drawback (L5); mitigable to ~9% (L40) | 4 — skew halves ripple (L10); windows known (P13) | 4 | 4 |
| Acoustic noise/NVH (10%) | 2 — main 2W adoption blocker; mature mitigation toolbox (L26–L37) | 4 | 3 | 4 |
| Loss structure / controllability (8%) | 3 — needs position sensor or estimation; converter per phase (L3, L4) | 3 — sensorless proven industrially (L41, L42) | 4 | 4 |
| Thermal performance (8%) | 4 — no hot magnets; barriers usable as cooling ducts (P18) | 4 — same, no magnets (L18) | 2 — demag/thermal limits | 4 |
| Manufacturing complexity (8%) | 4 — concentrated windings, simple laminated rotor | 3 — thin barrier bridges need precision (P6) | 2 — magnet insertion, containment | 4 |
| Material cost & supply chain (10%) | 5 — zero rare earth (L2, L25); NITI Aayog motivation (L23) | 5 — zero rare earth | 1 — rare-earth exposure (L23, L24) | 4 |
| Controller complexity (4%) | 3 — asymmetric converter | 3 — standard 2-level inverter | 4 | 4 |
| Reliability/serviceability (3%) | 4 — rugged | 4 | 3 — demag risk | 4 |
| **Weighted total (est.)** | **≈3.6** | **≈3.8** | **≈3.5** | **≈3.7** |
| Indian prior art density (context) | Thin (P4 ceased; P15–P17 unverified) | Thin (P15 unverified) | Crowded | Crowded |
| 2W/3W prototype precedents found | 0.5 kW e-rickshaw (L19), 3.5 kW motorcycle (L14), scooter (L16, L17) | 1.2 kW Indian trike (L18) | everywhere | few at this scale |

## Recommendation (PROVISIONAL — requires founder approval, revisable at Gate B)

**Primary baseline: synchronous reluctance motor (SynRM), 4-pole, multi-barrier rotor.**
**Comparison architecture: 12/8 (or 6/4) SRM.**
**Benchmark: interior PMSM at same envelope (literature numbers only, no build).**

Rationale:
1. SynRM wins the weighted matrix, driven by ripple/NVH (the documented 2W adoption blocker) while
   keeping the magnet-free supply-chain argument intact (L23, L25) — the "magnet-free" property is
   shared with SRM, so it cannot be the deciding factor between them (per master-prompt rule).
2. SynRM's chief weakness — flux weakening (L12) — matters least in the low-speed 2W/3W duty, and
   matters most in high-performance cars, which M1 is not.
3. The nearest full-text Indian analog (L18: 1.2 kW ferrite-assisted SynRM, Indian drive cycle,
   experimental) is a ready validation anchor for Gate B.
4. SRM remains the live challenger: if at Gate B the same-envelope comparison shows SynRM losing on
   torque density by >15% at the same current density, the baseline flips to SRM (documented in
   DECISIONS.md).

**Hypothesis being tested:** H1 (see `../research/research_gaps.md`).

## Explicit non-claims

- No efficiency, torque, or cost number here is a Project M1 measurement; all are cited literature values.
- Axial-flux was considered and parked: no magnet-free axial-flux prototype evidence was found in the
  verified set at this power band, and it adds mechanical novelty before electromagnetic validation.
- Wound-field synchronous (EESM) is magnet-free and promising near-term (L25) but adds a brush/
  transformer excitation system that complicates a first prototype; revisit post-Gate-C.
