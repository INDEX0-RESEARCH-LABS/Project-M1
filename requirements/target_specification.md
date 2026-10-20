# Target Specification v0 — PRELIMINARY

**Status:** PROVISIONAL, founder-approval pending. All values revisable per master prompt §3.
Basis: desk review above; not yet validated against a simulation baseline (Gate B) or application
duty cycle (Gate F).

## Prototype test-platform envelope (Phase 6)

| Parameter | Target | Confidence | Basis |
|---|---|---|---|
| Rated power (continuous) | 0.5 kW | ESTIMATE | Master prompt 0.5–1 kW |
| Peak power | 1.0 kW (≤60 s) | ESTIMATE | Master prompt |
| DC bus | 48 V nominal (24–48 V range) | ESTIMATE | Master prompt |
| Rated speed | 3000 rpm | ESTIMATE | 0.5 kW / ≈1.6 N·m; to be confirmed by drive-cycle work |
| Peak torque | ≥2.5 N·m (≤60 s) | ESTIMATE | Starting/gradeability, to be revisited |
| Cooling | Natural convection first; forced-air option | ESTIMATE | Minimises prototype complexity |
| Ambient | 10–45 °C, Indian operating conditions | ESTIMATE | L18 Indian drive-cycle context |
| Insulation class | Class B (130 °C) minimum | ESTIMATE | Confirm vs IEC 60085 at Gate D — standard text not yet obtained (gap: standards access) |
| Control | Closed-loop, sensored (encoder) first | ESTIMATE | Defer sensorless (L41/L42 are industrial-voltage) |

## Baseline comparison intent (Gate B/C)

Same stator envelope, same current density, same thermal limit for SynRM vs SRM; metrics:
average torque, torque-ripple RMS, torque per ampere, iron+ copper loss estimate, efficiency at ≥3
operating points. Drive-cycle weighting deferred until a specific 2W/3W application is chosen.

## Explicitly NOT yet specified

Cost target, efficiency target, IP rating, NVH limit in dB, exact duty cycle, production volume —
each requires application data (Gate F) or a validated baseline (Gate B) before a number is honest.
