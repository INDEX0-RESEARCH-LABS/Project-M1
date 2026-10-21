# RESULT — envelope point design (110-140 mm bore) + thermal/bridge checks

**Scripts:** `envelope_point_design.py`, `thermal_first_order.py`, `bridge_sweep.py`
(logs in `/tmp/opencode/m1/`). Declared expectations in `PLAN.md`.
**Basis:** 150 mm frame result (`../envelope_validation/RESULT.md`).

## 1. Bore screen (1536/rows4, delta 26.25, self-similar geometry)

| bore | T/m | stack for 2.0 N.m | stack for 1.6 N.m |
|---|---|---|---|
| 100 mm | 12.19 | 164 mm | 131 mm |
| 110 mm | 17.93 | 112 mm | 89 mm |
| 120 mm | 29.70 | 67 mm | 54 mm |
| 130 mm | 40.12 | 50 mm | 40 mm |
| 140 mm | 57.14 | 35 mm | 28 mm |

The 100/110 mm bores need stacks >74 mm -> rejected. **120 and 130 mm certified.**

## 2. Certification (3072 rays, rows 4/20/40, delta 26.25)

| frame | rows 4 / 20 / 40 [N.m/m] | drift | @ target stack | verdict |
|---|---|---|---|---|
| 120 mm, L 74 mm | 26.15 / 25.56 / **26.92** | +2.9% | **1.99 N.m** (1.24x) | P2 PASS |
| 130 mm, L 50.4 mm | 38.50 / 37.86 / **39.67** | +3.0% | **2.00 N.m** (1.25x) | P2 PASS |

Both meet the 25% margin gate. Bmax 2.74 / 2.83 T (still above the BH bracket - same
caveat as the 150 mm frame; torque insensitive to the bracket, 3% spread measured there).

Windability (48 V / 3000 rpm, N_c = a*N_ph/n_coils): 120/74 -> a=4: 3.7 turns;
130/50 -> a=4: **5.0 turns**, a=6: 7.5. Both buildable.

**Choice:** 130 mm bore / 50 mm stack for minimum volume (731 cm3 vs 915 cm3 stator
annulus), 188 mm OD, L/D 0.39. The 120/74 option is the one to take if the packaging
constraint is OD (174 mm) rather than axial length.

## 3. Thermal / efficiency at the chosen frame (130/50, first-order lumped)

**Values below are post-correction (D-012 addendum 9).** Two factor-2 copper errors were
found in sequence: peak-vs-RMS (addendum 6) and mean-turn-length vs half-turn volume
(addendum 9). The copper loss is 4x lower than the first published table.

| J (peak) | P_cu (enclosed, hot) | winding rise | note |
|---|---|---|---|
| 6.0 (2.0 N.m margin point) | 32.6 W | 12.3 K | viable enclosed |
| **5.34 (1.6 N.m target)** | **25.6 W** | **9.7 K** | comfortable |
| 3.0 | 7.9 W | 3.0 K | large margin |

Still air (h=10) at J=6 is 34.1 W / 25 K: fine. Enclosed (h=25) and forced air (h=50,
7 K) are comfortable. At the exact target torque the machine runs ~26 W copper, ~10 K
rise. Hotspot is higher than this lumped number.

**Iron loss (D-012 addendum 8, `../iron_loss/RESULT.md`):** first-order estimate from the
grade guarantee, 100 Hz electrical: **8.4-23.4 W, median 13.5 W** (stator 8.4 W, rotor 5.0 W
upper bound). With iron charged to the winding the target is ~39 W, **~15 K**, and
**efficiency 92.7% (91.1-93.7%)** including iron; copper-only 95.1%.

**Correction history:** addendum 5 moved the target from J=4.8 to J=5.34 (`T ~ J^2`);
addendum 6 fixed peak-vs-RMS; addendum 9 fixed the half-turn volume and the matching
`R_ph`. Net effect: the target went from 97 W / 37 K / 84% to **26 W / 10 K / 95%**
copper-only (92.7% with iron).

## 4. System-level number (recorded because it drives inverter cost)

**PUBLISHED (D-012 addendum 9) - model-independent, from measured flux linkage + torque:**

| point | i phase | Vhat | S | PF |
|---|---|---|---|---|
| 1.6 N.m (J=5.34) | 102 A | 5.9-6.4 V | 0.91-0.99 kVA | 0.53-0.58 |
| 2.0 N.m (J=6) | 115 A | 7.2 V | 1.24 kVA | 0.54-0.58 |

Bracket = two flux routes that disagree by 33% in the perpendicular component (torque vs
alpha-beta linkages); see `../dq_model/RESULT.md` s.8. The torque route is the lower bound
and the one consistent with the certified torque.

kT ~ 0.016 N.m/A at this winding. **The inverter is a ~1.2 kVA, ~100 A class part**, not
4 kVA. Voltage is far from the 26.3 V ceiling, so the winding is under-turned ~3x: at a=4
(~15 turns/coil) the phase current falls to ~35 A for identical copper loss. That, not
the VA, is the cost driver. Full derivation and caveats: `../dq_model/RESULT.md` s.7.

**WITHDRAWN:** the earlier `PF ~0.25 / ~4 kVA` figure (a VA upper bound) and the
`kN.m/A` + 84% combination. The intermediate `PF not published` state (addendum 5) is
also superseded - the dq *model* failed, but PF does not need it.


## 5. Bridge thickness is not the lever (falsified)

Sweep at 130 mm, delta 26.25, 1536/rows4:

| bridge | T/m | Bmax |
|---|---|---|
| 0.3 mm | 40.23 | 2.96 T |
| 0.4 mm | 40.25 | 2.90 T |
| 0.6 mm | 40.12 | 2.80 T |
| 1.0 mm | 39.52 | 2.64 T |

**Flat to 2%.** The 0.6 mm surface bridge is not what clamps the torque; thinning it buys
nothing (and weakens the rotor - the stress check covers 0.6 mm only). Combined with the
Gate C family sweep (arc/slot/barrier variations all capped at the same level), the
conclusion is: **this concentric-barrier SynRM family is intrinsically low-density; no
single geometric knob fixes it.** Changing that is a topology research task, not a sizing
task.

## 6. Consequences for D-012

- **Envelope: 130 mm bore / 50 mm stack** (or 120/74 if OD is the constraint), 4-pole,
  36 slots, ~5 turns/coil at a=4. Delivers 1.6 N.m at J=5.34 with ~15 K rise (iron included).
- **Efficiency 92.7% including iron** (91.1-93.7% band; copper-only 95.1%), bought with size:
  8.9 kg of active iron = 56 W/kg. **PF 0.53-0.58 and the ~100 A phase current at the 48 V
  design winding** are the product-level constraints. A ~1 kVA controller covers it.
- The turns lever is a *speed* trade, not a free win: at constant copper loss, doubling the
  series turns halves the current (51 A) and halves the no-field-weakening speed headroom
  (~6,100 rpm instead of ~12,250). Low-turns is right for a wide speed range; 2x turns is
  right only if the application tops out near 5,000-6,000 rpm.
- Remaining zero-budget work: rotor slot-harmonic loss (the one open efficiency term), and
  the turns/speed decision once the application's maximum speed is fixed.
