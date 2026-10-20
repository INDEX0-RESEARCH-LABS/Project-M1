# Toolchain & Reproducibility

Recorded 2026-10-20 during Phase Zero inspection.

## Environment

| Item | Value |
|---|---|
| OS | Arch Linux (pacman + paru/AUR), uid 1000 (no root; docker group) |
| Disk free | ~246 GB on `/home` |
| Python | 3.14.8 (mise-managed) |
| venv | `/home/darion-dev/project-m1/.venv` |
| git | 2.55.0 |
| Network | Available (PyPI reachable) |

## Python dependencies (pinned in `requirements.txt`)

| Package | Version |
|---|---|
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| pandas | 3.0.6 |
| matplotlib | 3.11.2 |
| pytest | 9.1.1 |

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q
```

## Electromagnetic FEA tools — status

| Tool | Status (2026-10-20) | Notes |
|---|---|---|
| FEMM / OpenFemm | **Not installed** | Attempt via AUR at Gate B; blocker recorded honestly if it fails |
| Elmer FEM | **Not installed** | Check availability (`paru -s elmerfem`) at Gate B |
| Gmsh | Not installed | Needed if Elmer path is used |
| FreeCAD / CAD | Not installed | Required only at mechanical design stage |

No simulation output will be produced or claimed until a solver is genuinely installed and run.
Solver capability limits (e.g. FEMM = 2D magnetics, no thermal/stress) will be documented in
`simulation/README` when the tool is adopted.

## Solver status (updated 2026-10-20, D-005)

| Tool | Status | Notes |
|------|--------|-------|
| scikit-fem 12.0.2 + gmsh 4.15.2 | **primary solver** | pip-only, deterministic, headless; validated 0.066 % vs analytic wire |
| xfemm 3.0 (xfemm-3.0-1, patched PKGBUILD) | demoted to cross-check | `fmesher` + `.fem` text I/O work; `femmcli` lua hangs nondeterministically; `fsolver` failed to converge in 13 min on a 10 k-node case it should solve in seconds; SIGTERM'd `fsolver` deletes its own mesh files; no `mo_*` solution API in `femmcli` |

xfemm was rebuilt from the AUR tree with `/tmp/opencode/makepkg-noassert.conf`
(Arch's default `-Wp,-D_GLIBCXX_ASSERTIONS` makes it abort on a latent
out-of-bounds access in `femmsolver::CMMeshNode`). Even without assertions the
build is unreliable — hence D-005.

Validation record: `simulation/validation/known_answer/RESULT.md`
