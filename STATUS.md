# Current state - single source of truth

**As of D-012 addendum 10 (2026-10-21).** Everything here is reproduced by the scripts named
in section 6. Where a number moved during the campaign, the latest value is here and the
superseded one is marked in `DECISIONS.md`; **quote from this file, not from old RESULT
sections.**

Labels: **SOLVED** = from a converged field solution; **DERIVED** = algebra on solved
quantities; **ESTIMATE** = model with a stated band; **ASSUMED** = input not yet verified.

## 1. Where the project is

Zero-budget (D-009) design study of a magnet-free 48 V traction motor for the Indian 2W
market. Gate A-C are complete; the baseline is a 4-pole, 36-slot synchronous reluctance
machine. The point design is **130 mm bore / 50.4 mm stack**. Two things now block the
founder call, and neither is torque: **PF 0.49-0.54** at the current that delivers the
1.6 N.m target (a ~1.1 kVA controller for 0.5 kW of shaft), and the **torque extractor
bias** found on 2026-10-21 (absolute torque is 1.45 N.m, not 1.592; +/-4% band). The
voltage question is closed: 96 V does not change apparent power.

**Candidate that may close the PF blocker (D-014, not yet certified):** the barrier stack
is too shallow. Deepening it from 10.4 to 44.5 mm gives +16% torque and PF 0.635 at the
same current, i.e. ~0.8 kVA at the target instead of ~1.1. It is waiting on Gate B stress
and an iron-loss re-run before it can replace the baseline.

## 2. The design, in numbers

| quantity | value | label | source |
|---|---|---|---|
| frame | 130 mm bore, 50.4 mm stack, 188 mm OD, 4 poles, 36 slots | - | `envelope_point_design/RESULT.md` |
| winding (decided, D-013) | single layer, 6 coils/phase, **10 turns/coil at a=4**, 2 x 1.2 mm per turn | SOLVED + scaling | `prototype/design/winding_spec_v1.md` |
| torque at J=5.34 A/mm2 | **1.45 N.m, band 1.40-1.51** (the 1.592 previously quoted was a single-circle coarse-mesh sample) | SOLVED, band | `torque_extractor/RESULT.md` |
| torque at J=6.0 | 1.920 N.m (ring-averaged, 3072/10); the 25% margin point is not held, margin is +20% | SOLVED | same |
| torque per stack length | 38.5 N.m/m (rows 4/20/40: 38.50/37.86/39.67), ratio-based, shares the -9% extractor bias | SOLVED | `envelope_point_design/RESULT.md` |
| torque-density utilization | 0.43 of the anchor-class expectation | DERIVED | `torque_density_audit` |
| current for the 1.6 N.m target | **J = 5.62 A/mm2, 53.7 A peak** at k=2 (at 51 A the machine gives 1.45 N.m / 454 W) | DERIVED | `torque_extractor/RESULT.md` s.3 |
| copper loss (hot, enclosed) | **26-28 W** at the 1.6 N.m target; 24-26 W at 51 A | DERIVED | `dq_model/RESULT.md` s.9 |
| iron loss (100 Hz elec.) | 8.4-23.4 W, median **13.5 W** | ESTIMATE | `iron_loss/RESULT.md` |
| winding rise | **~11 K** copper only, **~16 K** with iron (enclosed), at the 1.6 N.m target | ESTIMATE | same |
| efficiency | **92.3% (91.1-93.7%)** at the 1.6 N.m target; 92.1% if 51 A is held (454 W); copper-only ~94.8% | ESTIMATE | same |
| phase current | **53.7 A** peak for the target; 51 A gives 1.45 N.m (102 A at the FEM reference state, N_c = 1.247) | DERIVED | D-013, `torque_extractor` |
| terminal voltage | **13.5 V** peak at 3000 rpm against a 26.3 V ceiling | DERIVED | same |
| PF / apparent power | **0.49-0.54 / ~1.09 kVA** at the target; 0.53-0.58 / 0.99 kVA at 51 A | ESTIMATE | same |
| active mass | 8.9 kg iron + 0.82 kg copper | DERIVED | `iron_loss`, `dq_model` |
| slot | 36 x trapezoid, **3.0 mm semi-closed mouth**, 11.7 mm deep, fill 0.40 assumed | ASSUMED | `winding_spec_v1.md` |
| specific power | ~51 W/kg of active iron at the target (was 56 before the extractor correction) | DERIVED | - |

The machine is **thermally comfortable and electrically current-limited**. It is also
oversized: 8.9 kg of iron for 0.5 kW is what buys the 92.3%.

## 3. What is actually open

| item | status | what unblocks it |
|---|---|---|
| Winding turns | **DECIDED (D-013): k=2, 51 A**, ceiling ~5,860 rpm at the 1.6 N.m target (was ~6,130) | reopens if the final gear ratio pushes the motor past ~5,800 rpm |
| **Deep-barrier rotor (D-014)** | **CANDIDATE**: +16.2% torque, PF 0.635, S 903 VA at 102 A; ~0.76-0.80 kVA at the target | Gate B stress on 3.8 mm ribs / 0.6 mm bridge; iron-loss re-run; then certification. `saliency_lever/RESULT.md` |
| **PF 0.49-0.54 at 48 V** | OPEN - founder call (D-012) | accept ~1.1 kVA / 54 A, hold 51 A and accept 454 W, or certify the deep-barrier rotor (D-014), which screens at PF 0.635 / ~0.8 kVA |
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
    .venv/bin/python -m pytest -q

Logs from the current runs: `/tmp/opencode/m1/{dq_fix,dq_pfcheck_fix,thermal_fix,iron_loss_fix,pf_angle,angle_check,torque_mesh}.log`.
