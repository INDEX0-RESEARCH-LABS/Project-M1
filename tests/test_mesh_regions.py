"""Mesh correctness: every region's meshed area must match its closed-form area.

Guards the failure modes found on 2026-10-20:
- double-covered space (area total > physical domain total),
- centroid misclassification of coarse elements,
- inverted slot direction swallowing the airgap.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulation" / "scripts"))

from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas


def _element_areas(mesh) -> np.ndarray:
    p0, p1, p2 = (mesh.p[:, mesh.t[i]] for i in range(3))
    return 0.5 * np.abs(
        (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1]))


def test_every_element_assigned_exactly_once():
    mesh, sub, _ = build_mesh(SynRMGeometry())
    hits = np.zeros(mesh.t.shape[1], int)
    for v in sub.values():
        hits[v] += 1
    assert (hits == 1).all(), f"{(hits != 1).sum()} elements mis-classified"


def test_mesh_dominion_not_double_covered():
    g = SynRMGeometry()
    mesh, sub, _ = build_mesh(g)
    meshed_total = _element_areas(mesh).sum()
    exact_total = sum(expected_areas(g).values())
    assert abs(meshed_total - exact_total) / exact_total < 0.01


def test_region_areas_match_closed_form():
    g = SynRMGeometry()
    mesh, sub, _ = build_mesh(g)
    area = _element_areas(mesh)
    exp = expected_areas(g)
    for name, exact in exp.items():
        meshed = area[sub[name]].sum()
        err = (meshed - exact) / exact
        assert abs(err) < 0.01, f"{name}: meshed {meshed*1e6:.1f} mm^2 " \
            f"vs exact {exact*1e6:.1f} mm^2 ({err:+.2%})"


if __name__ == "__main__":
    raise SystemExit("run with: .venv/bin/python -m pytest tests/ -q")
