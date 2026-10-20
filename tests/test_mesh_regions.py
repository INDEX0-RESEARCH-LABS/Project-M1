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


def test_geometry_module_agrees_with_mesh_classifier():
    """Cross-module check: synrm_geometry.rotor_barriers and the mesh classifier
    must place barriers at the same angles (q-axis-centred, 45 deg folded). A
    45 deg placement mismatch between the two modules survived the area tests
    because area is rotation-invariant.

    Method: unwrap vertex angles of each geometry-module barrier and require
    the midpoint to sit at 45 deg mod 90 (q-axis, not pole axis); do the same
    for the angular run the mesh classifier calls barrier at a radius inside
    the barrier zone.
    """
    import math

    from synrm_geometry import SynRMGeometry, rotor_barriers
    from synrm_mesh import _in_barrier

    g = SynRMGeometry()
    p = rotor_barriers(g)[0]  # pole 0, layer 0
    angs = np.degrees(np.unwrap([math.atan2(y, x) for x, y in p["points"]]))
    geom_mid = angs.mean() % 90.0
    assert abs(geom_mid - 45.0) < 1.0, \
        f"geometry barrier midpoint {geom_mid:.1f} deg, expected ~45 (q-axis)"

    r_mid = (p["r_inner"] + p["r_outer"]) / 2
    inb = [deg for deg in np.linspace(0, 90, 1801)
           if _in_barrier(g, r_mid * math.cos(math.radians(deg)),
                          r_mid * math.sin(math.radians(deg)))]
    assert inb, "mesh classifier finds no barrier at the barrier-zone radius"
    mesh_mid = (min(inb) + max(inb)) / 2
    assert abs(mesh_mid - 45.0) < 1.0, \
        f"mesh classifier barrier midpoint {mesh_mid:.1f} deg, expected ~45"


if __name__ == "__main__":
    raise SystemExit("run with: .venv/bin/python -m pytest tests/ -q")
