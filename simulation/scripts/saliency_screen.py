"""Saliency screen: does rotor barrier geometry buy power factor?

Gates declared in validation/saliency_lever/PLAN.md before this ran.
Same solver and extractor as dq_model.py; only the barrier parameters change.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dq_model as D          # noqa: E402
import rajini_anchor as A     # noqa: E402
from envelope_validation import build  # noqa: E402
from fem_magnetics import load_bh_curve, torque_annulus  # noqa: E402

J = 5.34e6
CONFIGS = (
    ("BASE", dict(n_barriers=3, barrier_angle_frac=0.62, barrier_gap_frac=0.40)),
    ("V1", dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25)),
    ("V2", dict(n_barriers=5, barrier_angle_frac=0.62, barrier_gap_frac=0.25)),
    ("V3", dict(n_barriers=4, barrier_angle_frac=0.75, barrier_gap_frac=0.25)),
    ("V4", dict(n_barriers=3, barrier_angle_frac=0.75, barrier_gap_frac=0.20)),
)

# Second probe: the barrier stack is only 10.4 mm deep on a 64.5 mm rotor radius, so
# q-flux can dive under it. These variants push the stack toward the shaft (which is
# magnetic: shaft radius 16.9 mm), the standard multi-barrier SynRM construction.
CONFIGS_SPAN = (
    ("BASE", dict(n_barriers=3, barrier_angle_frac=0.62, barrier_gap_frac=0.40)),
    ("S1", dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
                barrier_span=0.0208)),
    ("S2", dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
                barrier_span=0.0312)),
    ("S3", dict(n_barriers=5, barrier_angle_frac=0.62, barrier_gap_frac=0.30,
                barrier_span=0.0260)),
    ("S4", dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
                barrier_span=0.0455)),
)

# S4 violates the declared 2 mm yoke/shaft margin (zone_in 18.38 mm vs shaft radius
# 16.9 mm). S6 is the same design pulled back to pass sanity_checks: zone_in 19.28 mm.
CONFIGS_CAND = (
    ("S6", dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
                barrier_span=0.0445)),
)


def run_config(name: str, kw: dict, H, B) -> dict:
    n_c1 = D.turns(D.BORE, D.L_STACK, 1)
    out = {}
    for d, tag in ((45.0, "d"), (0.0, "q"), (D.DELTA_OP, "op")):
        r = D.solve_point(d, J, H, B, geom=build(d, D.BORE, **kw))
        i = J * A.FILL * r["a_slot"] / n_c1
        r["i"] = i
        r["L"] = r["lam_per_turn"] * n_c1 / i
        out[tag] = r
    op = out["op"]
    i = op["i"]
    # D-016: torque and PF from the converged gap area integral, not the
    # single circle (which carries a +0.55 N.m solid-rotor bias).
    t_nm = op["T_ann"] * D.L_STACK
    lam_par = op["lam_alpha"] * n_c1
    lam_perp = op["T_ann"] * D.L_STACK / (1.5 * D.P_POLES * i)
    r_ph = D.RHO * 6 * n_c1**2 * D.MTL / (A.FILL * op["a_slot"])
    w_m = 2 * math.pi * (D.RPM / 60)
    w_e = w_m * D.P_POLES
    vhat = math.hypot(r_ph * i + w_e * lam_perp, w_e * lam_par)
    p_cu = 1.5 * r_ph * i * i
    pf = (p_cu + t_nm * w_m) / (1.5 * vhat * i)
    return {"name": name, "xi": out["d"]["L"] / out["q"]["L"],
            "Ld": out["d"]["L"], "Lq": out["q"]["L"], "T": t_nm, "i": i,
            "PF": pf, "S": 1.5 * vhat * i, "Bmax": op["Bmax"], "kw": kw}


BASE_KW = dict(n_barriers=3, barrier_angle_frac=0.62, barrier_gap_frac=0.40)
S6_KW = dict(n_barriers=4, barrier_angle_frac=0.62, barrier_gap_frac=0.25,
             barrier_span=0.0445)


def certify(name: str, kw: dict, H, B, jj: float) -> dict:
    """One operating point at the ruled mesh: annulus torque and power-balance PF.

    D-016 ruled that absolute torque comes from the gap area integral, so PF here
    is the annulus PF. Nothing is compared to a stored constant: BASE and the
    candidate are solved by the same code at the same mesh and angle, so the
    difference is like-for-like.
    """
    from torque_mesh_convergence import solve_raw, torque_at

    g = build(D.DELTA_OP, D.BORE, **kw)
    res = solve_raw(D.DELTA_OP, jj, H, B, 3072, 10, geom=g)
    t = [torque_at(res, r) for r in (1, 5, 9)]
    n_c1 = D.turns(D.BORE, D.L_STACK, 1)
    i = jj * A.FILL * res["a_slot"] / n_c1
    bands = torque_annulus(res["sol"], g.rotor_od / 2 + 1e-6,
                           g.stator_bore / 2 - 1e-6, 1.0, n_bands=4) * D.L_STACK
    t_ann = float(bands.mean())
    band = (bands.max() - bands.min()) / abs(t_ann)
    lam_perp = t_ann / (1.5 * D.P_POLES * i)
    lam_par = res["lam_alpha"] * n_c1
    r_ph = D.RHO * 6 * n_c1**2 * D.MTL / (A.FILL * res["a_slot"])
    w_m = 2 * math.pi * (D.RPM / 60)
    w_e = w_m * D.P_POLES
    vhat = math.hypot(r_ph * i + w_e * lam_perp, w_e * lam_par)
    p_cu = 1.5 * r_ph * i * i
    pf = (p_cu + t_ann * w_m) / (1.5 * vhat * i)
    out = dict(name=name, T=t_ann, T_ring=t, band=band, PF=pf,
               S=1.5 * vhat * i, i=i, vhat=vhat, p_cu=p_cu, lam_par=lam_par)
    print(f"  {name:4s} T_ann={t_ann:.3f} N.m  (rings 1/5/9 "
          f"{t[0]:.3f}/{t[1]:.3f}/{t[2]:.3f})  band {band:.1%}  PF={pf:.3f}  "
          f"S={out['S']:.0f} VA  i={i:.1f} A  Vhat={vhat:.2f} V")
    return out


def confirm_deep(H, B, j_mm2=None) -> int:
    """Like-for-like certification of the deep-barrier candidate against BASE.

    Gate G-PF1 (declared before the run): D-014's adoption criterion was
    PF >= BASE + 0.030 absolute. Both rotors are solved at delta=DELTA_OP on the
    ruled mesh (3072/10) with the annulus estimator, so no stored torque constant
    enters the comparison.
    """
    jj = J if j_mm2 is None else j_mm2 * 1e6
    print(f"\ncertification: 3072/10, delta={D.DELTA_OP} deg, J={jj/1e6:.2f} A/mm2")
    b = certify("BASE", BASE_KW, H, B, jj)
    s = certify("S6", S6_KW, H, B, jj)
    d_pf = s["PF"] - b["PF"]
    print(f"\nG-PF1: PF {s['PF']:.3f} - {b['PF']:.3f} = {d_pf:+.3f} "
          f"{'PASS' if d_pf >= 0.03 else 'FAIL'} (gate >= +0.030)")
    print(f"  torque {s['T']:.3f} vs {b['T']:.3f} N.m = "
          f"{s['T']/b['T']-1:+.1%}; kVA {s['S']:.0f} vs {b['S']:.0f} VA")
    print(f"  N.m/kVA {1e3*s['T']/s['S']:.3f} vs {1e3*b['T']/b['S']:.3f}")
    return 0


def main() -> int:
    H, B = load_bh_curve("M-43 Steel")
    span_mode = "--span" in sys.argv
    configs = CONFIGS_SPAN if span_mode else CONFIGS
    if "--cand" in sys.argv:
        configs = CONFIGS_CAND
    if "--deep" in sys.argv:
        configs = (("S5", dict(n_barriers=4, barrier_angle_frac=0.68,
                               barrier_gap_frac=0.25, barrier_span=0.0455)),)
    print(f"saliency screen: J={J/1e6:.2f} A/mm2, 1536/rows4, "
          f"bore {D.BORE*1e3:.0f} mm, span {0.012*D.BORE/0.150*1e3:.1f} mm"
          f"{' (span probe)' if span_mode else ''}")
    print("id    nb  frac  rib    span    xi     Ld[mH]  Lq[mH]  T[N.m]   i[A]   "
          "PF     S[VA]  Bmax[T]")
    res = {}
    for name, kw in configs:
        r = run_config(name, kw, H, B)
        res[name] = r
        span_mm = kw.get("barrier_span", 0.012 * D.BORE / 0.150) * 1e3
        print(f"{name:5s} {kw['n_barriers']:3d} {kw['barrier_angle_frac']:5.2f} "
              f"{kw['barrier_gap_frac']:5.2f} {span_mm:6.1f} {r['xi']:6.2f} "
              f"{r['Ld']*1e3:7.4f} {r['Lq']*1e3:7.4f} {r['T']:7.3f} {r['i']:6.1f} "
              f"{r['PF']:6.3f} {r['S']:6.0f} {r['Bmax']:7.2f}")

    b = res.get("BASE")
    if b is not None:
        print(f"\nS1 regression: xi={b['xi']:.2f} ({b['xi']/1.85-1:+.1%} vs 1.85), "
              f"T={b['T']:.3f} N.m ({b['T']/1.592-1:+.1%} vs 1.592), "
              f"PF={b['PF']:.3f}")
        assert abs(b["xi"] / 1.85 - 1) <= 0.05, "harness does not reproduce baseline xi"
        assert abs(b["T"] / 1.592 - 1) <= 0.02, "harness does not reproduce baseline T"
    else:
        print("\n(no BASE in this run: comparisons use the BASE row from the "
              "same extractor, 1536/rows4)")
        b = {"xi": 1.85, "T": 1.592, "PF": 0.532}

    print("\nS3 candidates (xi>=2.5, T>=0.95xBASE, PF>=BASE+0.03):")
    cands = []
    for name, r in res.items():
        if name == "BASE":
            continue
        ok = (r["xi"] >= 2.5 and r["T"] >= 0.95 * b["T"]
              and r["PF"] >= b["PF"] + 0.03)
        print(f"  {name}: xi {r['xi']:.2f} ({r['xi']/b['xi']-1:+.0%}), "
              f"T {r['T']/b['T']-1:+.1%}, PF {r['PF']-b['PF']:+.3f}  "
              f"{'CANDIDATE' if ok else 'no'}")
        if ok:
            cands.append(r)
    if cands:
        best = max(cands, key=lambda r: r["PF"])
        print(f"\nS3 PASS: {best['name']} is a candidate; it needs a ring-averaged "
              f"certification solve before any absolute claim (S4).")
    else:
        print("\nS3 FAIL: no configuration clears all three. This barrier family is "
              "exhausted for PF as well as torque -> geometry is not the lever "
              "inside this topology.")
    return 0


if __name__ == "__main__":
    _H, _B = load_bh_curve("M-43 Steel")
    if any(a == "--target" or a.startswith("--target=") for a in sys.argv):
        jt = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--target=")),
                        5.21))
        raise SystemExit(confirm_deep(_H, _B, j_mm2=jt))
    if "--confirm" in sys.argv:
        raise SystemExit(confirm_deep(_H, _B))
    raise SystemExit(main())
