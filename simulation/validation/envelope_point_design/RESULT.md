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

**Values below are post-correction (D-012 addendum 6).** The original table used the FEM
peak slot current density as RMS and was 2x high on copper loss.

| J (peak) | P_cu (enclosed, hot) | winding rise | note |
|---|---|---|---|
| 6.0 (2.0 N.m margin point) | 68 W | 26 K | viable enclosed |
| **5.34 (1.6 N.m target)** | **53 W** | **20 K** | comfortable |
| 3.0 | 16 W | 6 K | large margin |

Still air (h=10) at J=6 is 75 W / 55 K: marginal but not the 131 K previously reported.
Enclosed (h=25) and forced air (h=50, 14 K) are comfortable. At the exact target torque
the machine runs ~53 W copper, ~20 K rise, **~90% copper-only efficiency**. Hotspot is
higher than this lumped number, and iron loss is excluded (efficiency is an upper bound).

**Correction history:** addendum 5 moved the target from J=4.8 to J=5.34 (`T ~ J^2`).
Addendum 6 fixed the peak-vs-RMS copper-loss error. Net effect versus the original table:
the target point went from 97 W / 37 K / 84% to **53 W / 20 K / ~90%**.

## 4. System-level number (recorded because it drives inverter cost)

**PUBLISHED (D-012 addendum 6) - model-independent, from measured flux linkage + torque:**

| point | i phase | Vhat | S | PF |
|---|---|---|---|---|
| 1.6 N.m (J=5.34) | 102 A | 6.5 V | ~1.0 kVA | 0.55 |
| 2.0 N.m (J=6) | 115 A | 7.3 V | 1.25 kVA | 0.56 |

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
  36 slots, ~5 turns/coil at a=4. Delivers 1.6 N.m at J=5.34 with ~20 K rise.
- **Efficiency is not the gap** (~90% copper-only, iron loss still to be added); **PF 0.55
  and the ~100 A phase current at the 48 V design winding** are the product-level
  constraints. A ~1.2 kVA controller covers it; the ~3x turns increase is the lever that
  drops current to ~35 A at identical copper loss.
- Remaining zero-budget work: iron loss from the same field solution (no new physics),
  then a spec decision on whether PF 0.55 / ~100 A is acceptable for the 2W product or
  whether the winding (turns) or pack voltage (96 V) should change.
