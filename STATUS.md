# Current state - single source of truth

**As of D-018 (2026-10-23): PF and the torque *shape* are certified; mean torque is the open number.**
The D-015 half-slot fix changed the machine, so D-014's numbers were re-derived on the
corrected winding with a 181-point 0.25 deg sweep and a four-mesh ladder. Torque is now
measured with the gap area integral, because a solid-rotor null test showed the
single-circle extractor the old chain used reads +0.55 N.m on a machine that must give
zero. Re-certified: torque 1.77 +- 0.14 N.m at 26.0 deg, efficiency 93.2% **at that peak
angle only - 90.6% on a mean basis (D-020, D-021)**, iron 16.3 W.
PF is re-certified **like-for-like** at 3072/10 (D-017): S6 **0.578 / 1.059 kVA** against
the baseline rotor **0.469 / 1.111 kVA** at the same angle and current, so S6 clears the
+0.030 PF gate by +0.109 with 18.3% more torque at 4.7% less apparent power. The baseline
PF is lower than the 0.532 previously quoted because that number was measured on the
uncorrected winding at 26.25 deg with a ring torque. **Torque ripple is now ESTABLISHED
(D-018): ~100% peak-to-peak in-model, gate R3 FAILS, locked to the 30 deg winding repeat
unit.** The certified 1.873 N.m is an instantaneous peak-angle value: the measured
running mean at J=5.21 is **1.2305 N.m**, so the 1.6 N.m target now needs about J=6.77 on a
mean basis (~40 W copper, ~89.9% efficiency, ~1.38 kVA - planning estimates, not
certified). The ripple is **order 36, i.e. slot-locked**, not winding-locked, and skew of
two slot pitches brings it inside the 15% gate in-model (D-019). See section 4 and
`validation/torque_ripple/RESULT.md`. **Superseded values are kept below and marked.**
**Originally as of D-014 (2026-10-22).** Everything here is
reproduced by the scripts named
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

**D-014 ADOPTED, and its PF justification now holds on a like-for-like basis (D-017): the
deep-barrier rotor beats the shallow baseline on torque, efficiency *and* power factor
when both are measured the same way.** The barrier stack used
to occupy only the outer 10.4 mm of a 64.5 mm rotor radius, so q-flux dived under it. At
44.5 mm depth (4 barriers, 25% ribs, 0.62 angular fraction) the machine at the 1.6 N.m
target needs **J 5.21 / 49.7 A**, gives **PF 0.578, S 1.06 kVA, 93.2% peak-angle efficiency / 90.6% mean-basis** (D-016, D-020
numbers; D-014's 0.633 / 0.86 kVA were on the uncorrected winding), and
carries **17% less iron** with a **~6,840 rpm** voltage ceiling. Gate B (plane-stress FE,
SF 12.2 at 7000 rpm) and iron loss (12.1 W median) both pass. The open risks are torque
ripple/NVH and tooling, not electromagnetics.

## 2. The design, in numbers

| quantity | value | label | source |
|---|---|---|---|
| frame | 130 mm bore, 50.4 mm stack, 188 mm OD, 4 poles, 36 slots | - | `envelope_point_design/RESULT.md` |
| winding (decided, D-013) | single layer, 6 coils/phase, **10 turns/coil at a=4**, 2 x 1.2 mm per turn | SOLVED + scaling | `prototype/design/winding_spec_v1.md` |
| torque at J=5.34 A/mm2 (**instantaneous**, 26.0 deg) | **1.873 N.m** annulus, 6.6% band spread (D-016, 3072/10); 1.77 +- 0.14 at J=5.21. D-014 had 1.685. This is one rotor position, not the running value | SOLVED, band | `torque_curve/RESULT.md` s.9 |
| **mean torque over a revolution** (J=5.21, current angle 26.0) | **1.2305 N.m** annulus at **0.5 deg** sampling (rings 1/5/9: 1.544/1.402/1.275), min 0.4268 (12.5 deg) / max 1.7461 (25.5 deg), p-p **107.2%**. **This is the sizing number.** A 2 deg grid biases it 3.2% low by quadrature across the notches (1.1918) - D-021 | SOLVED, band | `torque_ripple/RESULT.md` s.9 |
| torque at J=6.0 | 1.920 N.m (baseline rotor, ring-averaged 3072/10); S6 not measured at J=6 | SOLVED | `torque_extractor/RESULT.md` |
| torque per stack length | 38.5 N.m/m (rows 4/20/40: 38.50/37.86/39.67), ratio-based, shares the -9% extractor bias | SOLVED | `envelope_point_design/RESULT.md` |
| torque-density utilization | 0.43 of the anchor-class expectation | DERIVED | `torque_density_audit` |
| current for the 1.6 N.m target | **J = 5.21 A/mm2, 49.7 A peak** at k=2 (D-014; baseline needed 53.7 A) - **on an instantaneous basis**. On a *mean* basis the estimate is J = 6.77 / ~64.6 A peak, ~40 W copper, to be re-certified (D-019, D-021) | SOLVED (instantaneous) / DERIVED (mean, planning) | `saliency_lever/RESULT.md` s.5, `torque_ripple/RESULT.md` s.9 |
| copper loss (hot, enclosed) | **23-24.5 W** at the 1.6 N.m target (D-014; baseline 26-28 W) | DERIVED | `thermal_first_order`, `saliency_lever` s.5 |
| iron loss (100 Hz elec.) | 10.1-27.4 W, median **16.3 W** (D-016; D-014 had 12.1 W - the corrected winding saturates the rotor to 2.83 T) | ESTIMATE | `iron_loss --candidate` |
| winding rise | **~14 K** with iron (9.2 K copper only) at the 1.6 N.m target; enclosed, h=25 | ESTIMATE | `thermal_first_order` |
| efficiency | **90.6% mean-basis** (D-020, D-021), 93.2% at the peak angle only (D-016; D-014 had 93.4%). The 3 pp gap is the same peak-vs-mean error as the torque | ESTIMATE | `iron_loss --candidate` |
| **response to the mean-torque deficit** | **stack length 50.4 -> 65.5 mm at J=5.21** (D-020, D-021): torque is exactly proportional to L in-model, so this holds copper density (0.471 W/mm), kVA (1.06) and efficiency (90.6%) fixed and pays with speed ceiling (~6840 -> ~5260 rpm). The current route (J=6.77) costs 1.38 kVA and 89.9% | DERIVED (2D exact in L) | `DECISIONS.md` D-020 |
| phase current | **49.7 A** peak for the target at k=2 (D-014; 99.4 A at the k=1 FEM state, N_c = 1.247) | SOLVED | `saliency_lever` s.5 |
| terminal voltage | **11.5 V** peak at 3000 rpm against a 26.3 V ceiling (D-014) | DERIVED | `saliency_lever` s.5 |
| PF / apparent power | **0.578 / 1.059 kVA** (D-017, S6) against **0.469 / 1.111 kVA** (baseline), both at 26.0 deg, J=5.34, 3072/10, annulus. Gate +0.030 -> **+0.109 PASS** | SOLVED / DERIVED | `saliency_screen --confirm` |
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
| **Deep-barrier rotor (D-014)** | **ADOPTED; torque, efficiency and PF RE-CERTIFIED (D-016, D-017)**: 1.873 N.m at J=5.34 (annulus), 1.77 +- 0.14 at J=5.21, 93.2% peak-angle / 90.6% mean (D-020), iron 16.3 W, **PF 0.578 vs baseline 0.469**; Gate B SF 12.2 at 7000 rpm stands (independent of the winding fix). Ripple is **stator-side and skew-fixable (D-019)**, so it no longer sets the envelope; **mean torque does (D-020)** | punching tooling once the frame (stack length) is chosen. Rotor choice D-014 holds on a mean basis (+12..21% at equal current) |
| **PF at 48 V** | **CLOSED (D-017)**: like-for-like at 3072/10, S6 **0.578 / 1.059 kVA** vs baseline **0.469 / 1.111 kVA** at 26.0 deg, J=5.34. S6 wins by +0.109 PF and 18.3% torque at 4.7% *less* kVA. The kVA problem belongs to the frame and the current, not to S6 | D-012's choice is now a controller question: ~1.06 kVA at 48 V (65-88 A class) for either rotor |
| **Torque extractor convergence** | ABSORBED - 1.45 N.m +/-4% **at the certified point only**. `torque_at` returns `abs()` (no sign structure); angle-resolved torque below **~0.5 N.m is not resolvable** (four gap bands spread 10.7% at the certified point, 9x at a dip). New `fem_magnetics.torque_annulus` area-integral estimator gives 1.536 vs 1.576 N.m at the certified point with a per-band error bar (2026-10-23) | one fully converged certification point (4096/20, rings 9 + co-energy + annulus) would restore a point value; ~15 min compute. Low-torque work needs a stress method that does not depend on element-constant B (local jacobian or co-energy) |
| **Slot binning convention** | **FIXED (D-015)**: `split_slots` was half a slot off the geometry's k*pitch convention (+0.513 pitch measured), rotating the MMF 5 deg mech and mixing phases at belt boundaries; T(0)/T(45) read 0.44/0.46 N.m instead of 0.01/0.03 | regression test in `tests/test_rajini_winding.py`; nothing else to do |
| True MTPA angle | **MAPPED at 0.25 deg (D-016)**: argmax 26.0 deg, plateau 25.5-27.5 within 1.5%. The curve has converged dips at 12.5 / 22.5 / 33.0 / 41.75 deg (14-29% of peak) and a negative lobe at 1.5-3.9 deg | resolved enough for the operating point. The dips are mirror-symmetric about 22.5 deg (4.0<->41.6, 12.5<->33.0) and *irregularly* spaced (8.5/10.0/10.5/8.6 deg), so no single order explains them; origin unconfirmed but they respect the geometry's symmetry |
| **Running torque ripple** | **ESTABLISHED in-model (D-018), mechanism identified (D-019)**: p-p **107.2% annulus** unskewed, over an exact 30 deg period at 0.5 deg sampling; fine-mesh extrema reproduce p-p within 0.5 pp. Period exactly 30 deg (12 pairs, 0.0000 N.m). Harmonic fit: **order 36 = 0.457 N.m is 2.8x order 12 = 0.161**, so the ripple is **slot-locked**, not winding-locked | **R3 FAIL unskewed**; see the skew row |
| **Ripple mechanism is stator-side** | **the baseline 2-barrier rotor shows the same dips at the same angles** (12.0, 22.0 deg), same order-12 amplitude to 0.2%, order 36 within 6%, at its own rated current. The barriers barely modulate it, so this is not an S6 defect | closed; the lever is the stator slot/skew, not the barrier shape |
| **Skew lever** | **in-model, from the measured curve (multi-slice 2D, no new solves)**: 1 slot pitch (10 deg) 107.2% -> 23.1%; **2 slot pitches (20 deg) -> 12.9%, PASSES the 15% R3 gate**; 30 deg (one winding repeat) -> **2.7%**; 15 deg is *worse* (25.9%) because it is 1.5 pitches. Mean unchanged in-model; real cost ~2% via the skew factor 0.980 at 40 deg elec | needs a skewed-rotor solve for a certified number, and a lamination-stacking/tooling decision |
| D-014 advantage on a **mean** basis | **+12% to +21%** at equal current (bracket over T ~ J^1..J^2), against +18.3% instantaneous. both means taken on the same 2 deg grid, so the grid bias largely cancels; on that grid S6's relative ripple is shallower (96.6% vs 106.7%) | bracket tightens with a torque-vs-J solve at 5.21; no change to the decision |
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
