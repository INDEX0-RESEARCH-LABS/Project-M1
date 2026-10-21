# Winding spec v0 — 36/4/3 SynRM (committed anchor envelope)

> **SUPERSEDED for the chosen frame by `winding_spec_v1.md`** (130/50 point design,
> corrected copper loss, turns/speed trade). This file is kept because it documents the
> 159/92 anchor envelope and the original target-spec mismatch.

**Status: connection topology FINAL for this envelope; turn/electrical numbers
INDICATIVE ±25% (B̂g band) — and they expose a target-spec mismatch that needs a
founder decision (below).** Date 2026-10-21. Companion artifacts:
`prototype/rotor_stress/RESULT.md` (mechanics), `requirements/target_specification.md`
(all rows ESTIMATE class).

## 1. Winding topology (concrete, geometry-driven — not indicative)

- 3-φ, 36 slots, 4 poles, **q = 3**, double layer, **full-pitch coils (slot 1→10, i.e.
  span 9)**. 60° phase belts of 3 slots, repeated ×2 per pole pair:
  `A+ A+ A+ | C' C' C' | B+ B+ B+ | A' A' A' | C+ C+ C+ | B' B' B'` (×2 around).
  (Matches the belt order already encoded in `rajini_anchor.d_pattern()` — used by
  every validated torqu run.)
- 12 coils per phase (4 poles × q=3). Coil pitch factor k_p=1; distribution factor
  k_d = sin(q·γ/2)/(q·sin(γ/2)) = sin15°/(3·sin5°) = 0.990 → **k_w ≈ 0.95 declared**.
- Connection: v0 declares all-serial per phase (1 parallel path); parallel-path
  count is a Phase-1 manufacturing choice that scales voltage/current at constant
  AT — torque and flux are invariant to it (validated machinery property).

## 2. Electrical budget (the computation that matters)

Constants (all from committed machinery/anchor):
slot Cu area 40.44 mm² (101.1 × 0.40 fill), thermal slot loading **242.6 A·t/slot**
(J = 6 A/mm² continuous, same-sign double-layer convention used by every FEM run),
stack 74 mm, R_ro 45.53 mm, τ_p = 71.9 mm, 4 poles.

Per-series-turn linkage at the operating field:
**ψ₁ = k_w·(2/π)·B̂g·τ_p·L = 2.41/2.90/3.22 mWb for B̂g = 0.75/0.9/1.0 T** (band is
INDICATIVE — B̂g comes from the campaign's saturation maps, not a measured curve).

EMF budget (SVPWM, 48 V bus): usable phase peak ≈ Vdc/√3 × 0.95 = **27.7 V**:

| operating point | f | ψ₁ range | N_ph ≤ (series turns/phase) | turns/coil (÷12) | coil current (AT/2Nc) |
|---|---|---|---|---|---|
| **OP-A: 3000 rpm motor (target spec)** | 100 Hz | 2.4–3.2 mWb | **13–17** | **1.1–1.4** | 170–225 A |
| OP-B: hub direct ~750 rpm | 25 Hz | 2.4–3.2 mWb | 55–73 | 4.6–6.1 | 17–22 A |
| OP-C: 1500 rpm geared 4:1 | 50 Hz | 2.4–3.2 mWb | 27–35 | 2.2–2.9 | 34–45 A |

**Torque is turn-count invariant** at fixed slot AT (the FEM's core validated
property): continuous torque = 8.34 N·m/m × 0.074 m = **0.62 N·m** at thermal loading;
peak target 2.5 N·m ⇒ ×4 AT ⇒ **J_peak ≈ 24 A/mm² for ≤60 s** (short-time window
plausible on a 7-ish kg Cu/Fe frame, INDICATIVE; continuous 1.6 N·m target would need
J ≈ 15.5 A/mm² continuous — **above** the declared thermal 6 A/mm²).

## 3. The finding the computation forces — spec/envelope mismatch

- **OP-A unbuildable for a 2W product:** 1–2 turn bar coils carrying ~200 A is
  industrial bus-bar winding, not a 48 V scooter inverter's profile (phase currents
  10× the plausible MOSFET-class inverter).
- **Hub-direct (OP-B) has a buildable winding but ~13–20× too little torque:**
  0.62 N·m continuous vs the ~8–12 N·m a 10-inch hub wheel demands; recovering it on
  this frame needs ~4,000 A·t/slot ⇒ J ≈ 96 A/mm² — thermally impossible.
- **OP-C (geared) matches torque; still bar-coil territory.**

**Consequence: the committed envelope (159/92 mm, R_ro 45.5 mm, τ_p 71.9 mm) is not
compatible with the current target spec through any manufacturable winding.** The
turn-count scalars are pure geometry: ψ₁ ∝ R² of the rotor — the frame is
electrically "stiff" (big flux per turn) for a 48 V/low-voltage product at
traction-electrical speeds.

## 4. Options for the founder review (decision D-012 candidate)

1. **Downsize/envelope redesign** — shrink R_ro (ψ₁ ∝ R²) toward a purpose-sized 2W
   frame (e.g. R_ro ~20–30 mm class) so the 48 V window lands at 6–10 turns/coil at
   3000 rpm. This invalidates the anchor-envelope FEM results as *design* numbers
   (they remain validation-chain artifacts).
2. **Revise target spec** — accept a slower electric base speed + single-stage gear
   (OP-C territory) or re-rate voltage/phase current (e.g. 72–96 V bus moves OP-A to
   N_ph 20–26 turns — still 2 turns/coil, marginal).
3. **Keep envelope, embrace OP-B torque deficit** — only viable if the vehicle is
   defined around low wheel torque (not a real 2W).

Recommended: **option 1**, with a fresh Gate-B-style validation pass on the new
envelope before any claim. This is exactly what the D-gate review is for; better
surfaced now than after the BOM.

## 5. What survives regardless of the option

- The belt/connection table (§1), k_w, the ψ₁–turns–EMF formulas, the AT↔torque
  invariance, and the J/AT ledger: all are envelope-independent design tools now
  recorded in-repo.
- Phase-0 validation chain: untouched (it certified methodology, not this envelope's
  marketability — as D-009 said all along).
