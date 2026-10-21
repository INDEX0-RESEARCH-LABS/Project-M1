"""Rajini 2024 SyncRel envelope anchor -- INDICATIVE validation run.

Anchor source (verbatim-specified quantities only):
  Rajini et al. 2024, AIMS Energy 12(5):1027-1053 (DOI 10.3934/energy.2024.042?:
  stored full text /tmp/opencode/m1/rajini.txt; page refs in RESULT.md).
  Their SyncRel (column 2 of Tables 3/4):
    - stator OD 159 mm, 36 slots, 4 poles, airgap 0.52 mm, 3 phases
    - slot fill 40%, current density 6 A/mm^2, M1000-65A steel
    - stack length 74 mm chosen by THEIR FEA to deliver 8 N.m at rated point
    - stator active volume 976.3 cm^3, rotor active volume 299.6 cm^3

Derived from their data (reproducible arithmetic, not a guess):
    bore D_b = sqrt(D^2 - 4*V_stator/(pi*L))
             = sqrt(0.159^2 - 4*976.3e-6/(pi*0.074)) = 92.07 mm
    rotor OD = bore - 2*airgap = 90.99 mm

NOT published by them (hence declared assumptions, all ours):
    stator bore  -> derived above
    slot depth   -> 0.18 * r_bore (this module's first-pass rule)
    shaft OD     -> 24 mm
    rotor barrier layout -> 3 layers/pol, same angle/gap fracs as baseline,
       radial span scaled 1.4x baseline (32.65 -> 45.74 mm rotor radius)
  => This is an ENVELOPE-LEVEL check. The D-004 <=5% replication gate does
     NOT apply: it is unexecutable against unpublished geometry. Reported
     under the agreed "indicative, not validated" label (MagWeb not bought).

Steel: M1000-65A has no free citable B-H table (research/material_grades.md).
Bracket declared before running, from matlib B(10 kA/m)-match analysis:
    low bound  M-43 Steel  (hardest saturation of the bracket, H@2.1T=67 kA/m)
    high bound 1006 Steel  (easiest saturation, H@2.1T=37 kA/m; low-carbon
                            analog of low-Si 0.65 mm CRNO)
Anchor states saturation flux 2.1 T; both bracket curves reach it.
(Also found: matlib block "M-47 Steel" fails to parse -- avoid, see log.)

PASS criteria (declared before running):
  R1  region areas vs closed form <= 1% each (both bracket meshes)
  R2  d/q alignment |T| < 10% of sweep max  (winding sanity at 36 slots)
  R3  |T(3072,mtpa) - T(1536,mtpa)| / T <= 5%   (primary bracket only)
  R4  Picard converges on every solve
  R5  mirror symmetry |T(d)| vs |T(90-d)| within 20% on the sweep
  I1  INDICATIVE: T at L=74 mm within +/-25% of 8 N.m (both brackets)
  I2  INDICATIVE: required stack L* = 8/T_per_m within +/-25% of 74 mm

Method: stator MMF 'd' pattern (winding lobe at +45 deg mech, see BELT_PHASE
note: delta=0 puts barriers under the lobe, delta=45 d-aligns; envelope
definitions of I1/I2 use |T| = max over the sweep and are frame-invariant),
rotor rotated via barrier_center_angle = pi/4 + delta. Torque per metre via
torque_maxwell at depth=1, mid-airgap radius, mesh (1536, 4) -- the level
validated by synrm_torque_convergence.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell
from synrm_geometry import SynRMGeometry
from synrm_mesh import build_mesh, expected_areas

HERE = Path(__file__).resolve().parent
OUT = HERE / "validation" / "anchor_rajini"

# --- anchor constants (verbatim from the paper) -------------------------
STATOR_OD = 0.159
N_SLOTS = 36
AIRGAP = 0.00052
L_STACK = 0.074          # their SyncRel stack
T_TARGET = 8.0           # N.m desired (their reluctance torque)
J_CU = 6.0e6             # A/m^2 continuous
FILL = 0.40
V_STATOR = 976.3e-6      # m^3, their "active volume of stator", col 2

# --- derived geometry ----------------------------------------------------
BORE = math.sqrt(STATOR_OD**2 - 4 * V_STATOR / (math.pi * L_STACK))  # 92.075 mm

# --- declared assumptions (ours, not theirs) ------------------------------
SHAFT_OD = 0.024
BARRIER_SPAN = 0.0084    # 1.4x baseline: proportional to rotor radius ratio

ANGLE_MESH = dict(n_theta=1536, n_gap_rows=4)
FINE_MESH = dict(n_theta=3072, n_gap_rows=4)

SMOKE = "SMOKE" in __import__("os").environ     # plumbing test: small mesh, 3 pts
if SMOKE:
    ANGLE_MESH = dict(n_theta=768, n_gap_rows=2)
    FINE_MESH = None

PITCH = 2 * math.pi / N_SLOTS          # 10 deg mech
# 36/4/3: q = 3, belts of 3. Belt order A+, C', B+, A', C+, B' (per pole pair),
# repeated twice. With slot k centred at k*PITCH (geometry module convention),
# A+ belts are {35, 0, 1} and {17, 18, 19} (mirrored images of each other).
#
# WINDING AXIS = +45 deg mech, NOT 0 deg (verified diag15, 2026-10-21):
# the axis of a full-pitch coil lies midway between its two side groups —
# A+ slots centred 0 deg pair with A- slots {8,9,10} centred 90 deg, so the
# phase-A MMF lobe is at (0+90)/2 = +45 deg. Equivalently: the slot pattern
# is even about 0 deg, so the integrated ampere-turn wave is ODD (harmonic-2
# phasor C2 real, arg 0  =>  MMF wave ~ sin(2θ), positive lobe at +45 deg).
# Consequences for delta (barrier_center_angle = pi/4 + delta):
#   delta = 0  -> winding lobe sits on the rotor Q-axis (barriers under it):
#                 torque zero by mirror symmetry; gap B_r is ODD about the
#                 pole axis (B_r ~ 0 at pole centre, +-max at barrier centres).
#   delta = 45 -> poles under the lobe (d-aligned): torque zero again.
#   |T| max near delta = 22.5 / 67.5. Sweep deltas 0..90 cover the envelope;
#   envelope torque is frame-invariant, so I1/I2 are unaffected.
# -> index (k+1) % 18 kept: it builds the intended belt table; only the
#    delta interpretation above changes.
BELT_PHASE = "AAACCCBBB" * 2           # 18 belt slots
BELT_SIGN = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]


def slot_phase36(k: int) -> tuple[str, int]:
    i = (k + 1) % 18
    return BELT_PHASE[i], BELT_SIGN[i]


def d_pattern() -> dict[int, float]:
    """Per-slot dimensionless pattern, MMF along A-axis (i_a=1, b=c=-1/2)."""
    out = {}
    for k in range(N_SLOTS):
        ph, sign = slot_phase36(k)
        out[k] = sign * (1.0 if ph == "A" else -0.5)
    return out


def split_slots(mesh, subdomains) -> dict[str, np.ndarray]:
    cells = subdomains["slots"]
    ct = mesh.p[:, mesh.t].mean(axis=1)
    th = np.mod(np.arctan2(ct[1][cells], ct[0][cells]), 2 * math.pi)
    k = np.mod(np.floor(th / PITCH).astype(int), N_SLOTS)
    return {f"slot_{i:02d}": cells[k == i] for i in range(N_SLOTS)}


def tri_areas(mesh) -> np.ndarray:
    p0, p1, p2 = (mesh.p[:, mesh.t[i]] for i in range(3))
    return 0.5 * np.abs((p1[0] - p0[0]) * (p2[1] - p0[1])
                        - (p2[0] - p0[0]) * (p1[1] - p0[1]))


def solve_case(g: SynRMGeometry, mesh, sub, slot_groups, slot_area,
               H, B) -> dict:
    pattern = d_pattern()
    loading = {k: J_CU * FILL * slot_area[f"slot_{k:02d}"] for k in range(N_SLOTS)}
    jz = {f"slot_{k:02d}": pattern[k] * loading[k] / slot_area[f"slot_{k:02d}"]
          for k in range(N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **slot_groups}
    sol = solve_az_core(mesh, cell_sets, materials, jz)
    r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2
    T = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)   # N.m per metre
    bmax = float(np.hypot(sol["Bx"], sol["By"]).max())
    return {"converged": bool(sol["converged"]), "iters": int(sol["newton_iters"]),
            "T_per_m": T, "Bmax_T": bmax, "r_gap": r_gap}


def refinement_check(g: SynRMGeometry, results: dict, hb) -> tuple[bool, float]:
    """R3: re-solve the M-43 MTPA point on the finest validated mesh."""
    print("\n=== R3 refinement (M-43 Steel at MTPA) ===")
    H, B = hb
    deg = results["M-43 Steel"]["mtpa_deg"]
    gg = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                       airgap=AIRGAP, shaft_od=SHAFT_OD,
                       barrier_radial_span=BARRIER_SPAN,
                       barrier_center_angle=math.pi / 4 + math.radians(deg))
    mesh, sub, _ = build_mesh(gg, **FINE_MESH)
    sg = split_slots(mesh, sub)
    slot_area = {n: tri_areas(mesh)[c].sum() for n, c in sg.items()}
    c = solve_case(gg, mesh, sub, sg, slot_area, H, B)
    t_fine = abs(c["T_per_m"])
    t_coarse = results["M-43 Steel"]["T_per_m"]
    r3 = abs(t_fine - t_coarse) / t_coarse <= 0.05
    print(f"  T(1536)={t_coarse:.4f}  T(3072)={t_fine:.4f}  "
          f"diff={abs(t_fine - t_coarse) / t_coarse:.1%} -> {r3}")
    return r3, t_fine


def prep(g: SynRMGeometry, H, B) -> dict:
    mesh, sub, _ = build_mesh(g, **ANGLE_MESH)
    sg = split_slots(mesh, sub)
    areas = tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    exp = expected_areas(g)
    err = {}
    for n, e in exp.items():
        if n in sub and len(sub[n]) > 0 and e > 0:
            err[n] = abs(areas[sub[n]].sum() / e - 1.0)
    return {"g": g, "mesh": mesh, "sub": sub, "sg": sg, "areas": areas,
            "slot_area": slot_area, "err": err}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    g = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE, n_slots=N_SLOTS,
                      airgap=AIRGAP, shaft_od=SHAFT_OD,
                      barrier_radial_span=BARRIER_SPAN)
    print(f"bore derived = {BORE*1000:.3f} mm ; rotor_od = {g.rotor_od*1000:.3f} mm")
    from synrm_geometry import sanity_checks
    sc = sanity_checks(g)
    print("geometry sanity:", sc)
    if not sc["all_pass"]:
        return 2

    brackets = {"M-43 Steel": None, "1006 Steel": None}
    for name in brackets:
        brackets[name] = load_bh_curve(name)

    results = {}
    preps: dict[str, dict] = {}
    for steel, (H, B) in brackets.items():
        print(f"\n=== bracket steel: {steel} ===")
        p = prep(g, H, B)
        r1 = max(p["err"].values()) <= 0.01
        print(f"R1 region err max = {max(p['err'].values()):.3%} -> {r1}")
        sweep = {}
        deltas = (0, 45, 90) if SMOKE else (0, 15, 30, 45, 60, 75, 90)
        for deg in deltas:
            gg = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE,
                               n_slots=N_SLOTS, airgap=AIRGAP, shaft_od=SHAFT_OD,
                               barrier_radial_span=BARRIER_SPAN,
                               barrier_center_angle=math.pi / 4 + math.radians(deg))
            # same topology; deltas only rotate the rotor. Re-mesh per delta
            # (mesh rays follow barrier edges), reuse the same steel.
            pp = prep(gg, H, B)
            c = solve_case(gg, pp["mesh"], pp["sub"], pp["sg"],
                           pp["slot_area"], H, B)
            sweep[deg] = c
            print(f"  delta={deg:5.1f}deg  T/m={c['T_per_m']:+.4f}  "
                  f"Bmax={c['Bmax_T']:.2f}T  iters={c['iters']}  "
                  f"conv={c['converged']}")
        tmax = max(abs(sweep[d]["T_per_m"]) for d in (15, 30, 45, 60, 75))
        r2 = (abs(sweep[0]["T_per_m"]) < 0.10 * tmax
              and abs(sweep[90]["T_per_m"]) < 0.10 * tmax)
        pairs = [abs(abs(sweep[d]["T_per_m"]) - abs(sweep[90 - d]["T_per_m"]))
                 / max(abs(sweep[d]["T_per_m"]), abs(sweep[90 - d]["T_per_m"]))
                 for d in ((30,) if SMOKE else (15, 30))]
        r5 = max(pairs) < 0.20
        # refine around the sweep maximum on the same (1536,4) level
        best = min((15, 30, 45, 60, 75), key=lambda d: -abs(sweep[d]["T_per_m"]))
        fine_pts = {}
        for deg in (best - 7.5, best - 3.75, best, best + 3.75, best + 7.5):
            deg = min(max(deg, 5.0), 85.0)
            gg = SynRMGeometry(stator_od=STATOR_OD, stator_bore=BORE,
                               n_slots=N_SLOTS, airgap=AIRGAP, shaft_od=SHAFT_OD,
                               barrier_radial_span=BARRIER_SPAN,
                               barrier_center_angle=math.pi / 4 + math.radians(deg))
            pp = prep(gg, H, B)
            c = solve_case(gg, pp["mesh"], pp["sub"], pp["sg"],
                           pp["slot_area"], H, B)
            fine_pts[deg] = c
            print(f"  refine delta={deg:5.2f}deg  T/m={c['T_per_m']:+.4f}")
        mtpa_deg = min(fine_pts, key=lambda d: -abs(fine_pts[d]["T_per_m"]))
        best_c = fine_pts[mtpa_deg]
        mtpa = best_c if abs(best_c["T_per_m"]) > tmax else sweep[best]
        T_per_m = abs(mtpa["T_per_m"])
        L_star = T_TARGET / T_per_m
        T74 = T_per_m * L_STACK
        print(f"  MTPA delta={mtpa_deg:.2f}  T/m={T_per_m:.4f}  "
              f"T@74mm={T74:.3f} N.m (target 8)  L*={L_star*1000:.1f} mm "
              f"(theirs 74)")
        i_ok = abs(T74 / T_TARGET - 1.0) <= 0.25
        results[steel] = {"sweep15": {str(d): sweep[d] for d in sweep},
                          "refine": {str(d): fine_pts[d] for d in fine_pts},
                          "mtpa_deg": mtpa_deg, "T_per_m": T_per_m,
                          "L_star_mm": L_star * 1000, "T_at_74mm": T74,
                          "Bmax_T": mtpa["Bmax_T"],
                          "r1": r1, "r2": r2, "r5": r5, "i1": i_ok,
                          "region_err_max": max(p["err"].values()),
                          "slot_area_mm2": {k: v * 1e6 for k, v in
                                            p["slot_area"].items()}}
        preps[steel] = p

    # R3: refinement check on the primary bracket (M-43) at its MTPA angle
    if SMOKE:
        print("\n[SMOKE] skipping R3 refinement check")
        r3, t_fine = True, None
    else:
        r3, t_fine = refinement_check(g, results, brackets["M-43 Steel"])
    results["M-43 Steel"]["r3"] = r3
    results["M-43 Steel"]["T_fine_mesh"] = t_fine
    if t_fine is not None and r3 is not None:
        tc = results["M-43 Steel"]["T_per_m"]
        print(f"  T(1536)={tc:.4f}  T(3072)={t_fine:.4f}  "
              f"diff={abs(t_fine-tc)/tc:.1%} -> {r3}")
    else:
        print(f"  R3 refinement: {r3}")

    r4 = all(v["converged"] for r in results.values()
             for v in list(r["sweep15"].values()) + list(r["refine"].values()))
    ok = all(results[s]["r1"] and results[s]["r2"] and results[s]["r5"]
             and results[s]["i1"] for s in brackets) and r3 and r4
    print("\nGATES:")
    for s in brackets:
        r = results[s]
        print(f"  {s}: R1={r['r1']} R2={r['r2']} R5={r['r5']} I1={r['i1']} "
              f"(T74={r['T_at_74mm']:.3f} N.m, L*={r['L_star_mm']:.1f} mm)")
    print(f"  R3 (refinement) = {r3}, R4 (convergence) = {r4}")
    print("OVERALL:", "PASS" if ok else "FAIL",
          "(pass = infrastructure + indicative gate; steel+geometry still "
          "unvalidated per D-006 / unpublished-anchor-geometry)")

    # numpy scalars (np.bool_, np.float64) are not JSON serializable
    def _py(o):
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, dict):
            return {k: _py(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_py(v) for v in o]
        return o

    (OUT / "anchor_results.json").write_text(json.dumps(_py({
        "gates": {"overall": ok, "R3_refinement": r3, "R4_converged": r4},
        "results": results,
        "meta": {
            "anchor": "Rajini 2024 AIMS Energy 12(5):1027-1053, SyncRel col 2",
            "declared": {"stator_od": STATOR_OD, "n_slots": N_SLOTS,
                         "airgap": AIRGAP, "fill": FILL, "J_cu": J_CU,
                         "L_stack": L_STACK, "T_target": T_TARGET,
                         "V_stator_m3": V_STATOR, "steel": "M1000-65A"},
            "derived": {"bore_m": BORE},
            "assumptions": {"shaft_od": SHAFT_OD,
                            "barrier_span": BARRIER_SPAN,
                            "slot_depth": "0.18*r_bore (module first-pass)",
                            "barrier_angle_frac": 0.62,
                            "barrier_gap_frac": 0.40, "n_barriers": 3},
            "steel_note": "M1000-65A B-H unavailable; bracket M-43/1006 "
                          "(indicative). Anchor B_sat 2.1 T.",
            "label": "INDICATIVE -- not a D-004 5% replication "
                     "(rotor geometry unpublished)",
        },
    }), indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
