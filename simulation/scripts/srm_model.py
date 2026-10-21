"""SRM 12/8 vs SynRM same-envelope indicative comparison.

Gates declared BEFORE running in simulation/validation/srm_synrm_compare/PLAN.md.

Reuses the validated anchor toolchain end to end: structured polar mesh, per-slot
currents, damped-Newton nonlinear solver, multi-ring Maxwell torque. The SRM rotor
is the synrm "barrier" machinery with rotor_n_poles=8: a rotor slot IS the air
region inside the rotor iron, which is what the barrier class models.

All torques are per meter of stack (depth=1.0); omitted Planck constant: none.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas
from rajini_anchor import (AIRGAP, BARRIER_SPAN, BORE, FILL, J_CU, L_STACK,
                           N_SLOTS, SHAFT_OD, STATOR_OD, split_slots)

# --- declared SRM design (PLAN.md) -------------------------------------------
SRM_N_SLOTS = 12
SRM_POLE_TIP_MM = 12.0        # slot-opening arc at bore -> stator pole tip ~15 deg
ROTOR_SLOT_FRAC = 25.0 / 45.0  # rotor slot arc / rotor pitch (45 deg)
ROTOR_SLOT_DEPTH = 0.005
ROTOR_TIP = 0.002             # rotor "bridge" = pole tip height
TORQUE_NTHETA = 2880
N_RINGS = 9
SWEEP_DEG = [15.0, 20.0, 25.0, 30.0, 35.0, 37.5, 40.0, 45.0, 52.5, 60.0]
# unaligned at 15 deg (rotor slot under stator pole), aligned at 37.5 deg,
# and periodic: 60 deg = 15 deg + 45 deg rotor pitch (G3 checks both zeros)

MAX_ITER = 80


def synrm_reference_geometry() -> SynRMGeometry:
    return SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                         airgap=AIRGAP, shaft_od=SHAFT_OD,
                         barrier_radial_span=BARRIER_SPAN)


def srm_slot_area(depth: float, *, a_open: float, half_bot: float) -> float:
    r_bore = BORE / 2
    rs = np.linspace(r_bore, r_bore + depth, 500)
    frac = (rs - r_bore) / depth
    half = a_open + (half_bot - a_open) * frac
    return float(np.trapezoid(2 * half * rs, rs))


def srm_slot_depth() -> float:
    """Declared: total SRM stator slot area == total SynRM slot area (equal Cu)."""
    a_open = math.asin((SRM_POLE_TIP_MM * 1e-3 / 2) / (BORE / 2))
    half_bot = 0.55 * (2 * math.pi / SRM_N_SLOTS) / 2
    target = expected_areas(synrm_reference_geometry())["slots"] / SRM_N_SLOTS
    lo, hi = 2e-3, 30e-3
    for _ in range(60):
        mid = (lo + hi) / 2
        if srm_slot_area(mid, a_open=a_open, half_bot=half_bot) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


SRM_DEPTH = srm_slot_depth()


def srm_geometry(phi_rad: float) -> SynRMGeometry:
    return SynRMGeometry(
        stator_od=STATOR_OD, stator_bore=BORE, n_slots=SRM_N_SLOTS,
        slot_opening=SRM_POLE_TIP_MM * 1e-3, slot_depth=SRM_DEPTH,
        airgap=AIRGAP, shaft_od=SHAFT_OD,
        n_barriers=1, barrier_gap_frac=0.0,
        barrier_radial_span=ROTOR_SLOT_DEPTH, barrier_angle_frac=ROTOR_SLOT_FRAC,
        barrier_center_angle=phi_rad, bridge=ROTOR_TIP, rotor_n_poles=8)


def srm_pattern() -> dict[str, float]:
    """Phase A on: 4 stator poles (slots (0,1),(3,4),(6,7),(9,10)), +/- conductors."""
    jcx = J_CU * FILL
    jz = {f"slot_{k:02d}": 0.0 for k in range(SRM_N_SLOTS)}
    for base in (0, 3, 6, 9):
        jz[f"slot_{base:02d}"] = jcx
        jz[f"slot_{base + 1:02d}"] = -jcx
    return jz


def triangle_areas(mesh) -> np.ndarray:
    t, p = mesh.t, mesh.p
    return 0.5 * np.abs(
        (p[0][t[1]] - p[0][t[0]]) * (p[1][t[2]] - p[1][t[0]])
        - (p[0][t[2]] - p[0][t[0]]) * (p[1][t[1]] - p[1][t[0]]))


def solve_case(gg: SynRMGeometry, jz: dict[str, float], H, B, *, mesh_kw: dict):
    mesh, sub, _ = build_mesh(gg, **mesh_kw)
    sg = split_slots(mesh, sub, gg.n_slots)
    cells = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B),
                 **{f"slot_{k:02d}": 1.0 for k in range(gg.n_slots)}}
    sol = solve_az_core(mesh, cells, materials, jz, max_iter=MAX_ITER)
    return sol, mesh, cells


def area_report(mesh, cells: dict[str, np.ndarray],
                gg: SynRMGeometry) -> tuple[float, dict[str, float]]:
    tri = triangle_areas(mesh)
    exp = expected_areas(gg)
    errs = {n: abs(tri[c].sum() - exp[n]) / exp[n] for n, c in cells.items()
            if n in exp}
    return max(errs.values()), errs


def torque_nmm(sol, gg: SynRMGeometry) -> float:
    rg = (BORE / 2 + gg.rotor_od / 2) / 2
    half_gap = (BORE / 2 - gg.rotor_od / 2) / 2
    return torque_maxwell(sol, rg, 1.0, n_theta=TORQUE_NTHETA,
                          n_rings=N_RINGS, r_spread=0.5 * half_gap)


def sweep(steel: str, mesh_kw: dict, phases_deg=None) -> dict:
    H, B = load_bh_curve(steel)
    jz = srm_pattern()
    out = {}
    for deg in (phases_deg or SWEEP_DEG):
        gg = srm_geometry(math.radians(deg))
        sol, mesh, cells = solve_case(gg, jz, H, B, mesh_kw=mesh_kw)
        conv = bool(sol.get("converged", True))
        aerr, _ = area_report(mesh, cells, gg)
        out[deg] = {"T_pmm": torque_nmm(sol, gg), "conv": conv, "area_err": aerr}
        print(f"  {steel:10s} phi={deg:5.1f}  T={out[deg]['T_pmm']:+.4f} N.m/m"
              f"  conv={conv}  area_err={aerr:.3%}", flush=True)
    return out


def main() -> None:
    import json
    out_dir = Path(__file__).parent / "validation" / "srm_synrm_compare"
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh_kw = dict(n_theta=1536, n_gap_rows=4)
    mesh_kw_fine = dict(n_theta=3072, n_gap_rows=4)

    print("SRM slot depth (equal-Cu):", f"{SRM_DEPTH*1e3:.2f} mm", flush=True)
    area_synrm = expected_areas(synrm_reference_geometry())["slots"]
    print(f"  total slot area: synrm={area_synrm*1e6:.1f} mm^2  "
          f"srm={12*srm_slot_area(SRM_DEPTH, a_open=math.asin((SRM_POLE_TIP_MM*1e-3/2)/(BORE/2)), half_bot=0.55*(2*math.pi/SRM_N_SLOTS)/2)*1e6:.1f} mm^2", flush=True)

    results: dict = {"srm_depth_mm": SRM_DEPTH * 1e3,
                     "curve": sweep("M-43 Steel", mesh_kw)}

    peak = max((abs(v["T_pmm"]) for v in results["curve"].values()))
    aligned = results["curve"][37.5]["T_pmm"]
    unaligned = results["curve"][15.0]["T_pmm"]
    g1 = all(v["conv"] for v in results["curve"].values())
    g2 = max(v["area_err"] for v in results["curve"].values()) <= 0.01
    g3 = (abs(aligned) <= 0.2 * peak) and (abs(unaligned) <= 0.2 * peak)
    results["peak_T_pmm"] = peak

    # G4 refinement at aligned position
    fine = sweep("M-43 Steel", mesh_kw_fine, phases_deg=[37.5])
    t_fine = abs(fine[37.5]["T_pmm"])
    g4 = abs(t_fine - peak) / peak if peak else 1.0
    results["fine_T_pmm"] = fine[37.5]["T_pmm"]

    # C1 comparison (anchor numbers from the completed sweep, N.m per meter)
    synrm_T_pmm = 7.6911
    srm_T_74 = peak * L_STACK
    synrm_T_74 = synrm_T_pmm * L_STACK
    ratio = peak / synrm_T_pmm
    results["comparison"] = {
        "synrm_T_pmm": synrm_T_pmm, "srm_T_pmm_peak": peak,
        "synrm_T_74mm": synrm_T_74, "srm_T_74mm": srm_T_74,
        "ratio_srm_over_synrm": ratio,
        "synrm_active_mass_kg": active_mass_kg(L_STACK),
        "srm_T_per_active_vol_Nm_per_L": srm_T_74 / active_volume_L(L_STACK),
    }

    gates = {"G1_converged": g1, "G2_areas<=1%": g2,
             "G3_zeros<=20%peak": g3, "G4_refine<=10%": g4 <= 0.10}
    results["gates"] = gates
    results["gates_detail"] = {"aligned_T": aligned, "unaligned_T": unaligned,
                               "g4_diff": g4,
                               "overall": all(gates.values())}
    print("GATES:", gates, flush=True)
    print(f"C1: SRM peak {peak:.4f} N.m/m ({srm_T_74:.3f} N.m @74mm) vs "
          f"SynRM {synrm_T_pmm:.4f} N.m/m ({synrm_T_74:.3f} N.m) -> "
          f"ratio {ratio:+.3f} (+/-25% band per PLAN)", flush=True)
    print("OVERALL:", "PASS" if all(gates.values()) else "FAIL", flush=True)

    def _np(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        raise TypeError(repr(o))
    (out_dir / "srm_results.json").write_text(
        json.dumps(results, indent=1, default=_np))


def active_volume_L(L: float) -> float:
    r_out, r_sh = STATOR_OD / 2, SHAFT_OD / 2
    return math.pi * (r_out**2 - r_sh**2) * L * 1e3  # litres


def active_mass_kg(L: float) -> float:
    r_out, r_sh = STATOR_OD / 2, SHAFT_OD / 2
    return math.pi * (r_out**2 - r_sh**2) * L * 7650


if __name__ == "__main__":
    main()
