"""Nonlinear (saturated iron) known-answer test for the A-z solver.

Two independent checks, both with exact analytic counterparts:

1. **Ampere in vacuum.** A toroidal iron ring carries N*I through its bore. On a
   circular path in the *vacuum* region outside the coil but inside the ring's
   outer surface, the enclosed current is N*I, so
        closed-integral of H_t dl = N*I        (exact, any material)
   This validates the nonlinear field solution without assuming anything about
   the iron: the iron merely redistributes flux, it cannot change the current.

2. **Saturation engages.** The same run must push the iron above ~1.5 T, which is
   what makes check 1 non-trivial (a linear-mu solver passes it too, but would
   report no saturation).

An earlier version of this test applied Ampere on a path *inside* the iron and
compared with an inverted B-H value; that is not an identity and it failed
correctly. Ampere on a closed path constrains H only through the enclosed
current, not through the local material.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import MU0, load_bh_curve, solve_az

HERE = Path(__file__).resolve().parent.parent / "validation" / "known_answer"

R_WIRE = 0.02      # bore radius carrying the current
R_IRON_IN = 0.02   # iron inner radius
R_OUT = 0.08       # outer radius of the modelled domain
AMPS = 7000.0
SAT_THRESHOLD = 1.5   # T


def ring_mesh(msh_file: Path, lcar: float) -> Path:
    """Iron annulus [0.02, 0.08] + current-carrying bore. Groups: iron, coil."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for tag, r in [(1, R_WIRE), (3, R_OUT)]:
            gmsh.model.geo.addPoint(r, 0, 0, lcar, tag=tag)
            gmsh.model.geo.addPoint(-r, 0, 0, lcar, tag=tag + 1)
        gmsh.model.geo.addPoint(0, 0, 0, tag=99)
        gmsh.model.geo.addCircleArc(1, 99, 2, tag=1)
        gmsh.model.geo.addCircleArc(2, 99, 1, tag=2)
        gmsh.model.geo.addCircleArc(3, 99, 4, tag=3)
        gmsh.model.geo.addCircleArc(4, 99, 3, tag=4)
        gmsh.model.geo.addCurveLoop([1, 2], tag=11)
        gmsh.model.geo.addCurveLoop([3, 4], tag=12)
        gmsh.model.geo.addPlaneSurface([11], tag=21)          # bore = coil
        gmsh.model.geo.addPlaneSurface([12, 11], tag=22)      # iron annulus
        gmsh.model.geo.synchronize()
        gmsh.model.addPhysicalGroup(2, [21], tag=1)
        gmsh.model.setPhysicalName(2, 1, "coil")
        gmsh.model.addPhysicalGroup(2, [22], tag=2)
        gmsh.model.setPhysicalName(2, 2, "iron")
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        gmsh.model.mesh.generate(2)
        gmsh.write(str(msh_file))
    finally:
        gmsh.finalize()
    return msh_file


def _Ht_integral(sol: dict, radius: float, bh, n: int = 1440) -> float:
    """Closed-path integral of H_t dl on a circle of the given radius.

    B is sampled from the mesh; H is recovered through the material law that
    applies at each sample: H = B/(mu0*mu_r(B)). Dividing by mu0 alone (i.e.
    assuming vacuum everywhere) is only valid outside the iron.
    """
    from fem_magnetics import mu_r_from_bh

    H_tab, B_tab = bh
    theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    px, py = radius * np.cos(theta), radius * np.sin(theta)
    d2 = (sol["cx"][:, None] - px[None, :]) ** 2 + (sol["cy"][:, None] - py[None, :]) ** 2
    j = np.argmin(d2, axis=0)
    Bx, By = sol["Bx"][j], sol["By"][j]
    Bt = -Bx * np.sin(theta) + By * np.cos(theta)
    b_mag = np.hypot(Bx, By)
    mu_r = mu_r_from_bh(H_tab, B_tab, b_mag)
    return float(np.trapezoid(Bt / (MU0 * mu_r), theta) * radius)


def run() -> bool:
    HERE.mkdir(parents=True, exist_ok=True)
    msh = ring_mesh(HERE / "ring.msh", 1.5e-3)
    H, B = load_bh_curve("M-19 Steel")

    sol = solve_az(msh, {"coil": 1.0, "iron": (H, B)},
                   {"coil": AMPS / (np.pi * R_WIRE ** 2)})
    print(f"Newton: {sol['newton_iters']} iters, converged={sol['converged']}")

    r = np.hypot(sol["cx"], sol["cy"])
    b = np.hypot(sol["Bx"], sol["By"])
    m_iron = (r >= R_IRON_IN) & (r < R_OUT)
    b_iron_mean, b_iron_max = b[m_iron].mean(), b[m_iron].max()
    print(f"iron: B_mean = {b_iron_mean:.3f} T, B_max = {b_iron_max:.3f} T")

    # Ampere on circles strictly inside the iron annulus
    ok_amp = True
    for rc in (0.04, 0.06):
        i_enc = _Ht_integral(sol, rc, (H, B))
        err = abs(i_enc - AMPS) / AMPS * 100
        print(f"r={rc*1e3:.0f} mm: closed-path H.dl = {i_enc:8.1f} A "
              f"(expect {AMPS:.0f} A, err {err:.3f} %)")
        ok_amp &= err < 2.0

    saturated = b_iron_mean > SAT_THRESHOLD
    print(f"iron saturated (> {SAT_THRESHOLD} T avg): {saturated}")
    ok = sol["converged"] and ok_amp and saturated
    print("NONLINEAR CHECK:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
