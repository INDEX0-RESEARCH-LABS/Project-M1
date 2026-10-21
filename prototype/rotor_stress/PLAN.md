# PLAN — rotor mechanical check (Gate D prep, zero-spend analytic)

**Declared before running, frozen.** Script: `simulation/scripts/rotor_stress_check.py`.
Purpose: does the committed SynRM barrier rotor survive service speeds with the thin
bridges (0.6 mm committed, 0.4 mm winner-family variant)? This is the #1 mechanical
risk of the whole architecture.

## Geometry facts used (from `synrm_geometry.rotor_barriers`)

- Barrier layers top out at `R_out − bridge` → **the surface ring is a continuous
  annulus** of radial thickness `bridge` (0.6/0.4 mm) — verified from the polygon
  construction (no barrier crosses it).
- R_out = (BORE − 2·AIRGAP)/2 = 45.517 mm; BORE 92.075 mm, SHAFT_OD 24 mm, 4 poles.
- Iron webs and pole-body spokes are bounded by barrier sectors (frac 0.62 of the pole
  pitch) and terminate on continuous iron at the d-axes (arc width (1−0.62)·90°
  at pole centers — wide columns to the shaft hub).

## Frozen model + assumptions (first-cut, conservative, declared)

- **M-A (dominant): surface-ring hoop**, thin free ring: σ = ρ ω² R_m², R_m = R_out −
  bridge/2. Conservative: ignores shaft-hub elastic support.
- **M-B (spoke check):** spoke treated as a solid-disk slice, plane-stress radial
  stress σ_r = (ρ ω²/8)[(3+ν)R² − (1+ν)r²] at the hub junction (r = 12 mm).
- Stress bands various: stress concentration factor Kt ∈ {1.5, 2.0, 3.0} on the
  maximal mechanism (barrier-mouth corners into the ring; undocumented published
  aid assumption, KEPT as band, never hidden).
- **Material:** σ_y = 230 MPa declared conservative for M-43-class annealed
  electrical sheet (typical published band 260–340 yield / 420–480 UTS; no paid
  certificate available — D-009). SF = 230 / σ_max.
- **Airgap-closure sanity:** ring dilation ε·R_m vs the 0.52 mm airgap, reported.
- **Out-of-scope flag (recorded, not solved):** the SRM-comparison rotor sets
  bridge=0 (open surface slots) → its surface fins are unsupported cantilevers;
  noted for physics honesty. SRM is the rejected architecture (D-008), so no model.

## Frozen pass rule

Mechanical gate passes if **SF ≥ 2.0** against all Kt values of the band at both
the declared continuous rating (3000 rpm) and the declared peak envelope (6000 rpm)
of `requirements/target_specification.md`. Additionally the table must show the
rpm at which SF crosses 2.0 / 1.5 / 1.0 for the committed bridge (0.6) and the
winner-family variant (0.4), as forward information only.
