# Solver validation — saturated iron / nonlinear path (Gate B)

**Date:** 2026-10-20  **Solver:** in-house A-z + Picard-on-nu, scikit-fem 12.0.2 + gmsh 4.15.2

## Material data
M-19 electrical steel, 47-point B-H curve read from the FEMM material library
`/usr/local/share/xfemm/release/matlib.dat` (Aladdin/US Steel handbook data).
Loaded by `fem_magnetics.load_bh_curve("M-19 Steel")` — no hand-typed curve.
**Provenance caveat:** M-19 is the *solver-validation* material only. It is not
the grade used by either Gate B validation anchor. Both anchor grades were
subsequently confirmed from full text (see `research/material_grades.md`), and
neither is M-19:

| anchor | grade | thickness | saturation |
|--------|-------|-----------|-----------|
| Kachapornkul 2022 (SRM) | 35A300 (JIS) ≡ 36F168 / V300-35A | 0.35 mm | — |
| Rajini 2024 (SynRM anchor) | M1000-65A (CRNO) | 0.65 mm | 2.1 T assumed |

**Neither grade's B-H curve is in the local FEMM library.** Reproducing an
anchor's torque needs a citable curve for its grade first — this is now the
critical path for the torque comparison, not the solver.

## Test case
Toroidal iron ring, bore radius 20 mm, outer radius 80 mm, 7000 A through the
bore. Deep saturation is the point: an unsaturated case would pass even with a
linear solver.

Two independent checks:
1. **Ampère's law** — on a closed path inside the iron, ∮H·dl must equal the
   enclosed 7000 A exactly, for any material. H is recovered through the local
   B-H law (H = B/(μ0·μr(B))), not by dividing by μ0.
2. **Saturation engaged** — iron mean |B| must exceed 1.5 T.

## Results

| check | value | target |
|-------|-------|--------|
| Picard convergence | 98 iterations, converged | converged |
| ∮H·dl at r = 40 mm | 6965.6 A | 7000 A ±2% → **0.49%** |
| ∮H·dl at r = 60 mm | 6987.4 A | 7000 A ±2% → **0.18%** |
| iron mean / peak \|B\| | 1.922 T / 2.347 T | > 1.5 T |

Independent 1-D cross-check: H = 7000/(2π·0.05) = 22 282 A/m → B = 1.955 T from
the same curve. FEM mean 1.922 T agrees to 1.7% (the 1-D value ignores the
radial flux distribution).

**Result: PASS.**

## Iteration notes (what was actually hard)
- Initialising iron at the curve's low-field μr (~4400) produced a first-iteration
  \|B\| ≈ 223 T; the iteration then crawled back. Initialising at μr ≈ 100 fixes it.
- Plain substitution (relax = 1) diverges. Under-relaxation with a stagnation
  test (`res > 0.95·prev` → relax × 0.7) converges to 1e-7 by ~80 iterations.
  An earlier 0.9 / ×0.5 schedule throttled relaxation too fast and plateaued at
  a 1e-2 residual.
- Two earlier versions of this test reported spurious failures because they
  applied Ampère's law with H = B/μ0 inside iron. That is only valid in vacuum.

## Open items
- ~~Verify the actual steel grades used by the two validation anchors.~~ Done —
  35A300 and M1000-65A, both quoted from full text in `research/material_grades.md`.
- Obtain a *citable* B-H curve for 35A300 and for M1000-65A. M-19 must not be
  silently substituted: it has a substantially higher permeability and a
  different saturation knee, so a torque comparison run on M-19 would be
  comparing materials, not machines.
- Iron losses (hysteresis + eddy) are **not** modelled; AC/thermal work at a
  later gate must add Steinmetz or a loss model.

Reproduce: `.venv/bin/python simulation/scripts/known_answer_nonlinear.py`
