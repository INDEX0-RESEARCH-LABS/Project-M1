# Research Gaps, Prior Art Landscape, and Hypotheses — Gate A

**Compiled:** 2026-10-20 from four verified research passes. Sources: `literature_review.md` (IDs L-nn),
`prior_art.md` (P-nn).

## 1. Observed research gaps

1. **No peer-reviewed Indian SRM/SynRM e-2W prototype paper exists** (all Indian reluctance work found
   is e-3W/e-rickshaw/trike: L18, L19, L21).
2. **SynRM for 2W/3W is nearly absent worldwide** — one trike prototype (L18); no SynRM e-scooter or
   e-rickshaw prototype found in any country.
3. **No standardized drive-cycle efficiency comparison of SRM vs SynRM vs PMSM at 0.5–5 kW** (the
   e-2W/e-3W band); the only three-way comparison found is car-class 60 kW (L9).
4. **24–48 V inverter-loss evidence is nearly empty** — one abstract-level paper (L44); everything else
   is 400/800 V or device-level (L45, L46).
5. **Vehicle-level NVH quantification for SRM in 2W/3W is missing** — reviews confirm ripple+noise as
   the dominant blocker but no opened paper quantifies it at vehicle level for these segments.
6. **EM–thermal co-optimization does not exist at kW-class low-voltage reluctance machines** (L49, L50
   are PM/aerospace).
7. **Optimization-gain claims are simulation-conditional and unbenchmarked** — no head-to-head
   same-budget BO vs NSGA-II vs random benchmark across machines; surrogate validation is always
   against the FEA teacher (L51–L65, L70).
8. **No electric-machine-specific methodological paper arguing "optimization result ≠ physically
   validated design"** — the corrective literature (L69–L72) lives outside the EM domain. Writing
   that bridge for the 0.5–5 kW class is itself a contribution.
9. **Indian patent space for reluctance structure is thin but foreign space is crowded** (see prior art).

## 2. Prior-art landscape (summary — full table in `prior_art.md`)

**Crowded (do not stake novelty here):** multi-layer SynRM flux barriers (LG'99, ABB, Mitsubishi,
Gree, Schaeffler); numeric ripple windows (Gree CN110635591, <5% ripple claim); control-side ripple
(Enedym US10637386, active to ~2038); basic SRM pole-arc shaping (back to Samsung 1996).

**Moderately crowded:** ferrite PM-assisted SynRM (Osaka, D&M, decade of filings); anti-demagnetization
geometry is the narrower niche.

**Open-ish:** flux barriers reused as cooling channels (ABB US8686608 expired-fee-related; combinations
with partitioned rotors thinly populated); Indian-origin structural SRM filings rare (IISc
WO2019116389A1, ceased); field-switched/transformer-excited magnet-free motors in India ≈ one
unverified family.

*Preliminary search only — not a freedom-to-operate or patentability opinion. Indian patent counsel
review required before any filing decision or public disclosure.*

## 3. Candidate research hypotheses (Gate A — evidence-backed)

### H1 — SynRM flux-barrier geometry can outperform a same-envelope SRM on the 2W/3W duty cycle
**Statement:** For a 0.5–1 kW, 24–48 V machine sized to the same stator envelope, a multi-barrier SynRM
will deliver ≥5 percentage points higher drive-cycle efficiency and ≥10 dB lower audible-noise proxy
(ripple torque RMS) than an equivalent SRM, at the cost of a more complex rotor.
**Evidence:** L10 (skew halves ripple; industrial IE5 SynRM), L12 (SynRM viable when flux-weakening
demand is modest — true for low-speed 2W/3W), L18 (1.2 kW ferrite-assisted SynRM prototype beats
alternatives on EM+thermal+vibration incl. Indian drive cycle), L5 (SRM ripple+noise = dominant
drawback), gap 2 (nobody has shown this for e-2W).
**Falsification:** same-envelope FEM comparison at identical current density and same thermal limit;
if SynRM loses on efficiency or ripple, H1 dies.
**Status:** PROPOSED — testable entirely in simulation at Gate B/C.

### H2 — SRM torque-ripple reduction has headroom left at the *combination* level for low-pole-count 2W motors
**Statement:** For a 3-phase low-pole SRM (e.g. 6/4 or 12/8 external-rotor) in the 0.5–1 kW band,
combined pole-count/pole-arc choice + DITC-style control can reduce torque-ripple RMS below 8% of
average torque without reducing average torque by more than 3% relative to a naive design.
**Evidence:** L14 (6/4 vs 8/6 trade-off quantified on a real prototype), L40 (ripple 9.08% vs 12.84%
simulated), L33 (profiling cuts noise *and* raises efficiency), L38 (DITC with mutual coupling),
P14 (Enedym holds the control-side patent — check FTO before productising).
**Falsification:** FEM + circuit co-simulation sweep; if <8% requires >3% average-torque loss, H2 dies.
**Status:** PROPOSED.

### H3 — Physics-informed Bayesian optimization beats evolutionary search *per FEM-evaluation budget* in this design space
**Statement:** At a fixed budget of ≤150 2D-FEM evaluations on the Gate-B baseline geometry, a
physics-informed GP-BO will find a design ≥5% better on the primary objective than NSGA-II run on the
same budget, with results re-verified on a held-out FEM configuration (mesh/angle sweep not seen by
the search).
**Evidence:** L51 (45% faster than NSGA-II, single machine, single objective — needs independent
replication), L65/L66 (surrogate review, open problems), L70 (model-discrepancy trap),
gap 7 (no same-budget benchmark exists anywhere).
**Falsification:** run both methods with identical budget, seeds, and objective function; re-verify
best-of-each on independent mesh. If BO's advantage vanishes under re-verification, H3 dies.
**Status:** PROPOSED — this is also a publishable gap regardless of outcome (gap 8).

## 4. Smallest scientifically credible experiment (Gate B definition)

Before any optimization or prototype commitment:
1. Build a 2D FEM model of **one** shortlisted architecture (SRM 12/8 or SynRM 4-pole multi-barrier).
2. Run a mesh-convergence study (≥3 mesh densities; declare torque change tolerance, e.g. <1%).
3. Reproduce **one published** torque-vs-current or flux-vs-current curve (candidate source: L14 or L18
   — both full-text with prototype data) within a declared tolerance (target ≤5%, stated before the run).
4. Log everything in `simulation/validation/`.
If step 3 fails, no downstream optimization result is considered trustworthy.
