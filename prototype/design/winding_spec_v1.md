# Winding spec v1 - 130/50 point design

**Supersedes `winding_spec_v0.md` for the chosen frame.** v0 described the committed
159/92 anchor envelope and concluded the target torque did not fit; the 130/50 point
design (D-012 addendum 4) does. Numbers below are from the certified field solutions, the
corrected copper-loss route (addendum 9) and the PF bracket (addendum 7 + 9).
Status: topology and **turns count DECIDED (D-013: k = 2, 10 turns/coil at a=4, 51 A)** for
an application whose motor tops out at 5,000-6,000 rpm. The FEM reference state is still
N_c = 1.247 (k = 1); the k = 2 column is exact scaling from it (see section 3).

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
| effective series turns N_c | 1.247 (a=4, 5 physical turns/coil) - FEM reference state | solved |
| phase current, reference state | 102.1 A peak | solved |
| current density | 5.34 A/mm2 peak, 3.78 rms | solved |
| copper volume / mass | 91.9 cm3 / 0.82 kg | derived |
| copper loss (hot, enclosed) | 25.6 W | derived |
| terminal voltage | 6.4 V peak (26.3 V ceiling) | derived |
| PF | 0.53-0.58 (bracket) | ESTIMATE |
| apparent power | 0.99 kVA | ESTIMATE |
| efficiency with iron | 92.7% (91.1-93.7%) | ESTIMATE |

## 3. Turns trade at constant slot AT (same torque, same copper loss)

**Decided: k = 2** (row in bold). The reference state k = 1 is what the field solutions were
run at; every k > 1 number is exact scaling (`lambda ~ k`, `R ~ k^2`, `I ~ 1/k`), not a new
solve, because the slot ampere-turns are unchanged.

Scaling the series turns by `k` at fixed copper fill keeps the slot AT and the torque
unchanged, scales current as `1/k`, terminal voltage as `k`, and leaves **kVA invariant**
(the resistive drop scales with k exactly like the back-EMF does).

| k | physical turns/coil (a=4) | N_c | phase current | R_ph | Vhat @ 3000 rpm | max speed, no FW | wire area / example |
|---|---|---|---|---|---|---|---|
| 1 | 5 | 1.247 | 102 A | 1.53 mOhm | 6.4 V | ~12,300 rpm | 4.58 mm2 (4 x 1.2 mm) |
| **2 (DECIDED)** | **10** | **2.494** | **51 A** | **6.12 mOhm** | **12.9 V** | **~6,130 rpm** | **2.29 mm2 (2 x 1.2 mm)** |
| 3 | 15 | 3.741 | 34 A | 13.8 mOhm | 19.3 V | ~4,090 rpm | 1.53 mm2 (1 x 1.4 mm) |

At k = 2 the decided build is: **10 turns/coil, a = 4, 2 strands of 1.2 mm per turn,
51 A peak, 12.9 V peak at 3000 rpm, 24-26 W copper, PF 0.53-0.58, ~0.99 kVA.** The 48 V
envelope is 91% used at 5,600 rpm (Vhat 24.0 V of 26.3 V), so any gearing that pushes the
motor past ~6,100 rpm needs k = 1.5 or field weakening.

Max speed = 3000 rpm x 26.33 V / Vhat(3000). Field weakening would extend it, but a SynRM
with this saliency is not a good field-weakening machine, so treat these as real ceilings.

## 4. Decision rule (applied)

The turns count is set by the application's maximum motor speed, not by preference:

    k <= 26.33 V / (6.44 V * v_max_rpm / 3000)

- Top speed <= ~4,000 rpm at the motor: k = 3, 34 A - cheapest controller and cabling.
- Top speed ~5,000-6,000 rpm: **k = 2, 51 A - SELECTED (D-013)** - the balance point for a
  2W with a 5-6:1 reduction (a 10-inch wheel at 45-60 km/h lands here).
- Top speed > 6,000 rpm (direct drive or tall gearing): k = 1, 102 A - current becomes the
  cost driver in the controller and harness.

The trigger for revisiting: the final gear ratio. If the motor must exceed ~6,100 rpm,
k = 2 fails on voltage and the choice returns to k = 1 (or k = 1.5 with field weakening).
At k = 2 the winding is 10 turns of 2 x 1.2 mm per coil, which is a heavier needle-winding
job than 5 turns of 4 x 1.2 mm but the same slot fill; see section 5.4.

kVA is ~1.0 kVA in every column, so the inverter's silicon is not what the turns choice
buys - it is the current rating and the speed range.

## 5. What is still open

1. **Final gear ratio** - the k = 2 choice is only valid while the motor stays below
   ~6,100 rpm. That is the one number left that can reopen D-013.
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
