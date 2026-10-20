"""FEMM batch pipeline driver: .fem -> fmesher -> fsolver -> parse .ans.

Uses xfemm's headless CLI tools (fmesher, fsolver) directly — the femmcli Lua
bindings crash/hang in xfemm 3.0, so geometry is written as .fem text by callers
(e.g. femm_model.py) and this module only runs the solver chain and parses results.

Known xfemm 3.0 behavior (recorded 2026-10-20):
- fmesher writes Triangle-format .node/.ele/.edge next to the .fem.
- fsolver takes the basename (no extension), reads .fem + .node, writes .ans.
- A SIGTERM'd fsolver deletes its mesh files — never kill it; let it finish.
- Arch's -D_GLIBCXX_ASSERTIONS makes stock xfemm abort in the solver; our installed
  package was rebuilt without it (see docs/toolchain.md).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

FEMMBIN = Path.home() / ".cache/paru/clone/xfemm/src/xfemm_linux64/cfemm/bin"


def run_fmesher(fem_file: Path) -> dict:
    r = subprocess.run([str(FEMMBIN / "fmesher"), fem_file.name],
                       cwd=fem_file.parent, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"fmesher failed: {r.stdout}\n{r.stderr}")
    node = fem_file.with_suffix(".node")
    if not node.exists() or node.stat().st_size == 0:
        raise RuntimeError("fmesher produced no mesh (.node missing/empty) — check block labels")
    return {"stdout": r.stdout}


def run_fsolver(fem_file: Path, timeout: int = 1800) -> Path:
    """fsolver wants the basename without extension. Do NOT interrupt it."""
    r = subprocess.run([str(FEMMBIN / "fsolver"), fem_file.stem],
                       cwd=fem_file.parent, capture_output=True, text=True, timeout=timeout)
    ans = fem_file.with_suffix(".ans")
    if r.returncode != 0 or not ans.exists():
        raise RuntimeError(f"fsolver failed (rc={r.returncode}): {r.stdout}\n{r.stderr}")
    return ans


def parse_ans(ans_file: Path) -> dict:
    """Parse FEMM text .ans: header lines, [Solution], then N node records.

    Node record layout (FEMM 4.x planar): x y A Bx By c
    (c = conductor flag). Returns dict with np arrays x, y, A, Bx, By.
    """
    import numpy as np
    lines = ans_file.read_text().splitlines()
    i = lines.index("[Solution]")
    header = {}
    for ln in lines[:i]:
        if "=" in ln:
            k, v = ln.split("=", 1)
            header[k.strip("[] ")] = v.strip()
    n = int(lines[i + 1])
    data = np.loadtxt(lines[i + 2:i + 2 + n])
    return {"header": header, "n": n,
            "x": data[:, 0], "y": data[:, 1], "A": data[:, 2],
            "Bx": data[:, 3], "By": data[:, 4]}


def b_at(sol: dict, x: float, y: float) -> float:
    """|B| at the solution node nearest (x, y)."""
    import numpy as np
    d2 = (sol["x"] - x) ** 2 + (sol["y"] - y) ** 2
    j = int(np.argmin(d2))
    return float(np.hypot(sol["Bx"][j], sol["By"][j]))


def solve_fem(fem_file: Path) -> dict:
    run_fmesher(fem_file)
    ans = run_fsolver(fem_file)
    return parse_ans(ans)


if __name__ == "__main__":
    import sys
    sol = solve_fem(Path(sys.argv[1]))
    print(f"nodes: {sol['n']}")
