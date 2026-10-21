# D-012 envelope sizing — revised after the torque-density audit

**Status: sizing scan revised (parallel-path winding model).** Script:
`simulation/scripts/envelope_sizing.py`. Audit that forced the revision:
`simulation/validation/torque_density_audit/RESULT.md`. All torque numbers are
ESTIMATE class (linear AT scaling from the certified anchor point).

## What changed since the first version of this note

1. **The "~4x density gap" framing was wrong.** The audit measured our own operating
   point: A1 = 9.7 kA/m, Bhat = 0.269 T, textbook shear 1.31 kPa, FEM shear 0.56 kPa ->
   **utilization 0.43**, which is normal for a SynRM with a partly-aligned field. There
   is no order-of-magnitude defect. The ~100 N.m/m expectation that started the audit was
   an arithmetic error (|AT|-sum/circumference is not the fundamental electric loading).
2. **The first scan assumed series-only windings.** With `a` parallel paths the physical
   turns per coil rise by `a` at the same terminal voltage. That is standard 48 V traction
   practice and it changes the windability answer completely.

## Corrected scan (36 frames: 2/4/6/8 poles x D 90/110/130 mm x L 30/50/74 mm)

At 3000 rpm, 48 V SVPWM, J = 6 A/mm2 continuous, fill 0.40, q = 3, Bhat = 0.9 T,
torque from the certified anchor shear (642 Pa at 242.6 AT/slot, linear in AT):

- **Windable at some a in (1,2,4): 24 of 36.**
- **Meeting both torque targets (1.6 N.m cont / 2.5 N.m peak): 1 of 36** —
  **2-pole, D = 130 mm, L = 74 mm**: N_c = 1.7 (a=1) / 3.4 (a=2) / 6.8 (a=4),
  AT/slot 355 A, T_cont = 1.84 N.m, T_peak = 7.4 N.m (peak is generous because the
  linear extrapolation to J=24 is optimistic).
- The 4-pole 130/74 frame gives 0.92 N.m continuous — half the target — but is the
  natural next step if the frame can grow: T scales roughly with D^2..D^4 in this model,
  so a 4-pole bore around 150 mm reaches ~1.6 N.m continuous and stays windable with
  a = 6 (4.1 turns/coil).
- High pole counts lose torque at fixed J (slot area per slot falls as slots multiply)
  and demand fewer turns per coil — the worst combination.

## What the numbers mean

- The target is **not** blocked by a density mystery. It is blocked by the **product
  J x active volume** at 3000 rpm / 48 V.
- Windability is a **parallel-path** choice, not a hard wall: 3-7 turns per coil at
  a = 2-4 is normal for 48 V machines.
- The 130 mm / 74 mm 2-pole point is a plausible 2W hub-class frame (stator OD ~158 mm),
  but it needs a **2-pole SynRM rotor topology** (barriers spanning 180 deg), which the
  current `synrm_geometry` module does not model (it is 4-pole). That is a geometry +
  FEM re-validation task, zero budget.
- The principal *unvalidated* risk is thermal: ~90-100 W of copper loss in a 130 mm frame
  at 1.8 N.m / 3000 rpm (about 580 W mechanical). J = 6 A/mm2 continuous assumes
  forced-air-class cooling, not sealed natural convection. This must be checked before
  any spec commitment.

## Recommendation

1. **Envelope: 4-pole, bore 150 mm, L = 74 mm is FEM-validated** at J = 6 A/mm2
   (5.07 N.m @ 74 mm rows40, ~3x the 1.6 N.m target; bracket spread 3%). Winding:
   ~4 turns/coil with a = 6 parallel paths. See
   `simulation/validation/envelope_validation/RESULT.md`.
2. **The frame is over-sized for the target** (~5 N.m at J=6 = ~1.6 kW). Next task is a
   point design at bore 110 and 130 mm with the same proportions; pick the smallest frame
   holding >= 1.6 N.m cont with >= 25% margin.
3. The 2-pole 130/74 point from the scan stays available as an option to reduce OD, but
   it is no longer needed: it would require a new 2-pole rotor topology, and the 4-pole
   150 mm route is already validated.
4. **Gates before spec freeze:** (a) certified rows40 extraction with a monotone trace at
   the chosen bore, (b) first-order copper-loss/PF/thermal estimate at the operating J,
   (c) BH-extrapolation note for local Bmax ~3 T in the bridges.
5. No envelope freeze until (1)-(4) land.

## Caveats (unchanged)

- Linear AT->torque extrapolation is optimistic at high AT; the continuous points use
  AT ~ 130-355 A, close to the certified 242.6 A, so the continuous numbers are the
  credible ones; peak numbers are indicative only.
- Bhat = 0.9 T single point (band 0.6-1.0 -> roughly +/-40% on turns and torque).
- Slot-area/annulus proportions are declared assumptions (42% slot fraction, 14 mm
  radial build).
