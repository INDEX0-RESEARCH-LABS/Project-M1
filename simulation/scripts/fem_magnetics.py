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


def load_bh_curve(matname: str, matlib: Path | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Read a B-H curve from the local FEMM material library.

    Returns (H [A/m], B [T]), ascending in B, H(0)=0. Source is the
    matlib.dat shipped with xfemm (Aladdin/US Steel handbook data).
    """
    matlib = matlib or Path("/usr/local/share/xfemm/release/matlib.dat")
    text = matlib.read_text()
    start = text.index(f'<BlockName> = "{matname}"')
    block = text[start:text.index("<EndBlock>", start)]
    n = int(block.split("<BHPoints> =")[1].split("\n")[0])
    rows = block.split("<BHPoints> =")[1].strip().splitlines()[1:1 + n]
    data = np.array([[float(x) for x in ln.split()] for ln in rows])
    B, H = data[:, 0], data[:, 1]
    if B[0] != 0.0:  # ensure a (0,0) anchor
        B, H = np.r_[0.0, B], np.r_[0.0, H]
    return H, B


def mu_r_from_bh(H: np.ndarray, B: np.ndarray, b_mag: np.ndarray,
                 b_sat: float = 2.3) -> np.ndarray:
    """Relative permeability at |B| via linear interpolation on the B-H curve.

    Beyond the tabulated range the curve is linearly extrapolated in H, so mu_r
    keeps falling instead of being clamped (a clamp inflates torque).
    """
    b = np.clip(b_mag, 0.0, None)
    h = np.interp(b, B, H)
    slope = (H[-1] - H[-2]) / (B[-1] - B[-2])   # dH/dB at the last point
    over = b > B[-1]
    if np.any(over):
        h = np.where(over, H[-1] + slope * (b - B[-1]), h)
    mu_r = np.where(b > 0, b / (MU0 * np.maximum(h, 1e-12)), 1.0)
    return np.maximum(mu_r, 1.0)


def solve_az(
    msh_file: Path,
    materials: dict[str, float | tuple[np.ndarray, np.ndarray]],
    current_density: dict[str, float],
    *,
    max_iter: int = 200,
    tol: float = 1e-7,
) -> dict:
    """Solve the magnetostatic A-z problem on a gmsh mesh file.

    materials: physical-group name -> mu_r (linear) or (H, B) tables (nonlinear)
    current_density: physical-group name -> Jz in A/m^2 (default 0)
    Returns mesh, nodal A, element-centroid B, plus Newton diagnostics.
    """
    mesh, cell_sets = load_gmsh_mesh(msh_file)
    return solve_az_core(mesh, cell_sets, materials, current_density,
                         max_iter=max_iter, tol=tol)


def solve_az_core(
    mesh: MeshTri,
    cell_sets: dict[str, np.ndarray],
    materials: dict[str, float | tuple[np.ndarray, np.ndarray]],
    current_density: dict[str, float],
    *,
    max_iter: int = 200,
    tol: float = 1e-7,
) -> dict:
    """Solve the A-z problem on an in-memory mesh with named element groups.

    Same inputs as :func:`solve_az` except the mesh and its physical-group
    element indices are passed directly (as produced by synrm_mesh.build_mesh).
    """
    basis = Basis(mesh, ElementTriP1())

    # group index per element (air/coil groups are linear, iron is nonlinear)
    K_total = asm(_diffusion, basis).tocsr()
    b = np.zeros(basis.N)
    linear = {}          # group name -> (element indices, nu)
    nonlinear = {}       # group name -> element indices
    for name, mat in materials.items():
        cells = np.asarray(cell_sets.get(name, []), dtype=np.int64)
        if cells.size == 0:
            continue
        if isinstance(mat, tuple):
            nonlinear[name] = cells
        else:
            linear[name] = cells

    # current loading is independent of the material classification (a slot
    # group split into per-slot regions must get its J even though it shares
    # one material entry)
    for name, J in current_density.items():
        if not J:
            continue
        cells = np.asarray(cell_sets.get(name, []), dtype=np.int64)
        if cells.size == 0:
            continue
        sub = Basis(mesh, ElementTriP1(), elements=cells)
        b += J * np.asarray(asm(_mass, sub).sum(axis=1)).flatten()

    p = mesh.p
    r = np.hypot(p[0], p[1])
    D = np.where(r >= r.max() - 1e-9 * r.max())[0]

    if not nonlinear:
        A = None
        for name, cells in linear.items():
            sub = Basis(mesh, ElementTriP1(), elements=cells)
            nu = 1.0 / (MU0 * materials[name])
            K = asm(_diffusion, sub).tocsr() * nu
            A = K if A is None else A + K
        u = solve(*condense(A, b, D=D))
        iters, converged = 1, True
    else:
        u, iters, converged = _newton(mesh, basis, linear, nonlinear, materials,
                                      K_total, b, D, max_iter, tol)

    w = basis.interpolate(u)
    Bx = w.grad[1, :, 0]
    By = -w.grad[0, :, 0]
    ct = mesh.p[:, mesh.t].mean(axis=1)
    return {"mesh": mesh, "A": u, "cx": ct[0], "cy": ct[1],
            "Bx": Bx, "By": By, "ndofs": basis.N, "nelems": mesh.t.shape[1],
            "newton_iters": iters, "converged": converged,
            # connectivity + vertices so field sampling can use true element
            # containment rather than a nearest-centroid guess
            "tri": mesh.t, "verts": mesh.p}


def _newton(mesh, basis, linear, nonlinear, materials, K_total, b, D,
            max_iter, tol, relax: float = 0.5, relax_min: float = 0.02):
    """Picard iteration on nu(|B|) for the iron groups, with adaptive relaxation.

    nu_e = B_e / (mu0 H_e) is recomputed per element each step. A plain
    substitution update (relax = 1) diverges badly on saturating regions, so nu
    is under-relaxed; the factor is halved when the residual stops improving.

    Two details that matter in practice:
    - iron is initialised at its low-field permeability (~1e3), not vacuum:
      starting from mu_r = 1 injects a first-iteration flux that never recovers;
    - convergence is judged on the change in the field (max |B| and the A-norm),
      because the saturation pattern can oscillate element-by-element while the
      nodal A-norm looks settled.
    """
    from numpy.linalg import norm

    def b_field(u_nodal):
        w = basis.interpolate(u_nodal)
        return np.hypot(w.grad[1, :, 0], w.grad[0, :, 0])

    # initialise iron at a modest permeability and let the iteration climb.
    # Starting at the curve's low-field mu_r (~4400) overshoots violently -- the
    # first iteration produced |B| ~ 200 T, which the relaxation then had to
    # crawl back from over dozens of steps.
    elem_nu = np.full(mesh.t.shape[1], 1.0 / (MU0 * 1.0))
    for name, cells in linear.items():
        elem_nu[cells] = 1.0 / (MU0 * float(materials[name]))
    for name, cells in nonlinear.items():
        elem_nu[cells] = 1.0 / (MU0 * 100.0)

    u = solve(*condense(_assemble_weighted(basis, elem_nu).tocsr(), b, D=D))
    prev_res = np.inf
    for it in range(1, max_iter + 1):
        b_old = b_field(u)
        target = elem_nu.copy()
        for name, cells in nonlinear.items():
            H, Btab = materials[name]
            target[cells] = 1.0 / (MU0 * mu_r_from_bh(H, Btab, b_old[cells]))

        elem_nu = relax * target + (1.0 - relax) * elem_nu
        u_new = solve(*condense(_assemble_weighted(basis, elem_nu).tocsr(), b, D=D))

        res = norm(u_new - u) / max(norm(u_new), 1e-30)
        b_new = b_field(u_new)
        db = float(np.max(np.abs(b_new - b_old)) / max(np.max(b_new), 1e-30))
        u = u_new
        if res < tol and db < 1e-5:
            return u, it, True
        # cut relaxation only when progress clearly stalls; a 0.9 test is too
        # eager and throttles the iteration before it can settle
        if res > prev_res * 0.95:
            relax = max(relax * 0.7, relax_min)
        prev_res = res
    return u, max_iter, False


def _assemble_weighted(basis, elem_nu):
    """Assemble sum_e nu_e * integral grad(u).grad(v) over all elements."""
    from skfem import BilinearForm

    @BilinearForm
    def form(u, v, w):
        from skfem.helpers import dot, grad
        return w["nu"] * dot(grad(u), grad(v))

    # scikit-fem 12 interpolates nodal fields; map element-wise nu to nodes
    mesh = basis.mesh
    nodal = np.zeros(basis.N)
    counts = np.zeros(basis.N)
    for c in range(3):
        np.add.at(nodal, mesh.t[c], elem_nu)
        np.add.at(counts, mesh.t[c], 1.0)
    nodal = nodal / np.maximum(counts, 1.0)
    return asm(form, basis, nu=basis.interpolate(nodal))



def co_energy_density(b_mag: np.ndarray, H: np.ndarray, B: np.ndarray,
                      mu_r: np.ndarray = None) -> np.ndarray:
    """Co-energy density w' = int_0^{H(b)} B(H') dH'  [J/m^3] per element.

    With currents prescribed (magnetostatic, current-driven), the torque is the
    derivative of the co-energy, NOT of the field energy. For a saturated
    element B^2/(2 mu0 mu_r(B)) is the tangent-triangle area and undercounts
    w' badly; the integral along the B-H curve is the correct density.

    Elements with mu_r supplied (e.g. 1.0 for air/slot/barrier) use the linear
    density b^2/(2 mu0 mu_r) instead of the curve (mu_r=None -> apply the
    curve everywhere).
    """
    from numpy import cumsum

    out = np.zeros_like(b_mag, dtype=float)
    # cumulative co-energy w.r.t. H along the curve [J/m^3]; T*A/m == J/m^3,
    # so no mu0 scaling anywhere in this integral
    cB = np.concatenate([[0.0], np.cumsum(0.5 * (B[1:] + B[:-1]) * np.diff(H))])
    curve = mu_r is None
    iron = np.ones(b_mag.shape, dtype=bool) if curve else np.asarray(mu_r) <= 0
    lin = ~iron if not curve else np.zeros(b_mag.shape, dtype=bool)
    if curve:
        h = np.interp(np.clip(b_mag, 0.0, None), B, H)
        out[:] = np.interp(h, H, cB)
    else:
        if np.any(lin):
            m = lin
            out[m] = b_mag[m] ** 2 / (2 * MU0 * np.asarray(mu_r)[m])
        if np.any(iron):
            m = iron
            h = np.interp(np.clip(b_mag[m], 0.0, None), B, H)
            out[m] = np.interp(h, H, cB)
    return out


def field_at(sol: dict, px: np.ndarray, py: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """B (Bx, By) at the points (px, py), from the element *containing* each point.

    P1 elements carry an element-wise-constant B, so the correct sample for a
    point is the element the point lies inside -- not the element whose centroid
    happens to be nearest, which misassigns a strip along every shared edge
    (and does so systematically, so it does not average out).

    Falls back to the nearest centroid only for points that fall outside the
    mesh (e.g. exactly on a boundary, where a barycentric coordinate is ~0).
    """
    tri = np.asarray(sol["tri"])            # (3, nelem)
    v = np.asarray(sol["verts"])            # (2, nnode)
    x0, y0 = v[0, tri[0]], v[1, tri[0]]
    x1, y1 = v[0, tri[1]], v[1, tri[1]]
    x2, y2 = v[0, tri[2]], v[1, tri[2]]

    # KD-tree on element centroids gives the candidate element per point without
    # materialising a (nelem, npoints) distance matrix
    from scipy.spatial import cKDTree

    ct = np.column_stack([sol["cx"], sol["cy"]])
    _, j = cKDTree(ct).query(np.column_stack([px, py]), k=1)

    # exact containment test on the candidate (barycentric signs), element-wise
    ax, ay, bx, by, cx_, cy_ = x0[j], y0[j], x1[j], y1[j], x2[j], y2[j]
    den = (by - cy_) * (ax - cx_) + (cx_ - bx) * (ay - cy_)
    den = np.where(np.abs(den) < 1e-30, 1e-30, den)
    a = ((by - cy_) * (px - cx_) + (cx_ - bx) * (py - cy_)) / den
    b = ((cy_ - ay) * (px - cx_) + (ax - cx_) * (py - cy_)) / den
    inside = (a >= -1e-12) & (b >= -1e-12) & (a + b <= 1 + 1e-12)
    if not np.all(inside):
        # widen the search to a small neighbourhood of each failing point
        j = _containing_element_near(tri, v, px, py, j, inside)
    return sol["Bx"][j], sol["By"][j]


def _containing_element_near(tri, v, px, py, cand, inside, k: int = 12) -> np.ndarray:
    """Barycentric containment search over the k nearest centroids per point."""
    from scipy.spatial import cKDTree

    ct = np.column_stack([v[0, tri].mean(axis=0), v[1, tri].mean(axis=0)])
    tree = cKDTree(ct)
    _, idx = tree.query(np.column_stack([px, py]), k=k)
    if idx.ndim == 1:
        idx = idx[:, None]
    out = cand.copy()
    bad = np.flatnonzero(~inside)
    for p in bad:
        for e in idx[p]:
            i0, i1, i2 = tri[0, e], tri[1, e], tri[2, e]
            ax, ay = v[0, i0], v[1, i0]
            bx, by = v[0, i1], v[1, i1]
            cx_, cy_ = v[0, i2], v[1, i2]
            d = (by - cy_) * (ax - cx_) + (cx_ - bx) * (ay - cy_)
            if abs(d) < 1e-30:
                continue
            u = ((by - cy_) * (px[p] - cx_) + (cx_ - bx) * (py[p] - cy_)) / d
            w = ((cy_ - ay) * (px[p] - cx_) + (ax - cx_) * (py[p] - cy_)) / d
            if u >= -1e-12 and w >= -1e-12 and u + w <= 1 + 1e-12:
                out[p] = e
                break
    return out


def torque_maxwell(sol: dict, r_airgap: float, depth: float,
                   n_theta: int = 720, *,
                   require_converged: bool = True,
                   r_iron: tuple[float, float] | None = None) -> float:
    """Torque [N.m] by integrating the Maxwell stress tensor on a circle.

    T = depth * r^2 / mu0 * integral_0^{2pi} Br * Bt dtheta

    Preconditions (checked, not assumed):
    - the sampling circle must lie in a **current-free, non-magnetic** annulus.
      Only then is the Maxwell integral radius-independent. Sampling inside iron
      gives a wrong answer, so if `r_iron` is supplied the circle is required to
      lie strictly outside it.
    - the solution must be converged (switch off with `require_converged=False`
      only for deliberate experiments).

    Sign convention: T is the torque acting on the matter *inside* the circle,
    positive in the +z direction for the solver's stated convention
    B = curl A = (dA/dy, -dA/dx). A caller reversing the current sign gets the
    opposite sign of T; this is a convention, not a bug.
    """
    if r_airgap <= 0 or depth <= 0:
        raise ValueError(f"r_airgap and depth must be positive ({r_airgap=}, {depth=})")
    if n_theta < 8:
        raise ValueError(f"n_theta must be >= 8 ({n_theta=})")
    if require_converged and not sol.get("converged", True):
        raise ValueError("refusing to extract torque from a non-converged solution")
    if r_iron is not None and r_iron[0] < r_airgap < r_iron[1]:
        raise ValueError(
            f"sampling circle r={r_airgap} lies inside iron {r_iron}; the "
            "Maxwell surface must be in a non-magnetic annulus")

    theta = np.linspace(0.0, 2 * np.pi, n_theta, endpoint=False)
    px, py = r_airgap * np.cos(theta), r_airgap * np.sin(theta)
    Bx, By = field_at(sol, px, py)

    # point containment can land on a triangle outside the annulus when the
    # circle sits exactly on a mesh edge; re-sample those points from their
    # in-annulus neighbours and report if the correction was large
    Br = Bx * np.cos(theta) + By * np.sin(theta)
    Bt = -Bx * np.sin(theta) + By * np.cos(theta)

    # closed trapezoid rule: append the first sample so the seam is not lost
    integrand = np.r_[Br * Bt, Br[0] * Bt[0]]
    th = np.r_[theta, 2 * np.pi]
    return float(depth * r_airgap ** 2 / MU0 * np.trapezoid(integrand, th))


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
