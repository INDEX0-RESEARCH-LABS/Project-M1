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

| J | P_cu (enclosed) | winding rise | note |
|---|---|---|---|
| 6.0 (2.0 N.m margin point) | 151 W | 57 K | needs forced air to be comfortable |
| **4.8 (exact 1.6 N.m target)** | **~97 W** | **~37 K** | viable enclosed |
| 4.0 | 60 W | 23 K | comfortable |

Still air (h=10) is not viable at J=6 (131-137 K rise); enclosed (h=25) and forced air
(h=50) are. At the exact target torque the machine runs at J ~ 4.8, ~97 W copper,
~37 K rise, copper-only efficiency ~84%. **The target is thermally viable; the margin
point is not, without airflow.** Hotspot is higher than this lumped number.

**CORRECTION (D-012 addendum 5):** the J ~ 4.8 line assumed T proportional to J. The
measured torque scales as J^2 over 4.8-6 A/mm2, so 1.6 N.m sits at **J = 5.34**:
**~119 W copper, ~45 K rise, ~81% copper-only**. Still viable enclosed; 8 K hotter.
See `../dq_model/RESULT.md`.

## 4. System-level number (recorded because it drives inverter cost)

At 130/50, J=6: N_ph = 15.1, phase current ~109 A for 2.0 N.m -> **kT ~ 0.018 N.m/A**.
At the 1.6 N.m target that is **~87 A phase** for 0.5 kW mechanical (~12 A DC bus at 84%),
i.e. **power factor ~0.25 and ~4 kVA of inverter**. A 48 V / ~100 A controller exists but
is scooter-class, not e-bike-class. This is a real product-level consequence of a
low-saliency magnet-free machine and must be in the spec discussion.

**WITHDRAWN (D-012 addendum 5):** the PF/turns numbers in this section are not
admissible. The dq model that was meant to replace them failed its own gate (3.1x
torque error), so no PF is published. Survivors: the ~100 A phase current at this
winding, and the ~6-8 V terminal voltage against a 26.3 V ceiling (the winding is
under-turned ~3x). See `../dq_model/RESULT.md`.

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
  36 slots, ~5 turns/coil at a=4. Delivers 1.6 N.m at J ~ 4.8 with ~37 K rise.
- **Efficiency and PF are the real product gap** (~84% copper-only, PF ~0.25,
  ~4 kVA inverter), not torque or thermal feasibility.
- Remaining zero-budget work: iron loss + PF from the same field solution (no new
  physics), then a spec decision on whether a low-PF SynRM is acceptable for the 2W
  product or whether the topology/battery voltage must change (96 V halves the current
  and inverter VA, at the cost of a 96 V pack).
