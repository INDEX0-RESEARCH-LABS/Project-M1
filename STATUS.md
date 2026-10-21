# Current state - single source of truth

**As of commit `f519498` (2026-10-21).** Everything here is reproduced by the scripts named
in section 6. Where a number moved during the campaign, the latest value is here and the
superseded one is marked in `DECISIONS.md`; **quote from this file, not from old RESULT
sections.**

Labels: **SOLVED** = from a converged field solution; **DERIVED** = algebra on solved
quantities; **ESTIMATE** = model with a stated band; **ASSUMED** = input not yet verified.

## 1. Where the project is

Zero-budget (D-009) design study of a magnet-free 48 V traction motor for the Indian 2W
market. Gate A-C are complete; the baseline is a 4-pole, 36-slot synchronous reluctance
machine. The point design is **130 mm bore / 50.4 mm stack**, and the remaining blocker is
not torque but **current at 48 V (102 A) and power factor (0.53-0.58)** - or, equivalently,
the choice of winding turns / pack voltage.

## 2. The design, in numbers

| quantity | value | label | source |
|---|---|---|---|
| frame | 130 mm bore, 50.4 mm stack, 188 mm OD, 4 poles, 36 slots | - | `envelope_point_design/RESULT.md` |
| winding | single layer, 6 coils/phase, 5 turns/coil at a=4 | SOLVED | `prototype/design/winding_spec_v1.md` |
| torque at J=5.34 A/mm2 | **1.592 N.m** (target 1.6) | SOLVED | `dq_model/RESULT.md` |
| torque at J=6.0 | 2.022 N.m | SOLVED | same |
| torque per stack length | 38.5 N.m/m (rows 4/20/40: 38.50/37.86/39.67) | SOLVED | `envelope_point_design/RESULT.md` |
| torque-density utilization | 0.43 of the anchor-class expectation | DERIVED | `torque_density_audit` |
| copper loss (hot, enclosed) | **25.6 W** at the target, 32.6 W at J=6 | DERIVED | `dq_model/RESULT.md` s.9 |
| iron loss (100 Hz elec.) | 8.4-23.4 W, median **13.5 W** | ESTIMATE | `iron_loss/RESULT.md` |
| winding rise | **~10 K** copper only, **~15 K** with iron (enclosed) | ESTIMATE | same |
| efficiency | **92.7% (91.1-93.7%)**, copper-only 95.1% | ESTIMATE | same |
| phase current | **102 A** peak at the design winding | SOLVED | `dq_model/RESULT.md` s.9 |
| terminal voltage | 6.4 V peak against a 26.3 V ceiling | DERIVED | same |
| PF / apparent power | **0.53-0.58** / ~0.99 kVA | ESTIMATE | same |
| active mass | 8.9 kg iron + 0.82 kg copper | DERIVED | `iron_loss`, `dq_model` |
| specific power | ~56 W/kg of active iron | DERIVED | - |

The machine is **thermally comfortable and electrically current-limited**. It is also
oversized: 8.9 kg of iron for 0.5 kW is what buys the 92.7%.

## 3. What is actually open

| item | status | what unblocks it |
|---|---|---|
| **Winding turns / max speed** | OPEN - blocks the winding drawing | application max motor speed or gear ratio (founder input). k=2 (51 A, ~6,100 rpm) is the recommendation for a 2W drivetrain |
| **PF 0.53-0.58 / 102 A at 48 V** | OPEN - founder call (D-012) | accept ~1 kVA controller at 100 A, or change winding (k=2/3, same kVA) or pack voltage (96 V) |
| Rotor slot-harmonic loss (~1800 Hz) | NOT MODELLED | a time-domain eddy solve; order-of-magnitude bound says 1-4 W (see `iron_loss/RESULT.md` s.5) |
| 33% flux-linkage vs torque gap | OPEN, interpretation-limited | rotating-field solve; does not change the torque or the envelope |
| D-004 (5% replication) | CANCELLED under D-009 | founder sign-off, paperwork only |
| BOM, insulation/megohm, dyno-class tests | BLOCKED | F-class spend, founder approval |
| Double-layer winding (if wanted for manufacture) | NOT CERTIFIED | would need the slot-AT pattern re-solved; torque is not invariant |

## 4. The three corrections that matter (audit trail)

All three were **factor-2 errors on copper loss**, each found by a route cross-check, each
halving the number. This is why absolute loss figures are only quoted through this file.

| addendum | error | effect |
|---|---|---|
| 6 | mechanical vs electrical speed; peak vs RMS current density | PF from impossible (>1) to 0.55; loss halved |
| 6 | (same) | - |
| 9 | mean turn length applied to a **half-turn** copper volume | P_cu 53 -> 25.6 W, efficiency 88 -> 92.7% |

Addendum 9 also caught that the old thermal-vs-winding cross-check agreed because both
copies carried the same error. The three routes are now tied by
`tests/test_copper_loss_routes.py`.

## 5. Gates

- Gate A: research certified, one grade-substitution correction recorded.
- Gate B: rotor stress PASS at 0.6 mm bridges (M-43 bracket, INDICATIVE +/-25%).
- Gate C: C1-C3 PASS (torque, mesh/sensitivity, co-energy within 10%); **C4/C5 FAIL**
  (torque density and PF targets not met by this family) - D-011, honest failure.
- Iron loss F1-F4: PASS as declared (`iron_loss/PLAN.md`, `RESULT.md`).
- Tests: **25 passed** (`.venv/bin/python -m pytest -q`).

## 6. Reproduce

    cd /home/darion-dev/project-m1
    .venv/bin/python -u simulation/scripts/dq_model.py       # ~12 min, 9 solves
    .venv/bin/python -u simulation/scripts/dq_model.py --pf-check   # ~40 s, PF bracket
    .venv/bin/python -u simulation/scripts/thermal_first_order.py   # seconds
    .venv/bin/python -u simulation/scripts/iron_loss.py      # ~3 min, 2 solves
    .venv/bin/python -m pytest -q

Logs from the current runs: `/tmp/opencode/m1/{dq_fix,dq_pfcheck_fix,thermal_fix,iron_loss_fix}.log`.
