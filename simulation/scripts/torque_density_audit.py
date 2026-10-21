"""Torque-density audit (see validation/torque_density_audit/PLAN.md).

One solve of the certified anchor point (3072 / rows4, delta=26.25 deg,
M-43 Steel) plus pure post-processing:

  1. MMF harmonics of the ACTUAL d_pattern() slot ATs (staircase -> FFT).
  2. Airgap Br(theta) from the solved field at mid-gap -> FFT.
  3. Textbook sizing T = (pi/2) D^2 L * 0.5*A1*B1  (A1 = p*Fhat_p, B1 = Bhat_p).
  4. Ratio T_fem / T_sizing.

Frozen interpretation rule lives in the PLAN; this script only measures.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rajini_anchor as A  # noqa: E402  (constants + helpers; no main on import)
from fem_magnetics import load_bh_curve, solve_az_core, torque_maxwell  # noqa: E402
from synrm_geometry import SynRMGeometry  # noqa: E402
from synrm_mesh import build_mesh  # noqa: E402

DELTA_DEG = 26.25
P = 2                      # pole pairs (4-pole machine)
N_HARM = 20


def mmf_wave(pattern: dict[int, float], slot_area: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    """Staircase MMF from slot ATs, sampled on a dense angle grid.

    Slot k is centred at k*PITCH (geometry convention), AT_k concentrated at
    the slot centre (standard staircase).
    """
    n = 8192
    th = np.linspace(0.0, 2 * math.pi, n, endpoint=False)
    at = np.array([pattern[k] * A.J_CU * A.FILL * slot_area[f"slot_{k:02d}"]
                   for k in range(A.N_SLOTS)])
    cum = np.concatenate(([0.0], np.cumsum(at)))          # boundary k -> k+1
    F = np.empty(n)
    for i, t in enumerate(th):
        k = int(math.floor(t / A.PITCH)) % A.N_SLOTS
        F[i] = cum[k]
    F -= F.mean()
    return th, F


def fourier_amp(y: np.ndarray, n: int) -> float:
    """Amplitude of the n-th harmonic of a uniformly sampled periodic signal."""
    N = y.size
    k = n % N
    c = np.fft.fft(y) / N
    return float(2.0 * abs(c[k]))


def gap_field(sub: dict, sol: dict, gap: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Br(theta) at mid-gap from the solved element field, area-weighted binning."""
    cells = np.asarray(sub["airgap"], dtype=np.int64)
    cx, cy = sol["cx"][cells], sol["cy"][cells]
    r = np.hypot(cx, cy)
    th = np.mod(np.arctan2(cy, cx), 2 * math.pi)
    r_gap = float(r.mean())
    band = np.abs(r - r_gap) <= 0.30 * gap            # middle band of the 4 rows
    cells, th = cells[band], th[band]
    b_r = sol["Bx"][cells] * np.cos(th) + sol["By"][cells] * np.sin(th)
    n_bin = 1440
    bins = np.mod((th / (2 * math.pi) * n_bin).astype(int), n_bin)
    acc = np.bincount(bins, weights=b_r, minlength=n_bin)
    cnt = np.bincount(bins, minlength=n_bin)
    ok = cnt > 0
    return (np.linspace(0, 2 * math.pi, n_bin, endpoint=False)[ok],
            acc[ok] / cnt[ok], r_gap)


def main() -> int:
    g = SynRMGeometry(
        stator_od=A.STATOR_OD, stator_bore=A.BORE, n_slots=A.N_SLOTS,
        airgap=A.AIRGAP, shaft_od=A.SHAFT_OD,
        barrier_radial_span=A.BARRIER_SPAN,
        barrier_center_angle=math.pi / 4 + math.radians(DELTA_DEG),
    )
    print(f"geometry: bore={A.BORE*1000:.2f} mm  rotor_od={g.rotor_od*1000:.2f} mm  "
          f"gap={A.AIRGAP*1000:.2f} mm  delta={DELTA_DEG} deg")
    mesh, sub, _ = build_mesh(g, n_theta=3072, n_gap_rows=4)
    sg = A.split_slots(mesh, sub)
    areas = A.tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    print(f"mesh: {mesh.t.shape[1]} elements  mean slot area="
          f"{np.mean(list(slot_area.values()))*1e6:.1f} mm^2")

    H, B = load_bh_curve("M-43 Steel")
    pattern = A.d_pattern()
    loading = {k: A.J_CU * A.FILL * slot_area[f"slot_{k:02d}"] for k in range(A.N_SLOTS)}
    jz = {f"slot_{k:02d}": pattern[k] * loading[k] / slot_area[f"slot_{k:02d}"]
          for k in range(A.N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(A.N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    sol = solve_az_core(mesh, cell_sets, materials, jz)
    r_gap_solve = (g.stator_bore / 2 + g.rotor_od / 2) / 2
    t_fem = abs(torque_maxwell(sol, r_gap_solve, 1.0, n_theta=2880))
    bmax = float(np.hypot(sol["Bx"], sol["By"]).max())
    print(f"solve: converged={sol['converged']} iters={sol['newton_iters']} "
          f"Bmax={bmax:.2f} T  T_fem={t_fem:.4f} N.m/m (depth=1)")

    # --- 1. MMF spectrum -------------------------------------------------
    th, F = mmf_wave(pattern, slot_area)
    amps = {n: fourier_amp(F, n) for n in range(1, N_HARM + 1)}
    total_at = sum(pattern[k] * A.J_CU * A.FILL * slot_area[f"slot_{k:02d}"]
                   for k in range(A.N_SLOTS))
    abs_at = sum(abs(pattern[k]) * A.J_CU * A.FILL * slot_area[f"slot_{k:02d}"]
                 for k in range(A.N_SLOTS))
    print(f"\nMMF: net AT={total_at:+.1f} A (balanced -> ~0)  |AT| sum={abs_at:.1f} A")
    print("  harmonic  amplitude [A]   (order = pole pairs)")
    for n in range(1, N_HARM + 1):
        if amps[n] > 0.02 * max(amps.values()):
            print(f"  n={n:2d}      {amps[n]:8.1f}")
    dom = max(amps, key=amps.get)
    print(f"  dominant order n={dom} (pole pairs), p_machine={P} -> "
          f"{'MATCH' if dom == P else 'MISMATCH'}")

    a1 = P * amps[P] / r_gap_solve   # peak fundamental electric loading, A/m
    b_ideal = 1.25663706212e-6 * amps[P] / A.AIRGAP   # armature-only gap flux
    print(f"  Fhat_p = {amps[P]:.1f} A  ->  A1 = p*Fhat/r = {a1:.0f} A/m")
    print(f"  armature-only B = mu0*Fhat/g = {b_ideal:.3f} T")

    # --- 2. gap field ----------------------------------------------------
    th_g, br, r_gap = gap_field(sub, sol, A.AIRGAP)
    b_amps = {n: fourier_amp(br, n) for n in range(1, 13)}
    b1 = b_amps[P]
    print(f"\nGap field at r={r_gap*1000:.2f} mm: "
          f"Bmean={np.abs(br).mean():.3f} T  Bmax={np.abs(br).max():.3f} T  "
          f"Bhat_p({P})={b1:.3f} T")
    print("  gap harmonics [T]: " + "  ".join(
        f"n={n}:{b_amps[n]:.3f}" for n in (1, 2, 3, 4, 6, 8)))

    # --- 3. textbook sizing ----------------------------------------------
    d = A.BORE
    sigma = 0.5 * a1 * b1
    t_sizing = (math.pi / 2) * d**2 * sigma       # N.m per metre
    ratio = t_fem / t_sizing if t_sizing > 0 else float("nan")
    print(f"\nSizing: sigma=0.5*A1*B1 = {sigma:.0f} Pa  "
          f"T_sizing = {t_sizing:.2f} N.m/m")
    print(f"T_fem / T_sizing = {ratio:.3f}   "
          f"(T_fem={t_fem:.2f}, T_sizing={t_sizing:.2f})")
    print(f"anchor 8 N.m @74mm needs T/m = {8.0/0.074:.1f}; "
          f"scaling factor on our loading = {(8.0/0.074)/t_fem:.2f}x")

    # --- consistency checks (loud, not silent) ----------------------------
    assert sol["converged"], "solve did not converge"
    assert abs(total_at) < 0.02 * abs_at, "pattern is not balanced 3-phase"
    assert amps[P] > 0, "no p-th MMF harmonic"
    assert math.isfinite(ratio) and ratio > 0
    print("\nself-checks: converge OK, balanced pattern OK, finite ratio OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
