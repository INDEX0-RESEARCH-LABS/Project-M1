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
