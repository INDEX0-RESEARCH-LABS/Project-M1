# Current state - single source of truth

**As of D-014 (2026-10-22).** Everything here is reproduced by the scripts named
in section 6. Where a number moved during the campaign, the latest value is here and the
superseded one is marked in `DECISIONS.md`; **quote from this file, not from old RESULT
sections.**

Labels: **SOLVED** = from a converged field solution; **DERIVED** = algebra on solved
quantities; **ESTIMATE** = model with a stated band; **ASSUMED** = input not yet verified.

## 1. Where the project is

Zero-budget (D-009) design study of a magnet-free 48 V traction motor for the Indian 2W
market. Gate A-C are complete; the design is a 4-pole, 36-slot synchronous reluctance
machine at **130 mm bore / 50.4 mm stack**. The extractor bias found on 2026-10-21 is
absorbed (absolute torque 1.45 N.m for the shallow rotor, +/-4% band).

**D-014 ADOPTED: the deep-barrier rotor closes the PF blocker.** The barrier stack used
to occupy only the outer 10.4 mm of a 64.5 mm rotor radius, so q-flux dived under it. At
44.5 mm depth (4 barriers, 25% ribs, 0.62 angular fraction) the machine at the 1.6 N.m
target needs **J 5.21 / 49.7 A**, gives **PF 0.633, S 0.86 kVA, 93.4% efficiency**, and
carries **17% less iron** with a **~6,840 rpm** voltage ceiling. Gate B (plane-stress FE,
SF 12.2 at 7000 rpm) and iron loss (12.1 W median) both pass. The open risks are torque
ripple/NVH and tooling, not electromagnetics.

## 2. The design, in numbers

| quantity | value | label | source |
|---|---|---|---|
| frame | 130 mm bore, 50.4 mm stack, 188 mm OD, 4 poles, 36 slots | - | `envelope_point_design/RESULT.md` |
| winding (decided, D-013) | single layer, 6 coils/phase, **10 turns/coil at a=4**, 2 x 1.2 mm per turn | SOLVED + scaling | `prototype/design/winding_spec_v1.md` |
| torque at J=5.34 A/mm2 | **1.685 N.m, band 1.62-1.75** (D-014; baseline rotor was 1.45, band 1.40-1.51) | SOLVED, band | `saliency_lever/RESULT.md` s.5 |
| torque at J=6.0 | 1.920 N.m (baseline rotor, ring-averaged 3072/10); S6 not measured at J=6 | SOLVED | `torque_extractor/RESULT.md` |
| torque per stack length | 38.5 N.m/m (rows 4/20/40: 38.50/37.86/39.67), ratio-based, shares the -9% extractor bias | SOLVED | `envelope_point_design/RESULT.md` |
| torque-density utilization | 0.43 of the anchor-class expectation | DERIVED | `torque_density_audit` |
| current for the 1.6 N.m target | **J = 5.21 A/mm2, 49.7 A peak** at k=2 (D-014; baseline needed 53.7 A) | SOLVED | `saliency_lever/RESULT.md` s.5 |
| copper loss (hot, enclosed) | **23-24.5 W** at the 1.6 N.m target (D-014; baseline 26-28 W) | DERIVED | `thermal_first_order`, `saliency_lever` s.5 |
| iron loss (100 Hz elec.) | 7.5-21.2 W, median **12.1 W** (D-014; baseline 13.5 W) | ESTIMATE | `saliency_lever` s.5 |
| winding rise | **~14 K** with iron (9.2 K copper only) at the 1.6 N.m target; enclosed, h=25 | ESTIMATE | `thermal_first_order` |
| efficiency | **93.4% (91.7-94.3%)** at the 1.6 N.m target (D-014; baseline 92.3%) | ESTIMATE | `saliency_lever` s.5 |
| phase current | **49.7 A** peak for the target at k=2 (D-014; 99.4 A at the k=1 FEM state, N_c = 1.247) | SOLVED | `saliency_lever` s.5 |
| terminal voltage | **11.5 V** peak at 3000 rpm against a 26.3 V ceiling (D-014) | DERIVED | `saliency_lever` s.5 |
| PF / apparent power | **0.633 / 0.86 kVA** at the target (D-014; baseline 0.49-0.54 / 1.09 kVA) | SOLVED / DERIVED | `saliency_lever` s.5 |
| active mass | **7.37 kg iron** + 0.82 kg copper (D-014; baseline 8.9 kg iron) | DERIVED | `iron_loss --candidate` |
| slot | 36 x trapezoid, **3.0 mm semi-closed mouth**, 11.7 mm deep, fill 0.40 assumed | ASSUMED | `winding_spec_v1.md` |
| specific power | **~68 W/kg** of active iron at the target (D-014; baseline ~51) | DERIVED | - |

The machine is **thermally comfortable and electrically current-limited**. The deep
rotor removed 1.5 kg of iron without losing torque, so the design is less oversized than
it was: 7.37 kg of iron for 0.5 kW, at 93.5%.

## 3. What is actually open

| item | status | what unblocks it |
|---|---|---|
| Winding turns | **DECIDED (D-013): k=2**, ceiling **~6,840 rpm** at the 1.6 N.m target with D-014 (was ~5,860 with the shallow rotor) | reopens if the final gear ratio pushes the motor past ~6,800 rpm |
| **Deep-barrier rotor (D-014)** | **ADOPTED**: +16.2% torque at equal current, PF 0.633, S 0.86 kVA at the target; Gate B SF 12.2 at 7000 rpm; iron 12.1 W median | torque ripple/NVH and punching tooling (both outside simulation). `saliency_lever/RESULT.md`, `rotor_stress/RESULT.md` |
| **PF at 48 V** | **CLOSED by D-014**: 0.633 / 0.86 kVA at the target, no voltage, winding or frame change | D-012's founder choice shrinks to accepting 0.86 kVA or spending on a higher-current controller; nothing technical is blocking |
| **Torque extractor convergence** | ABSORBED - 1.45 N.m +/-4%, single-circle torque retired | one fully converged certification point (4096/20, rings 9 + co-energy) would restore a point value; ~15 min compute |
| True MTPA angle | NOT ESTABLISHED | a ring-averaged angle sweep with continuation between angles |
| Rotor slot-harmonic loss (~1800 Hz) | NOT MODELLED | a time-domain eddy solve; scoping bound 0.8-3.3 W (ASSUMED ripple, `iron_loss/RESULT.md` s.5) |
| Slot fill / windability | ASSUMED 0.40 | the 3.0 mm semi-closed mouth needs needle winding; at fill 0.36 the loss is +11% and efficiency ~91.8%. Resolves on the first wound stator |
| 33% flux-linkage vs torque gap | OPEN, interpretation-limited | rotating-field solve; does not change the torque or the envelope |
| 96 V vs 48 V | **CLOSED** - S is invariant under turns scaling (1e-12), 96 V buys current and speed only | no further work; see `voltage_and_angle/RESULT.md` |
| D-004 (5% replication) | CANCELLED under D-009 | founder sign-off, paperwork only |
| BOM, insulation/megohm, dyno-class tests | BLOCKED | F-class spend, founder approval |
| Double-layer winding (if wanted for manufacture) | NOT CERTIFIED | would need the slot-AT pattern re-solved; torque is not invariant |

## 4. The four corrections that matter (audit trail)

The first three were **factor-2 errors on copper loss**, each found by a route cross-check,
each halving the number. The fourth is a **measurement (extractor) bias**, not physics:
the machine did not get weaker, the measurement did. This is why absolute numbers are only
quoted through this file.

| addendum | error | effect |
|---|---|---|
| 6 | mechanical vs electrical speed; peak vs RMS current density | PF from impossible (>1) to 0.55; loss halved |
| 9 | mean turn length applied to a **half-turn** copper volume | P_cu 53 -> 25.6 W, efficiency 88 -> 92.7% |
| 10 | single Maxwell circle on a coarse mesh sampled one element | torque 1.592 -> 1.45 N.m (-9%); whole absolute set restated |

Addendum 9 also caught that the old thermal-vs-winding cross-check agreed because both
copies carried the same error. The three routes are now tied by
`tests/test_copper_loss_routes.py`. Addendum 10 is tied by
`tests/test_torque_rescope.py` and by `validation/torque_extractor/`.

## 5. Gates

- Gate A: research certified, one grade-substitution correction recorded.
- Gate B: rotor stress PASS at 0.6 mm bridges (M-43 bracket, INDICATIVE +/-25%).
- Gate C: C1-C3 PASS (torque, mesh/sensitivity, co-energy within 10%); **C4/C5 FAIL**
  (torque density and PF targets not met by this family) - D-011, honest failure.
- Iron loss F1-F4: PASS as declared (`iron_loss/PLAN.md`, `RESULT.md`).
- Torque extractor E1-E4: E1 PASS as written but **overruled** (badly designed gate, it
  compared two noisy samples); E2 FAIL at the coarse mesh -> single-circle torque retired;
  E3 arbitration 1.45 N.m (1.40-1.51); E4 FAIL on the 25% margin (+20% actual).
- Voltage/angle A1-A3 + V1-V2: A1 PASS, A2 FAIL as declared (no angle lever), A3 gain
  inside the bracket; V1/V2 PASS at 1e-12. See `voltage_and_angle/RESULT.md`.
- Tests: **32 passed** (`.venv/bin/python -m pytest -q`).

## 6. Reproduce

    cd /home/darion-dev/project-m1
    .venv/bin/python -u simulation/scripts/dq_model.py       # ~12 min, 9 solves
    .venv/bin/python -u simulation/scripts/dq_model.py --pf-check   # ~40 s, PF bracket
    .venv/bin/python -u simulation/scripts/thermal_first_order.py   # seconds
    .venv/bin/python -u simulation/scripts/iron_loss.py      # ~3 min, 2 solves
    .venv/bin/python -u simulation/scripts/pf_angle_sweep.py        # ~10 min, 10 solves
    .venv/bin/python -u simulation/scripts/pf_angle_sweep.py --angle-check
    .venv/bin/python -u simulation/scripts/torque_mesh_convergence.py  # ~12 min
    .venv/bin/python -u simulation/scripts/saliency_screen.py          # ~14 min, 5 configs
    .venv/bin/python -u simulation/scripts/saliency_screen.py --span   # ~14 min
    .venv/bin/python -u simulation/scripts/saliency_screen.py --confirm  # candidate, ~3 min
    .venv/bin/python -u simulation/scripts/saliency_screen.py --target=5.21  # certified point
    .venv/bin/python -u simulation/scripts/rotor_stress_fem.py  # Gate B FE, ~2 min
    .venv/bin/python -u simulation/scripts/iron_loss.py --candidate  # ~3 min
    .venv/bin/python -m pytest -q

Logs from the current runs: `/tmp/opencode/m1/{dq_fix,dq_pfcheck_fix,thermal_fix,iron_loss_fix,pf_angle,angle_check,torque_mesh}.log`.
