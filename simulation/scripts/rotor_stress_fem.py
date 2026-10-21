"""Gate B (rotor mechanics) for the deep-barrier rotor: 2D plane-stress FE.

Why this exists: `rotor_stress_check.py` is a first-order ring/spoke model that
assumes a continuous surface annulus. The D-014 candidate has four full-depth
barriers, so the hoop load is shared between the 0.6 mm surface bridge and three
3.8 mm arc ribs. That load sharing is statically indeterminate - it needs a field
solve, not a hand factor.

Model (declared in validation/rotor_stress/PLAN.md before running):
- rotor lamination only (iron, barriers are traction-free holes),
- plane stress, E = 200 GPa, nu = 0.30, rho = 7870 kg/m^3,
- centrifugal body force f = rho*w^2*r,
- shaft bore fully fixed (press fit on a much stiffer steel shaft; conservative).
- inter-lamination shear, shrink-fit preload and thermal stress are NOT modelled.

Run:  .venv/bin/python simulation/scripts/rotor_stress_fem.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from skfem import Basis, ElementTriP1, ElementVector, MeshTri, asm, condense, solve
from skfem import BilinearForm, LinearForm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dq_model import BORE  # noqa: E402  (130 mm point design, not the 92 mm anchor)
from rajini_anchor import AIRGAP  # noqa: E402
from synrm_geometry import rotor_barriers  # noqa: E402
from synrm_mesh import barrier_bands, classify_point  # noqa: E402
from envelope_validation import build  # noqa: E402

E = 200e9
NU = 0.30
RHO = 7870.0
SIGMA_Y = 230e6          # MPa, same declared conservative yield as Gate B
SF_RULE = 2.0            # frozen pass rule: SF >= 2.0

CAND = dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
            barrier_span=0.0445)


# ----------------------------------------------------------------------------- mesh
def polar_mesh(r_feat, th_rays, h_target=0.0008, closed=True):
    """Polar grid, refined to ~h_target radially; closed=False leaves a sector."""
    r_feat = np.unique(np.round(np.asarray(r_feat, float), 10))
    radii = [r_feat[0]]
    for r1, r2 in zip(r_feat[:-1], r_feat[1:]):
        n = max(1, int(math.ceil((r2 - r1) / h_target)))
        radii += list(np.linspace(r1, r2, n + 1)[1:])
    r = np.unique(np.round(radii, 10))

    th = np.unique(np.mod(np.asarray(th_rays, float), 2 * math.pi))
    th = th[np.r_[True, np.diff(th) > 1e-6]]

    nodes = [(0.0, 0.0)] if r[0] < 1e-15 else []
    rings = []
    n_ray = len(th)
    for rk in r:
        if rk < 1e-15:
            continue
        idx = np.arange(len(nodes), len(nodes) + n_ray)
        for t in th:
            nodes.append((rk * math.cos(t), rk * math.sin(t)))
        rings.append(idx)

    pts = np.array(nodes).T
    tris = []
    n_seg = n_ray if closed else n_ray - 1
    start = 0
    if r[0] < 1e-15 and len(rings) > 1:
        # fan from the centre to the first ring
        for i in range(n_seg):
            tris.append((0, rings[0][i], rings[0][(i + 1) % n_ray]))
        start = 1
    for k in range(start, len(rings) - 1):
        ia, ib = rings[k], rings[k + 1]
        for i in range(n_seg):
            i2 = (i + 1) % n_ray
            tris.append((ia[i], ib[i], ia[i2]))
            tris.append((ib[i], ib[i2], ia[i2]))
    t = np.array(tris).T
    mesh = MeshTri(pts, t)
    return mesh


def rotor_mesh(g, n_theta=720, h=0.0008):
    """Rotor-iron mesh only; rays carry the barrier edges exactly."""
    r_sh = g.shaft_od / 2
    r_ro = g.rotor_od / 2
    pp = 2 * math.pi / g.rotor_n_poles
    hs = (g.barrier_angle_frac * pp) / 2
    th = 2 * math.pi * np.arange(n_theta) / n_theta
    extra = [k * pp + g.barrier_center_angle + s * hs
             for k in range(g.rotor_n_poles) for s in (-1, 1)]
    th = np.concatenate([th, np.mod(extra, 2 * math.pi)])
    feat = [r_sh, r_ro - g.bridge, r_ro]
    for r_i, r_o in barrier_bands(g):
        feat += [r_i, r_o]
    mesh = polar_mesh(feat, th, h, closed=True)

    cx, cy = mesh.p[:, mesh.t].mean(axis=1)
    reg = classify_point(g, cx, cy)
    keep = np.flatnonzero(reg == "rotor_iron")
    m = MeshTri(mesh.p, mesh.t[:, keep])
    m = m.remove_unused_nodes()
    return m


# ------------------------------------------------------------------------- mechanics
@BilinearForm
def _stiff(u, v, w):
    from skfem.helpers import sym_grad, trace, ddot
    eps_u = sym_grad(u)
    eps_v = sym_grad(v)
    lam = E * NU / (1 - NU**2)
    mu = E / (2 * (1 + NU))
    tr = trace(eps_u)
    I2 = np.eye(2)[:, :, None, None]
    sig = 2 * mu * eps_u + lam * tr[None, None, :, :] * I2
    return ddot(sig, eps_v)


def solve_spin(mesh, omega, fixed_nodes):
    basis = Basis(mesh, ElementVector(ElementTriP1()))
    A_ = asm(_stiff, basis)

    @LinearForm
    def f(v, w):
        return RHO * omega**2 * (w.x[0] * v[0] + w.x[1] * v[1])

    b = asm(f, basis)
    D = np.concatenate([basis.nodal_dofs[0, fixed_nodes],
                        basis.nodal_dofs[1, fixed_nodes]])
    u = solve(*condense(A_, b, D=D))
    return basis, u


def elem_stress(mesh, u):
    """Constant-strain plane-stress field per element, from P1 displacements."""
    p = mesh.p
    t = mesh.t
    uu = u.reshape(-1, 2)
    B = np.empty((t.shape[1], 3, 3))
    B[:, :, 0] = 1.0
    B[:, :, 1] = p[0, t].T
    B[:, :, 2] = p[1, t].T
    invB = np.linalg.inv(B)
    vals = np.empty((t.shape[1], 3, 2))
    vals[:, :, 0] = uu[t, 0].T
    vals[:, :, 1] = uu[t, 1].T
    g = np.einsum("eij,ejk->eik", invB, vals)   # [., 0]=value, [.,1]=d/dx, [.,2]=d/dy
    dux_dx, duy_dx = g[:, 1, 0], g[:, 1, 1]
    dux_dy, duy_dy = g[:, 2, 0], g[:, 2, 1]
    exx, eyy, gxy = dux_dx, duy_dy, dux_dy + duy_dx
    c = E / (1 - NU**2)
    sxx = c * (exx + NU * eyy)
    syy = c * (NU * exx + eyy)
    sxy = c * (1 - NU) / 2 * gxy
    vm = np.sqrt(sxx**2 - sxx * syy + syy**2 + 3 * sxy**2)
    return sxx, syy, sxy, vm


def area_of(mesh):
    p, t = mesh.p, mesh.t
    x0, y0 = p[0, t[0]], p[1, t[0]]
    x1, y1 = p[0, t[1]], p[1, t[1]]
    x2, y2 = p[0, t[2]], p[1, t[2]]
    return 0.5 * np.abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0))


# ------------------------------------------------------------- known-answer check
def known_answer_disk(R=0.0645, n_theta=360, h=0.0008):
    """Solid rotating disk, 90-deg sector with symmetry BCs vs the exact field."""
    feat = np.linspace(0.0, R, max(2, int(R / h) + 1))
    th = np.linspace(0.0, np.pi / 2, n_theta + 1)
    mesh = polar_mesh(feat, th, h, closed=False)
    basis = Basis(mesh, ElementVector(ElementTriP1()))
    A_ = asm(_stiff, basis)
    omega = 2 * math.pi * 6000 / 60

    @LinearForm
    def f(v, w):
        return RHO * omega**2 * (w.x[0] * v[0] + w.x[1] * v[1])

    b = asm(f, basis)
    x, y = mesh.p
    on_x = np.flatnonzero((np.abs(y) < 1e-12) & (x > 1e-12))    # theta = 0
    on_y = np.flatnonzero((np.abs(x) < 1e-12) & (y > 1e-12))    # theta = pi/2
    D = np.concatenate([basis.nodal_dofs[1, on_x], basis.nodal_dofs[0, on_y]])
    u = solve(*condense(A_, b, D=D))

    sxx, syy, sxy, _ = elem_stress(mesh, u)
    # axisymmetric field: compare principal stresses (Cartesian components rotate)
    sm = 0.5 * (sxx + syy)
    rad = np.sqrt((0.5 * (sxx - syy))**2 + sxy**2)
    s1, s2 = sm + rad, sm - rad
    cx, cy = mesh.p[:, mesh.t].mean(axis=1)
    r = np.hypot(cx, cy)
    # exact: sigma_t (major), sigma_r (minor) for a solid disk
    c = RHO * omega**2 / 8
    sr = c * (3 + NU) * (R**2 - r**2)
    st = c * ((3 + NU) * R**2 - (1 + 3 * NU) * r**2)
    sel = (r > 0.55 * R) & (r < 0.65 * R)
    err_r = np.max(np.abs(s2[sel] - sr[sel])) / np.max(np.abs(sr[sel]))
    err_t = np.max(np.abs(s1[sel] - st[sel])) / np.max(np.abs(st[sel]))
    return err_r, err_t, float(np.max(st))


# ------------------------------------------------------------------------- reporting
def run_case(name, g, rpm, n_theta, h=0.0008):
    mesh = rotor_mesh(g, n_theta=n_theta, h=h)
    omega = 2 * math.pi * rpm / 60
    r = np.hypot(mesh.p[0], mesh.p[1])
    fixed = np.flatnonzero(r <= g.shaft_od / 2 + 1e-9)
    if fixed.size == 0:
        fixed = np.flatnonzero(r <= r.min() + 1e-9)
    basis, u = solve_spin(mesh, omega, fixed)
    sxx, syy, sxy, vm = elem_stress(mesh, u)
    ar = area_of(mesh)
    cx, cy = mesh.p[:, mesh.t].mean(axis=1)
    rr = np.hypot(cx, cy)

    # distance to the nearest sharp barrier corner (4 poles x bands x 2 angles)
    bb = barrier_bands(g)
    pp = 2 * math.pi / g.rotor_n_poles
    hs = g.barrier_angle_frac * pp / 2
    corners = np.array([(rb * math.cos(k * pp + g.barrier_center_angle + s * hs),
                         rb * math.sin(k * pp + g.barrier_center_angle + s * hs))
                        for k in range(g.rotor_n_poles)
                        for rb in (rr_ for band in bb for rr_ in band)
                        for s in (-1, 1)])
    d = np.sqrt((cx[:, None] - corners[None, :, 0])**2
                + (cy[:, None] - corners[None, :, 1])**2).min(axis=1)

    clean = d > 0.5e-3          # M3: corner-singular elements are excluded

    def pct(q):
        v, a = vm[clean], ar[clean]
        o = np.argsort(v)
        cum = np.cumsum(a[o]) / a.sum()
        return float(v[o][np.searchsorted(cum, q)])

    # radial growth of the rotor OD (airgap-closure sanity)
    ud = u.reshape(-1, 2)
    on_od = np.flatnonzero(np.abs(np.hypot(mesh.p[0], mesh.p[1]) - g.rotor_od / 2) < 1e-9)
    growth = float(np.mean((ud[on_od] * mesh.p[:, on_od].T).sum(axis=1)
                           / np.hypot(mesh.p[0, on_od], mesh.p[1, on_od]))) if on_od.size else 0.0
    return dict(name=name, rpm=rpm, nel=max(mesh.t.shape[1], 1), vm=vm, r=rr,
                growth=growth,
                d=d, p95=pct(0.95), p99=pct(0.99), p995=pct(0.995),
                corner_frac=float(ar[~clean].sum() / ar.sum()),
                vmax=float(vm.max()), vmax_r=float(rr[np.argmax(vm)]),
                vmax_d=float(d[np.argmax(vm)]),
                bridge=float(vm[(rr > g.rotor_od / 2 - g.bridge - 0.0002)].max())
                if (rr > g.rotor_od / 2 - g.bridge - 0.0002).any() else 0.0)


def main() -> int:
    print("Gate B FE: plane stress, E=%.0f GPa, nu=%.2f, rho=%.0f, yield %.0f MPa"
          % (E / 1e9, NU, RHO, SIGMA_Y / 1e6))
    print("pass rule (declared): SF >= %.1f on the hot-spot statistic "
          "(p99.5 of von Mises, area-weighted)" % SF_RULE)

    err_r, err_t, st_max = known_answer_disk()
    print(f"\nM0 known answer (solid disk, 6000 rpm, 90-deg sector): "
          f"sigma_r err {err_r:.2%}, sigma_t err {err_t:.2%}, peak sigma_t {st_max/1e6:.2f} MPa")
    assert err_r < 0.05 and err_t < 0.05, "FE does not reproduce the solid-disk answer"

    g = build(26.25, BORE, **CAND)
    print(f"\ncandidate S6: {CAND['n_barriers']} barriers, span "
          f"{CAND['barrier_span']*1e3:.1f} mm, rib {CAND['barrier_gap_frac']}, "
          f"bridge {g.bridge*1e3:.1f} mm")
    print("rpm   mesh      nel    max [MPa] (at r, corner dist)   p99.5   p99    bridge   corner area")
    rows = {}
    for rpm in (6000, 7000):
        for n_theta in (720, 1080):
            r = run_case("S6", g, rpm, n_theta)
            rows[(rpm, n_theta)] = r
            print(f"{rpm:5d} {n_theta:5d} {r['nel']:7d}   {r['vmax']/1e6:7.1f} "
                  f"({r['vmax_r']*1e3:5.1f} mm, {r['vmax_d']*1e3:5.2f} mm)    "
                  f"{r['p995']/1e6:6.1f} {r['p99']/1e6:6.1f} {r['bridge']/1e6:6.1f}  "
                  f"{r['corner_frac']:6.2%}")

    # M1 mesh independence of the hot-spot statistic
    for rpm in (6000, 7000):
        a, b = rows[(rpm, 720)], rows[(rpm, 1080)]
        dev = b["p995"] / a["p995"] - 1
        print(f"M1 {rpm} rpm: p99.5 {a['p995']/1e6:.1f} -> {b['p995']/1e6:.1f} MPa "
              f"({dev:+.1%})")
        assert abs(dev) < 0.10, "hot-spot statistic is mesh dependent"

    ok = True
    for rpm in (6000, 7000):
        r = rows[(rpm, 1080)]
        sf = SIGMA_Y / r["p995"]
        passed = sf >= SF_RULE
        ok &= passed
        print(f"M2 {rpm} rpm: p99.5 {r['p995']/1e6:.1f} MPa -> SF {sf:.1f} "
              f"({'PASS' if passed else 'FAIL'} vs {SF_RULE})")

    a, b = rows[(6000, 720)], rows[(6000, 1080)]
    print(f"\nairgap closure: rotor OD grows {rows[(7000,1080)]['growth']*1e6:.1f} um at "
          f"7000 rpm vs {AIRGAP*1e6:.0f} um airgap "
          f"({rows[(7000,1080)]['growth']/AIRGAP:.1%})")
    print(f"\nM3 corner check: max rises {a['vmax']/1e6:.1f} -> {b['vmax']/1e6:.1f} MPa "
          f"({b['vmax']/a['vmax']-1:+.1%}) at {b['vmax_d']*1e3:.2f} mm from a barrier "
          f"corner -> {'corner singularity' if b['vmax_d'] < 0.5e-3 else 'NOT a corner'}")
    print(f"\nGate B {'PASS' if ok else 'FAIL'} on the declared p99.5 rule. "
          f"Peak values are reported but are corner peaks (excluded by rule).")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
