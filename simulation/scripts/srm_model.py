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
ROTOR_SLOT_DEPTH = 0.012   # amended from 0.005: 5mm gave negligible saliency (see PLAN)
ROTOR_TIP = 0.0             # amended from 0.002: continuous 2mm surface sleeve shunted
                            # the flux (amendment 2 in PLAN)
SWEEP_DEG = list(range(0, 95, 5))          # one 90 deg period, 5 deg steps; the
# curve is 45 deg periodic (rotor pitch; phase circuit spans 2 pitches)
TORQUE_NTHETA = 2880
N_RINGS = 9

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
    """Phase A on, classic 12/8 wiring: 4 stator poles per phase alternate N,S,N,S
    (diametrically opposite poles reversed) so the phase flux closes pole -> rotor
    -> opposite pole. Poles at 15+90p deg; slots (3p, 3p+1); +currents for N."""
    jcx = J_CU * FILL
    jz = {f"slot_{k:02d}": 0.0 for k in range(SRM_N_SLOTS)}
    for p, base in enumerate((0, 3, 6, 9)):
        s = +1 if p % 2 == 0 else -1          # N,S,N,S
        jz[f"slot_{base:02d}"] = s * jcx
        jz[f"slot_{base + 1:02d}"] = -s * jcx
    return jz


def phase_linkage(sol, mesh, cells, pat: dict[str, float]) -> float:
    """Phase flux linkage [Wb/m] = sum over energized slots of j * A_bar * a."""
    A_el = np.asarray(sol["A"])[mesh.t].mean(axis=0)
    tri = triangle_areas(mesh)
    return float(sum(pat[f"slot_{k:02d}"] * A_el[cells[f"slot_{k:02d}"]].mean()
                     * tri[cells[f"slot_{k:02d}"]].sum()
                     for k in range(SRM_N_SLOTS)
                     if cells[f"slot_{k:02d}"].size and pat[f"slot_{k:02d}"]))


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


def main() -> None:
    """Empirical protocol (PLAN amendments 2-3): coarse 0..90/5 lambda+T curve,
    aligned/unaligned = measured lambda extrema, gates against those, fine mesh
    at the peak and both lambda-plateau centres."""
    import json
    out_dir = Path(__file__).parent / "validation" / "srm_synrm_compare"
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh_kw = dict(n_theta=1536, n_gap_rows=4)
    mesh_kw_fine = dict(n_theta=3072, n_gap_rows=4)

    print("SRM slot depth (equal-Cu):", f"{SRM_DEPTH*1e3:.2f} mm", flush=True)
    H, B = load_bh_curve("M-43 Steel")
    jz = srm_pattern()

    # coarse curve over one 90 deg period
    curve = {}
    for deg in SWEEP_DEG:
        gg = srm_geometry(math.radians(deg))
        sol, mesh, cells = solve_case(gg, jz, H, B, mesh_kw=mesh_kw)
        curve[deg] = {"T_pmm": torque_nmm(sol, gg), "conv": bool(sol["converged"]),
                      "area_err": area_report(mesh, cells, gg)[0],
                      "lam": phase_linkage(sol, mesh, cells, jz)}
        c = curve[deg]
        print(f"  phi={deg:5.1f} lam={c['lam']:+.5f} T={c['T_pmm']:+.4f}"
              f" conv={c['conv']} area={c['area_err']:.3%}", flush=True)

    lams = np.array([curve[d]["lam"] for d in SWEEP_DEG])
    span = lams.max() - lams.min()
    # lambda plateau = consecutive grid points within 5% of span of the extremum
    def plateau(i: int) -> float:
        lo = hi = i
        while lo > 0 and abs(lams[lo - 1] - lams[i]) <= 0.05 * span:
            lo -= 1
        while hi < len(SWEEP_DEG) - 1 and abs(lams[hi + 1] - lams[i]) <= 0.05 * span:
            hi += 1
        return (SWEEP_DEG[lo] + SWEEP_DEG[hi]) / 2
    phi_aligned = plateau(int(np.argmax(lams)))
    phi_unaligned = plateau(int(np.argmin(lams)))
    peak_phi = max(curve, key=lambda d: abs(curve[d]["T_pmm"]))
    peak = abs(curve[peak_phi]["T_pmm"])
    print(f"aligned={phi_aligned} T={curve[phi_aligned]['T_pmm']:+.4f}"
          f" unaligned={phi_unaligned} peak@{peak_phi}={peak:+.4f}", flush=True)

    fine = {}
    for deg in (peak_phi, phi_aligned, phi_unaligned):
        gg = srm_geometry(math.radians(deg))
        sol, mesh, cells = solve_case(gg, jz, H, B, mesh_kw=mesh_kw_fine)
        fine[deg] = {"T_pmm": torque_nmm(sol, gg), "conv": bool(sol["converged"]),
                     "area_err": area_report(mesh, cells, gg)[0]}
        print(f"  fine phi={deg:5.1f} T={fine[deg]['T_pmm']:+.4f}", flush=True)

    peak_fine = abs(fine[peak_phi]["T_pmm"])
    g1 = all(v["conv"] for v in list(curve.values()) + list(fine.values()))
    g2 = max(v["area_err"] for v in list(curve.values()) + list(fine.values())) <= 0.01
    g3 = (abs(fine[phi_aligned]["T_pmm"]) <= 0.2 * peak_fine
          and abs(fine[phi_unaligned]["T_pmm"]) <= 0.2 * peak_fine)
    g4 = abs(peak_fine - peak) / peak <= 0.10
    gates = {"G1_converged": g1, "G2_areas<=1%": g2,
             "G3_zeros<=20%peak": g3, "G4_refine<=10%": g4}

    synrm_T_pmm = 8.1235   # corrected anchor MTPA (2026-10-21 wrap-fix run)
    ratio = peak_fine / synrm_T_pmm
    c1 = {
        "synrm_T_pmm": synrm_T_pmm, "srm_T_pmm_peak_fine": peak_fine,
        "synrm_T_74mm": synrm_T_pmm * L_STACK, "srm_T_74mm_fine": peak_fine * L_STACK,
        "ratio_srm_over_synrm": ratio,
        "synrm_T_per_active_vol_Nm_per_L": synrm_T_pmm * L_STACK / active_volume_L(L_STACK),
        "srm_T_per_active_vol_Nm_per_L": peak_fine * L_STACK / active_volume_L(L_STACK),
    }
    results = {"srm_depth_mm": SRM_DEPTH * 1e3, "curve": curve,
               "peak_T_pmm_coarse": peak, "peak_phi": peak_phi,
               "phi_aligned": phi_aligned, "phi_unaligned": phi_unaligned,
               "fine": fine, "gates": gates, "comparison": c1}
    print("GATES:", gates, flush=True)
    print(f"C1: SRM peak {peak_fine:.3f} N.m/m ({peak_fine*L_STACK:.3f} N.m @74mm) vs "
          f"SynRM {synrm_T_pmm:.4f} ({synrm_T_pmm*L_STACK:.3f} N.m) -> ratio {ratio:+.3f}"
          " (+/-25% band per PLAN)", flush=True)
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


if __name__ == "__main__":
    main()
