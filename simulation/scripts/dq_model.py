"""dq model from the certified 130/50 solutions: Ld, Lq, terminal voltage, PF.

Method and gates are declared in validation/dq_model/PLAN.md before this ran.

Flux linkage comes from the slot stream function (geometric, valid with
saturation):
    lambda_A = L_stack * N_c * (sum_{A+} Abar_k - sum_{A-} Abar_k)
so L = lambda_A / i_A scales exactly as N_c^2, which is how the turns trade is
reported.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rajini_anchor as A  # noqa: E402
from envelope_point_design import turns  # noqa: E402
from envelope_validation import build  # noqa: E402
from fem_magnetics import (co_energy_density, load_bh_curve, solve_az_core,
                           torque_maxwell, MU0)  # noqa: E402
from synrm_mesh import build_mesh  # noqa: E402

BORE = 0.130
L_STACK = 0.0504
DELTA_D, DELTA_Q, DELTA_OP = 45.0, 0.0, 26.25
RPM, P_POLES = 3000.0, 2
V_CEIL = 48.0 / math.sqrt(3) * 0.95      # peak phase ceiling, same as the winding model
MTL = 2 * L_STACK + 1.2 * math.pi * BORE / 4
RHO = 1.75e-8
J_LEVELS = (4.8e6, 5.34e6, 6.0e6)   # 5.34e6 = the 1.6 N.m target (T ~ J^2)


def solve_point(delta: float, J: float, H, B, n_theta: int = 1536,
                rows: int = 4) -> dict:
    g = build(delta, BORE)
    mesh, sub, _ = build_mesh(g, n_theta=n_theta, n_gap_rows=rows)
    sg = A.split_slots(mesh, sub)
    areas = A.tri_areas(mesh)
    slot_area = {n: areas[c].sum() for n, c in sg.items()}
    pattern = A.d_pattern()
    jz = {f"slot_{k:02d}": pattern[k] * J * A.FILL for k in range(A.N_SLOTS)}
    materials = {"air": 1.0, "airgap": 1.0, "barriers": 1.0,
                 "rotor_iron": (H, B), "stator_iron": (H, B), "shaft": (H, B)}
    for k in range(A.N_SLOTS):
        materials[f"slot_{k:02d}"] = 1.0
    cell_sets = {**{n: c for n, c in sub.items() if n != "slots"}, **sg}
    sol = solve_az_core(mesh, cell_sets, materials, jz)
    if not sol["converged"]:
        raise RuntimeError(f"no convergence at delta={delta}, J={J}")
    r_gap = (g.stator_bore / 2 + g.rotor_od / 2) / 2
    T = torque_maxwell(sol, r_gap, 1.0, n_theta=2880)
    # area-weighted slot mean of A_z (element mean of the three nodal values)
    ae = sol["A"][mesh.t].mean(axis=0)
    abar = {k: float((ae[c] * areas[c]).sum() / areas[c].sum())
            for k, c in sg.items()}
    pos = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == ("A", 1)]
    neg = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == ("A", -1)]
    lam_per_turn = L_STACK * (sum(abar[f"slot_{k:02d}"] for k in pos)
                              - sum(abar[f"slot_{k:02d}"] for k in neg))
    lam_phase = {}
    for ph in ("A", "B", "C"):
        p = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == (ph, 1)]
        n = [k for k in range(A.N_SLOTS) if A.slot_phase36(k) == (ph, -1)]
        lam_phase[ph] = L_STACK * (sum(abar[f"slot_{k:02d}"] for k in p)
                                   - sum(abar[f"slot_{k:02d}"] for k in n))
    # flux linkage along the current vector (current is on the alpha/A axis):
    #   lam_alpha = (2/3)(lam_a - 0.5 lam_b - 0.5 lam_c); equals lam_a for a
    #   purely sinusoidal flux, so the difference measures the winding harmonics
    lam_alpha = (2.0 / 3.0) * (lam_phase["A"] - 0.5 * lam_phase["B"]
                               - 0.5 * lam_phase["C"])
    # co-energy of the same solution (arbiter for the torque extractor)
    bmag = np.hypot(sol["Bx"], sol["By"])
    air = np.abs(sol["nu"] - 1.0 / MU0) <= 1e-4 / MU0
    w = co_energy_density(bmag, H, B, np.where(air, 1.0, 0.0))
    Wp = float((w * areas).sum())
    return {"delta": delta, "T": abs(T), "lam_per_turn": lam_per_turn,
            "lam_alpha": lam_alpha, "lam_phase": lam_phase,
            "Wp": Wp, "a_slot": float(np.mean(list(slot_area.values()))),
            "Bmax": float(np.hypot(sol["Bx"], sol["By"]).max())}


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    n_c1 = turns(BORE, L_STACK, 1)           # turns/coil for a=1 at 48 V design
    n_ph = 12 * n_c1
    print(f"design winding: N_c(a=1)={n_c1:.3f}  N_ph={n_ph:.2f}  "
          f"MTL={MTL*1e3:.1f} mm  V_ceil={V_CEIL:.2f} V peak")

    out = {}
    for J in J_LEVELS:
        row = {}
        for d in (DELTA_Q, DELTA_OP, DELTA_D):
            r = solve_point(d, J, H, B)
            at_slot = J * A.FILL * r["a_slot"]
            i_a = at_slot / n_c1
            L = r["lam_per_turn"] * n_c1 / i_a      # N_c * lam / i, SAME as N_c^2 form
            row[d] = {**r, "at_slot": at_slot, "i": i_a, "L": L}
            print(f"  J={J/1e6:.1f} delta={d:5.2f}  T/m={r['T']:7.2f}  "
                  f"AT/slot={at_slot:6.1f}  i={i_a:6.1f} A  "
                  f"lam_turn={r['lam_per_turn']*1e3:7.3f} mWb  L={L*1e3:7.3f} mH")
        out[J] = row

    for J in J_LEVELS:
        row = out[J]
        Ld, Lq = row[DELTA_D]["L"], row[DELTA_Q]["L"]
        op = row[DELTA_OP]
        Lop = op["L"]
        beta = math.radians(45.0 - DELTA_OP)
        ihat = op["i"]
        i_d, i_q = ihat * math.cos(beta), ihat * math.sin(beta)
        t_dq = 1.5 * P_POLES * (Ld - Lq) * i_d * i_q
        r_ph = RHO * 12 * n_c1**2 * MTL / (A.FILL * op["a_slot"])
        w_m = 2 * math.pi * (RPM / 60)          # mechanical rad/s
        w_e = w_m * P_POLES                     # electrical rad/s (voltage only)
        # L-based (two-parameter) voltage: DIAGNOSTIC ONLY, this model failed D2
        v_d = r_ph * i_d - w_e * Lq * i_q
        v_q = r_ph * i_q + w_e * Ld * i_d
        vhat_lin = math.hypot(v_d, v_q)
        # Model-independent terminal voltage at the operating point:
        #   lam_par  = phase flux linkage along the current vector (slot stream sum)
        #   lam_perp = T / (1.5 p i)  from the MEASURED torque, not from Ld/Lq
        lam_par = op["lam_alpha"] * n_c1
        lam_perp = op["T"] * L_STACK / (1.5 * P_POLES * ihat)
        # frame with current along x: vx = R i - w*lam_y, vy = w*lam_x;
        # T = 1.5 p (lam_x i_y - lam_y i_x) = -1.5 p lam_y i  =>  lam_y = -lam_perp
        v_x = r_ph * ihat + w_e * lam_perp
        v_y = w_e * lam_par
        vhat = math.hypot(v_x, v_y)
        p_cu = 1.5 * r_ph * ihat**2
        p_mech = op["T"] * L_STACK * w_m        # MECHANICAL speed, not w_e
        pf = (p_cu + p_mech) / (1.5 * vhat * ihat)
        print(f"\nJ={J/1e6:.1f}: saliency Ld/Lq={Ld/Lq:.2f}  (Ld={Ld*1e3:.3f} mH, "
              f"Lq={Lq*1e3:.3f} mH, Lop={Lop*1e3:.3f} mH)")
        print(f"  T_dq={t_dq:.3f} N.m  vs T_FEM={op['T']*L_STACK:.3f} N.m  "
              f"gap={(t_dq - op['T']*L_STACK)/(op['T']*L_STACK):+.1%}  "
              f"(D2 <=25%: {'PASS' if abs(t_dq/(op['T']*L_STACK) - 1) <= 0.25 else 'FAIL'})")
        print(f"  i_d={i_d:.1f} A  i_q={i_q:.1f} A  R_ph={r_ph*1e3:.2f} mOhm  "
              f"P_cu={p_cu:.1f} W  P_mech={p_mech:.1f} W")
        print(f"  lam_par={lam_par*1e3:.2f} mWb  lam_perp={lam_perp*1e3:.2f} mWb  "
              f"|lam|={math.hypot(lam_par, lam_perp)*1e3:.2f} mWb  "
              f"(phase-A lam={op['lam_per_turn']*n_c1*1e3:.2f} mWb, "
              f"harmonic delta {(op['lam_alpha']/op['lam_per_turn']-1):+.1%})")
        print(f"  Vhat={vhat:.2f} V (ceiling {V_CEIL:.2f})  PF={pf:.3f}  "
              f"S={1.5*vhat*ihat:.0f} VA   [L-based Vhat={vhat_lin:.2f} V, "
              f"PF there {(p_cu+p_mech)/(1.5*vhat_lin*ihat):.3f} - failed model, do not quote]")
        # the energy balance is the check that caught the 2x errors: PF must be physical
        assert 0.0 < pf <= 1.0 + 1e-9, f"PF out of range: {pf:.3f}"
        k = 24.0 / vhat if vhat > 0 else float("nan")
        print(f"  turns rescale to 24 V: x{k:.2f} -> N_c={n_c1*k:.2f} "
              f"({max(1, round(n_c1*k))} turns/coil), i={ihat/k:.1f} A, "
              f"P_cu unchanged at {p_cu:.0f} W")

    # D1
    for J in J_LEVELS:
        assert out[J][DELTA_D]["L"] > out[J][DELTA_Q]["L"], "D1 failed: Ld <= Lq"
    print("\nD1 PASS: Ld > Lq at both current levels")

    # Independent torque arbiter: T = dW'/dtheta at fixed current (co-energy,
    # no Maxwell stress integral involved). J=6, +/-0.5 deg central difference.
    print("\nco-energy arbiter (J=6, 1536/rows4):")
    step = math.radians(0.5)
    ws = {}
    for d in (DELTA_OP - 0.5, DELTA_OP + 0.5):
        r = solve_point(d, 6.0e6, H, B)
        ws[d] = r["Wp"]
        print(f"  delta={d:5.2f}  W'={r['Wp']:+10.5f} J/m  Maxwell T/m={r['T']:7.3f}")
    t_co = (ws[DELTA_OP + 0.5] - ws[DELTA_OP - 0.5]) / (2 * step)
    t_mx = out[6.0e6][DELTA_OP]["T"]
    print(f"  T_coenergy={t_co:+7.3f} N.m/m  vs  T_maxwell={t_mx:7.3f} N.m/m  "
          f"gap={(abs(t_co) - t_mx)/t_mx:+.1%}")
    print("  (if the two disagree, the torque number - and every envelope result "
          "built on it - is the open question, not the dq model)")

    # D3: extraction convergence at the operating current
    print("\nD3 convergence (3072 rays / rows 10, J=4.8):")
    for d, label in ((DELTA_D, "Ld"), (DELTA_Q, "Lq")):
        fine = solve_point(d, 4.8e6, H, B, n_theta=3072, rows=10)
        at_slot = 4.8e6 * A.FILL * fine["a_slot"]
        i_a = at_slot / n_c1
        L_fine = fine["lam_per_turn"] * n_c1 / i_a
        L_coarse = out[4.8e6][d]["L"]
        drift = abs(L_fine - L_coarse) / L_coarse
        print(f"  {label}: 1536={L_coarse*1e3:.3f} mH  3072/rows10={L_fine*1e3:.3f} mH  "
              f"drift={drift:+.1%}  (<=10%: {'PASS' if drift <= 0.10 else 'FAIL'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
