"""Linear 2D magnetostatics (A-z formulation) on scikit-fem + gmsh meshes.

Primary solver per D-005. xfemm proved unreliable headless; this is fully
scriptable, deterministic, and validated against an analytic answer in
known_answer_check.py.

Formulation (planar, linear):
    A = Az(x,y),  B = curl A = (dA/dy, -dA/dx)
    weak form:  sum_i nu_i * int_{Omega_i} grad(u).grad(v) = sum_i int J_i v
    essential BC: A = 0 on the outer boundary (magnetic wall)
Units: SI (m, A, T).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from skfem import Basis, BilinearForm, ElementTriP1, LinearForm, MeshTri, asm
from skfem import condense, solve

MU0 = 4e-7 * np.pi


def load_gmsh_mesh(msh_file: Path) -> tuple[MeshTri, dict[str, np.ndarray]]:
    """Read a gmsh 2D mesh into a scikit-fem MeshTri + physical-group cell sets."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(str(msh_file))
        node_tags, coords, _ = gmsh.model.mesh.getNodes()
        p = coords.reshape(-1, 3).T[:2]
        _, etag_list, ntag_list = gmsh.model.mesh.getElements(2)
        # per element type: etags (N,), ntags flat node connectivity (3N,)
        etags = [e for e in etag_list if len(e) > 0]
        ntags = [n.reshape(-1, 3) for n, e in zip(ntag_list, etag_list) if len(e) > 0]
        # map gmsh node tags to 0-based indices
        idx = np.zeros(int(node_tags.max()) + 1, dtype=np.int64)
        idx[node_tags] = np.arange(len(node_tags))
        t = idx[np.concatenate(ntags)].T  # (3, nelem)
        cell_sets: dict[str, np.ndarray] = {}
        all_etags = np.concatenate(etags)
        order = np.argsort(all_etags)
        sorted_etags = all_etags[order]
        for phys_dim, phys_tag in gmsh.model.getPhysicalGroups():
            if phys_dim != 2:
                continue
            name = gmsh.model.getPhysicalName(phys_dim, phys_tag)
            ent_tags = gmsh.model.getEntitiesForPhysicalGroup(phys_dim, phys_tag)
            petags = np.concatenate(
                [e for ent in ent_tags
                 for e in gmsh.model.mesh.getElements(2, ent)[1] if len(e)])
            cell_sets[name] = order[np.searchsorted(sorted_etags, petags)]
    finally:
        gmsh.finalize()
    return MeshTri(p, t), cell_sets


@BilinearForm
def _diffusion(u, v, _):
    from skfem.helpers import dot, grad
    return dot(grad(u), grad(v))


@BilinearForm
def _mass(u, v, _):
    return u * v


def solve_az(
    msh_file: Path,
    materials: dict[str, float],
    current_density: dict[str, float],
) -> dict:
    """Solve nu-Laplace(A) problem on a gmsh mesh.

    materials: physical-group name -> relative permeability mu_r
    current_density: physical-group name -> Jz in A/m^2 (default 0)
    Returns dict with element-centroid coords, Bx, By, nodal A.
    """
    mesh, cell_sets = load_gmsh_mesh(msh_file)
    basis = Basis(mesh, ElementTriP1())

    A = None
    b = np.zeros(basis.N)
    for name, mu_r in materials.items():
        cells = np.asarray(cell_sets.get(name, []), dtype=np.int64)
        if cells.size == 0:
            continue
        sub = Basis(mesh, ElementTriP1(), elements=cells)
        K = asm(_diffusion, sub).tocsr()
        A = K * (1.0 / (MU0 * mu_r)) if A is None else A + K * (1.0 / (MU0 * mu_r))
        J = current_density.get(name, 0.0)
        if J:
            b += J * np.asarray(asm(_mass, sub).sum(axis=1)).flatten()

    # outer wall: nodal dofs on the largest-radius boundary circle
    p = mesh.p
    r = np.hypot(p[0], p[1])
    D = np.where(r >= r.max() - 1e-9 * r.max())[0]
    u = solve(*condense(A, b, D=D))

    # element-wise constant B for P1 elements
    w = basis.interpolate(u)
    Bx = w.grad[1, :, 0]
    By = -w.grad[0, :, 0]
    ct = mesh.p[:, mesh.t].mean(axis=1)
    return {"mesh": mesh, "A": u, "cx": ct[0], "cy": ct[1],
            "Bx": Bx, "By": By, "ndofs": basis.N, "nelems": mesh.t.shape[1]}


def b_magnitude_at(sol: dict, x: float, y: float) -> float:
    """|B| at the mesh node nearest (x, y), averaged over its incident elements.

    Element-centroid sampling alone loses ~O(h) accuracy; averaging over the
    patch around the nearest node recovers the nodal superconvergence.
    """
    mesh = sol["mesh"]
    p = mesh.p
    d2 = (p[0] - x) ** 2 + (p[1] - y) ** 2
    node = int(np.argmin(d2))
    incident = np.any(mesh.t == node, axis=0)
    return float(np.mean(np.hypot(sol["Bx"][incident], sol["By"][incident])))


def wire_problem(out_dir: Path, lcar: float, r_cond: float = 0.005,
                 r_domain: float = 0.2, current: float = 1000.0) -> Path:
    """Straight round wire along z in a circular air domain.

    Analytic (anywhere outside the conductor): B(r) = mu0 * I / (2*pi*r).
    Returns the .msh path. Physical groups: 'conductor', 'air', 'outer'.
    """
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        # two point pairs (one on each circle) + arcs make closed loops
        gmsh.model.geo.addPoint(r_cond, 0, 0, tag=11)
        gmsh.model.geo.addPoint(0, 0, 0, tag=12)      # center for inner arc
        gmsh.model.geo.addPoint(-r_cond, 0, 0, tag=13)
        gmsh.model.geo.addPoint(r_domain, 0, 0, tag=21)
        gmsh.model.geo.addPoint(0, 0, 0, tag=22)      # center for outer arc
        gmsh.model.geo.addPoint(-r_domain, 0, 0, tag=23)
        # inner circle (conductor boundary), CCW via two 180-deg arcs
        gmsh.model.geo.addCircleArc(11, 12, 13, tag=1)
        gmsh.model.geo.addCircleArc(13, 12, 11, tag=2)
        # outer circle (domain boundary)
        gmsh.model.geo.addCircleArc(21, 22, 23, tag=3)
        gmsh.model.geo.addCircleArc(23, 22, 21, tag=4)
        gmsh.model.geo.addCurveLoop([1, 2], tag=10)    # conductor boundary
        gmsh.model.geo.addCurveLoop([3, 4], tag=20)    # domain boundary
        gmsh.model.geo.addPlaneSurface([20, 10], tag=30)  # air annulus
        gmsh.model.geo.addPlaneSurface([10], tag=31)      # conductor disk
        gmsh.model.geo.synchronize()
        gmsh.model.addPhysicalGroup(2, [30], tag=1)
        gmsh.model.setPhysicalName(2, 1, "air")
        gmsh.model.addPhysicalGroup(2, [31], tag=2)
        gmsh.model.setPhysicalName(2, 2, "conductor")
        gmsh.model.addPhysicalGroup(1, [3, 4], tag=3)
        gmsh.model.setPhysicalName(1, 3, "outer")
        gmsh.model.mesh.setSize([(0, 11), (0, 13)], min(lcar, 2 * r_cond))
        gmsh.model.mesh.setSize([(0, 21), (0, 23)], lcar)
        # refine the annulus interior so h tracks lcar away from the boundary
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        gmsh.model.mesh.setSize([(0, 11), (0, 13)], lcar / 4)
        gmsh.model.mesh.generate(2)
        out = out_dir / f"wire_lcar{lcar:.0e}.msh"
        gmsh.write(str(out))
    finally:
        gmsh.finalize()
    return out


if __name__ == "__main__":
    import sys
    sol = solve_az(Path(sys.argv[1]), {"air": 1.0, "conductor": 1.0},
                   {"conductor": 1000.0 / (np.pi * 0.005 ** 2)})
    print(f"{sol['nelems']} elements, {sol['ndofs']} dofs")
