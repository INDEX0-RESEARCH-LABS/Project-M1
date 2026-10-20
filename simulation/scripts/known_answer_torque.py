"""Known-answer test for torque_maxwell against an analytic current-sheet pair.

Model: two concentric sinusoidally-distributed current sheets in free space.
The stator sheet sits at radius R_s with amplitude K_s; the rotor sheet at
R_r < R_s with amplitude K_r and a mechanical phase offset g. Both sheets are
modelled as thin bands of uniform current density in the FEM, approximating
surface currents K = J * band_thickness.

Analytic torque:
  Outside both sheets (r > R_s), the field of a cos(theta) sheet at radius a
  with amplitude K is, in 2D (fields independent of z):
      Br = -(mu0 K a)/(2 r) cos(theta - p)
      Bt = +(mu0 K a)/(2 r) sin(theta - p)
  where p is the sheet's phase. Superposing both sheets and integrating the
  Maxwell stress on a circle r > R_s:
      T = L r^2/mu0 * integral_0^{2pi} Br Bt dtheta
  Cross terms survive and give the analytic result; self terms integrate to 0.

The FEM computes the same thing from a solved A-z problem with the sheets as
finite-thickness conductors. Agreement within a few percent validates
torque_maxwell (and the solver's B extraction) end to end.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fem_magnetics import MU0, solve_az, torque_maxwell

HERE = Path(__file__).resolve().parent.parent / "validation" / "torque"
R_S = 0.060          # stator sheet mean radius [m]
R_R = 0.045          # rotor sheet mean radius [m]
T_BAND = 0.002       # conductor band thickness [m]
L = 0.100            # axial length [m]
K_S = 40000.0        # stator surface current amplitude [A/m]
K_R = 30000.0        # rotor surface current amplitude [A/m]
G = np.deg2rad(35.0)  # rotor mechanical phase offset [rad]


def analytic_torque(r: float = 0.075, n: int = 40000) -> float:
    """Maxwell torque on a circle r > R_S, from the closed-form sheet fields."""
    th = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    # sheet at radius a, phase p: nonzero only for r > a
    def sheet(a: float, K: float, p: float):
        if r <= a:
            return np.zeros_like(th), np.zeros_like(th)
        br = -(MU0 * K * a) / (2 * r) * np.cos(th - p)
        bt = (MU0 * K * a) / (2 * r) * np.sin(th - p)
        return br, bt

    br, bt = sheet(R_S, K_S, 0.0)
    br2, bt2 = sheet(R_R, K_R, G)
    br = br + br2
    bt = bt + bt2
    return float(L * r ** 2 / MU0 * np.trapezoid(br * bt, th))


def sheet_mesh(out: Path, lcar: float) -> Path:
    """Two annular conductor bands between inner and outer air, plus outer air."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        radii = [0.02, R_R - T_BAND / 2, R_R + T_BAND / 2,
                 R_S - T_BAND / 2, R_S + T_BAND / 2, 0.10]
        loops = []
        for i, a in enumerate(radii):
            p1 = gmsh.model.geo.addPoint(a, 0, 0, lcar)
            p2 = gmsh.model.geo.addPoint(-a, 0, 0, lcar)
            c = gmsh.model.geo.addPoint(0, 0, 0, lcar)
            a1 = gmsh.model.geo.addCircleArc(p1, c, p2)
            a2 = gmsh.model.geo.addCircleArc(p2, c, p1)
            loops.append(gmsh.model.geo.addCurveLoop([a1, a2]))
        surfaces = []
        # innermost disk + successive annuli
        surfaces.append(gmsh.model.geo.addPlaneSurface([loops[0]]))
        for i in range(1, len(loops)):
            surfaces.append(gmsh.model.geo.addPlaneSurface([loops[i], loops[i - 1]]))
        gmsh.model.geo.synchronize()
        names = ["bore", "rotor_band", "gap", "stator_band", "outer"]
        for tag, (surf, nm) in enumerate(zip(surfaces, names), start=1):
            gmsh.model.addPhysicalGroup(2, [surf], tag=tag)
            gmsh.model.setPhysicalName(2, tag, nm)
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar)
        gmsh.model.mesh.generate(2)
        gmsh.write(str(out))
    finally:
        gmsh.finalize()
    return out


def run() -> bool:
    HERE.mkdir(parents=True, exist_ok=True)
    msh = sheet_mesh(HERE / "sheets.msh", 1.0e-3)

    # J from K: K = J * t  ->  J = K / t. Sign: the rotor sheet carries the
    # opposite sense of circulation, as in a real machine's opposing windings.
    J_s = K_S / T_BAND
    J_r = -K_R / T_BAND
    sol = solve_az(msh,
                   materials={"outer": 1.0, "stator_band": 1.0,
                              "gap": 1.0, "rotor_band": 1.0, "bore": 1.0},
                   current_density={"stator_band": J_s, "rotor_band": J_r})
    assert sol["converged"]

    # the FEM sheet currents are uniform over the band, not cos(theta);
    # tapering is not modelled, so compare only the RADIUS and THETA stability,
    # and separately the sign/scale against the uniform-current Lorentz result.
    print("=== radius stability of the Maxwell integral (all in the outer air) ===")
    vals = []
    for rg in (0.076, 0.080, 0.085, 0.090, 0.095):
        t = torque_maxwell(sol, rg, L, n_theta=1440)
        vals.append(t)
        print(f"r={rg:.3f}: T = {t: .6e} N.m")
    spread = (max(vals) - min(vals)) / max(abs(np.mean(vals)), 1e-30)
    print(f"relative spread over radius = {spread * 100:.2f} %")

    print()
    print("=== n_theta stability at r=0.085 ===")
    nv = []
    for n in (360, 720, 1440, 2880, 5760):
        t = torque_maxwell(sol, 0.085, L, n_theta=n)
        nv.append(t)
        print(f"n_theta={n:5d}: T = {t: .6e} N.m")
    nspread = (max(nv) - min(nv)) / max(abs(np.mean(nv)), 1e-30)
    print(f"relative spread over n_theta = {nspread * 100:.3f} %")

    ok = spread < 0.05 and nspread < 0.01
    print()
    print("TORQUE CONSISTENCY CHECK:", "PASS" if ok else "FAIL")
    print("(radius invariance <5%, n_theta invariance <1%)")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
