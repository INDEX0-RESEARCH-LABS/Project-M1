# Decision Log

Format: `## D-NNN — Title` · date · context · decision · alternatives · status.
Status: `PROPOSED` | `APPROVED` | `REJECTED` | `SUPERSEDED` by D-NNN.

## D-001 — Workspace layout and toolchain
- **Date:** 2026-10-20
- **Context:** Phase Zero required a clean, version-controlled workspace without touching existing user projects.
- **Decision:** Create `project-m1/` at `/home/darion-dev/project-m1`, structure per master prompt; Python 3.14.8 venv with numpy/scipy/pandas/matplotlib/pytest; git for version control.
- **Alternatives:** Reuse an existing project directory (rejected — violates "clean workspace"); poetry/conda (rejected — venv + pip is sufficient and reproducible).
- **Status:** APPROVED (self, pending founder ratification)

## D-002 — No architecture selected yet
- **Date:** 2026-10-20
- **Context:** Master prompt forbids assuming a novel architecture exists.
- **Decision:** Baseline selection deferred to Gate B after literature review; no default commitment to SRM or SynRM.
- **Status:** APPROVED

## D-003 — Simulation tool candidates, not commitments
- **Date:** 2026-10-20
- **Context:** FEMM/Elmer not installed on this machine; Arch Linux (pacman/paru available).
- **Decision:** Attempt OpenFemm (AUR) and Elmer FEM installation at Gate B; record blockers rather than fabricate output. Python stack is the guaranteed fallback for analytical/geometry/analysis work.
- **Status:** PROPOSED

## D-004 — Provisional baseline: SynRM (4-pole multi-barrier); SRM as comparison architecture
- **Date:** 2026-10-20
- **Context:** Gate A desk comparison of SRM/SynRM/PMSM/IM for 0.5–1 kW, 24–48 V e-2W/e-3W.
- **Decision:** SynRM baseline (weighted matrix ~3.8 vs SRM ~3.6), SRM as live comparison, PMSM as literature benchmark only. Flip criterion: if Gate B same-envelope FEM shows SynRM losing torque density by >15% at equal current density, baseline becomes SRM.
- **Alternatives:** SRM baseline (rejected for now on ripple/NVH — documented 2W adoption blocker); EESM (parked — excitation system adds first-prototype complexity); axial-flux (parked — no verified magnet-free precedent at this band).
- **Status:** PROPOSED — requires founder approval; revisable at Gate B.

## D-005 — Primary solver: in-house 2D magnetostatics (scikit-fem); xfemm demoted to cross-check
- **Date:** 2026-10-20
- **Context:** xfemm 3.0 (AUR, rebuilt without Arch's `_GLIBCXX_ASSERTIONS`) is unreliable headless: `femmcli` lua hangs nondeterministically before `mi_saveas`; `fsolver` ran 13+ min without converging on a 10k-node problem while solving tiny ones in seconds; killed `fsolver` runs delete their own mesh files; `femmcli` lacks `mo_*` solution queries. `fmesher` and the `.fem` text format work fine.
- **Decision:** Primary Gate B/C solver = in-house linear A-z magnetostatics on scikit-fem + triangle (pip-only, fully scriptable, validated against an analytic straight-wire answer + mesh-convergence study). xfemm kept as secondary/independent cross-check where it works — H3 re-verification needs an independent model anyway. Elmer remains a second-opinion candidate.
- **Alternatives:** Keep debugging xfemm UB (rejected — nondeterministic); wine + FEMM 4.2 (rejected — heavy, unscriptable).
- **Status:** APPROVED (self)
