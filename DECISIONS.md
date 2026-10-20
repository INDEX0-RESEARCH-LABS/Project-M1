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
