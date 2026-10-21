# Winding spec v1 - 130/50 point design

**Supersedes `winding_spec_v0.md` for the chosen frame.** v0 described the committed
159/92 anchor envelope and concluded the target torque did not fit; the 130/50 point
design (D-012 addendum 4) does. Numbers below are from the certified field solutions, the
corrected copper-loss route (addendum 9) and the PF bracket (addendum 7 + 9).
Status: topology **DECIDED for the model**; turns count **OPEN - needs one application
input** (maximum motor speed / gear ratio).

## 1. Topology (what the FEM actually models)

- 4 poles, 36 slots, q = 3, 60-degree phase belts, **single layer**: one coil side per
  slot, 12 slots per phase, **6 coils per phase** in series, full pitch (span 9 slots).
- `N_ph = 6 * N_c` (effective series turns), not 12. The slot-AT pattern used in every
  certified torque run is the single-layer pattern (`rajini_anchor.d_pattern()`), and the
  copper-loss identity in `tests/test_copper_loss_routes.py` uses the same count.
- **Correction to v0:** v0 declared a double-layer build (12 coils/phase). That is *not*
  what was solved. A double-layer build has two phases per slot, a different slot-AT
  pattern, and therefore different torque and different copper volume. If a double-layer
  build is wanted for manufacturing reasons, the torque must be re-certified - it is not a
  free implementation detail.

## 2. Electrical state at the target (J = 5.34 A/mm2 peak, 1.592 N.m)

| quantity | value | label |
|---|---|---|
| slot AT | 127 A-turn/slot | solved |
| effective series turns N_c | 1.247 (a=4, 5 physical turns/coil) | solved |
| phase current | 102.1 A peak | solved |
| current density | 5.34 A/mm2 peak, 3.78 rms | solved |
| copper volume / mass | 91.9 cm3 / 0.82 kg | derived |
| copper loss (hot, enclosed) | 25.6 W | derived |
| terminal voltage | 6.4 V peak (26.3 V ceiling) | derived |
| PF | 0.53-0.58 (bracket) | ESTIMATE |
| apparent power | 0.99 kVA | ESTIMATE |
| efficiency with iron | 92.7% (91.1-93.7%) | ESTIMATE |

## 3. Turns trade at constant slot AT (same torque, same copper loss)

Scaling the series turns by `k` at fixed copper fill keeps the slot AT and the torque
unchanged, scales current as `1/k`, terminal voltage as `k`, and leaves **kVA invariant**
(the resistive drop scales with k exactly like the back-EMF does).

| k | physical turns/coil (a=4) | phase current | Vhat @ 3000 rpm | max speed, no field weakening | wire area / example |
|---|---|---|---|---|---|
| 1 | 5 | 102 A | 6.4 V | ~12,300 rpm | 4.58 mm2 (4 x 1.2 mm) |
| **2** | **10** | **51 A** | **12.9 V** | **~6,100 rpm** | **2.29 mm2 (2 x 1.2 mm)** |
| 3 | 15 | 34 A | 19.3 V | ~4,100 rpm | 1.53 mm2 (1 x 1.4 mm) |

Max speed = 3000 rpm x 26.33 V / Vhat(3000). Field weakening would extend it, but a SynRM
with this saliency is not a good field-weakening machine, so treat these as real ceilings.

## 4. Decision rule

The turns count is set by the application's maximum motor speed, not by preference:

    k <= 26.33 V / (6.44 V * v_max_rpm / 3000)

- Top speed <= ~4,000 rpm at the motor: k = 3, 34 A - cheapest controller and cabling.
- Top speed ~5,000-6,000 rpm: **k = 2, 51 A** - the balance point for a 2W with a 5-6:1
  reduction (a 10-inch wheel at 45-60 km/h lands here).
- Top speed > 6,000 rpm (direct drive or tall gearing): k = 1, 102 A - current becomes the
  cost driver in the controller and harness.

kVA is ~1.0 kVA in every column, so the inverter's silicon is not what the turns choice
buys - it is the current rating and the speed range.

## 5. What is still open

1. **Maximum speed / gear ratio** (application input). Everything in section 3 is exact
   given that number; without it, k = 2 is the recommendation for a 2W drivetrain.
2. **Rotor slot-harmonic loss** (1800 Hz) is not in the efficiency figure; it is the one
   open loss term (order +/-5 W on 13.5 W of iron loss).
3. End-winding length is estimated as 0.6 * tau_p per end. A real coil would be measured on
   the first prototype; it changes copper loss linearly (the end is ~55% of the turn length
   at this short stack), so it is the largest single geometric uncertainty in P_cu.
4. **Slot fill 0.40 is the optimistic end of what this slot can take.** The modelled slot is
   a trapezoid with a **3.0 mm semi-closed mouth** widening to 55% of the 11.35 mm pitch at
   the bottom, 11.7 mm deep (54-57 mm2). Consequences:
   - a 5-turn coil cannot be pre-formed and dropped in; it needs **needle winding** (or an
     open/segmented slot). A 4 x 1.2 mm bundle is 2.4 mm across before insulation, so it
     passes the 3 mm mouth with little clearance;
   - the narrow mouth means the slot-average fill will be lower than a rectangular slot's.
     At fill 0.36 instead of 0.40, copper loss rises ~11% at the same AT (P_cu ~ 1/fill):
     25.6 -> ~28 W, efficiency 92.7 -> ~92.2%. Torque is unchanged.
   This is the largest remaining *manufacturing* uncertainty in the electrical numbers and
   it resolves on the first wound stator, not in simulation.
