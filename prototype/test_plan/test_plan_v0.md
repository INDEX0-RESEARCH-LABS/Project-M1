# Gate-E test plan — skeleton v0

**Date:** 2026-10-21. **Status:** SKELETON, written before any hardware exists
(repo convention: plans declared before runs). Will be revised after D-012
resolves; this version is deliberately **envelope-agnostic** wherever the
envelope decision (D-012, PROPOSED) affects a number.

---

## 1. Purpose & scope

This plan defines what physical tests on the built prototype will certify at
Gate E (`ROADMAP.md`: "Manufactured prototype, calibrated instrumentation, test
results vs acceptance criteria → 5-point success definition met or falsified
honestly"), and what they will NOT attempt to re-certify that simulation has
already certified at Gates A–C.

Relationship to other artifacts:

- **Gate D inputs already landed (zero-spend):** rotor stress check
  (`prototype/rotor_stress/RESULT.md`) and winding spec v0
  (`prototype/design/winding_spec_v0.md`).
- **Open dependency:** D-012 (committed envelope vs target spec — winding
  infeasibility, envelope redesign recommended). Speed/turn/current acceptance
  numbers below are expressed against the *current* target-spec envelope
  (peak 6000 rpm) and must be re-derived if D-012 changes the envelope.
- Written **before any hardware exists**; will be revised after D-012
  resolves and after drawings exist.

## 2. What simulation has / has not certified

Objectives below are split so tests certify only what simulation cannot.

| Item | Status | Source |
|---|---|---|
| Solver chain validity (linear, nonlinear, xfemm parity) | Certified by simulation (23/23 tests) | Gate B validation chain |
| SRM vs SynRM architecture ordering at equal Cu/J/fill | Certified by simulation, same-extractor ratio 0.44 (single, mesh-converged; multi column uncertifiable) | D-008; `srm_synrm_compare/RESULT.md`; `extractor_convergence/RESULT.md` |
| Rotor mechanical survival at ≤6000 rpm (SF ≥ 2 across Kt=1.5–3 band) | Certified analytically (SF 18.3–24.4 @6000 rpm; crossings only at ~15,000 rpm) | `rotor_stress/RESULT.md` |
| Rotor stress concentrations from real barrier-mouth corners / cut edges | NOT certified — covers via spin test (T-06) | `rotor_stress/RESULT.md` ("does not certify" list) |
| Real steel B-H of purchased steel vs M-43/1006 bracket label | NOT certified — hardware/material test only (T-11, F) | D-009 consequence (2) |
| Thermal behavior, losses | NOT certified — simulation has no validated thermal/loss model in-repo | — |
| Torque ripple under rotation | NOT certified — FEM results are static rotor-angle curves; rotation dynamics untested | FEM artifacts (static curves) |
| Actual winding quality (fill, turns, R/phase), EMF constant | NOT certified — winding numbers are INDICATIVE ±25% | `winding_spec_v0.md` |
| Spin de-risk at ≥1.2× peak envelope speed | Explicit Gate E acceptance item, licenced by analytic result but not replaceable | `rotor_stress/RESULT.md` standing caveat |

## 3. Test objectives (mapped to Gate E + charter 5-point definition)

Charter points: (1) rotates under closed-loop control across agreed speed range;
(2) torque target at documented current limit; (3) efficiency at ≥3 operating
points traceable to calibrated instruments; (4) continuous-duty thermal test;
(5) data that confirms/falsifies the research hypothesis.

| Obj | Maps to | What tests must show | Note |
|---|---|---|---|
| O-1 | Charter 1 | Motor rotates under control from standstill to a stated speed range on 24–48 V bench | Drive/control electronics exist only if user-owned (D-009: no purchases without founder approval); acceptance numbers post-D-012 |
| O-2 | Charter 2 | Measured torque ≥ target at a stated current limit, static rig | Target-spec torque (≥2.5 N·m peak, ESTIMATE) vs committed-envelope thermal torque 0.62 N·m (winding spec) conflict — see §6 |
| O-3 | Charter 3 | ≥3 operating points measured with input V·I and output torque+speed | "Traceable to calibrated instruments" NOT achievable at cost 0 — F-gated (T-10). At cost 0 = rough labelled data only, honestly separated |
| O-4 | Charter 4 | Continuous-duty run without exceeding insulation-class temperature | Class B 130 °C per target spec (ESTIMATE; standard text gap noted there) |
| O-5 | Charter 5 | All recorded data usable to confirm/falsify the SynRM traction hypothesis | Honesty labels §4 make this meaningful |
| O-6 | Gate D handover → manufacturing | Winding fabricable to spec (continuity, R symmetry, insulation) | Accept-with-label until a final turn count exists |

## 4. Test matrix v0

Cost class: **0** = existing / user-owned / DIY; **F** = requires founder
approval & funds (D-009: no purchases). Acceptance numbers marked ✠ are
ESTIMATE-labeled placeholders pending D-012 / winding-spec revision.

| ID | Objective | Method | Instrumentation | Operator skill | Pass / accept-with-label rule | Cost |
|---|---|---|---|---|---|---|
| T-01 | Winding continuity + R per phase | DC resistance, per phase, all three phases | Multimeter with µΩ/mΩ-milliohm range (user-owned) | Any careful listener-to-instructions adult | ✠ All 3 phases within ±10 % of mean (placeholder ESTIMATE — set honestly at winding finalize); absolute value recorded, *accept-with-label*: no numeric target yet (turn count open → D-012) | 0 |
| T-02 | Insulation integrity, winding-to-frame | DC insulation resistance at DIY-safe voltage (multimeter + battery stack ≤48 V class); NO megger at cost 0 | Multimeter (resistance range) | Adult, electrical-safety briefed | ✠ Resistance above meter resolution with frame-lead contact verified (placeholder ESTIMATE); proper megohmmeter test + insulation-class verification → F (T-12) | 0 |
| T-03 | Static torque-vs-angle | Current steps at held angles; torque lever arm reading on a kitchen/cargo scale; angle by indexing (drawings, protractor-class) | Lever arm (measured length, recorded), scale, DC supply | Adult, mechanical aptitude; second person present | Curve obtained; ✠ peak ≤60 s current at declared supply limit recorded. Compare shape/order only vs FEM curve at cost 0; absolute target comparison needs label assessment per §5 | 0 |
| T-04 | No-load spin-up + speed | Supply via declared controller (user-owned, else F); speed from phone slow-motion video frame-counting, or reflective sticker + phone tach app | Smartphone camera/apps | Adult with phone; second person present | Reaches continuous-test speed (✠ 3000 rpm per target spec, ESTIMATE) and holds; speed quantified by frame count over ≥5 s | 0* (*controller-dependent; else F) |
| T-05 | Locked-rotor current vs supply limit | Rotor held rigid at a known angle; current from supply readout or multimeter series | DC supply metering, multimeter | Adult; second person present; ≤60 s dwell | Measured current ≤ declared supply limit at the held angle(s) tested; value recorded for inverter design | 0 |
| T-06 | Spin de-risk (Gate E mechanical acceptance) | Unguided free spin to ≥1.2× peak envelope speed inside containment guard, then inspect | Same as T-04 + guard enclosure (DIY bar-guard) | Adult only, per §6 safety rules, second person present | ✠ ≥1.2× peak envelope speed reached without visible failure: for current target-spec envelope (6000 rpm peak) = **≥7200 rpm (computed)**; re-derive if D-012 changes envelope. Failure/deformation of any kind = FAIL, no re-test without fracture analysis | 0 |
| T-07 | Continuous-duty thermal | Declared operating point run ≥30 min (duty exact value pending D-012): temperature by touch-proxy (≤few-second contact protocol), IR-phone-app spot readings, thermocouple only if user-owned | Touch protocol, phone IR app, thermocouple (if owned) | Adult; second person present | ✠ No reading/experience above class-B-consistent indication (130 °C, ESTIMATE). Accept-with-label: phone IR accuracy is not calibrated — record as MEASURED (class: phone) and correlate at F-class test | 0 |
| T-08 | Vibration / noise (subjective + phone) | A/B listening tiers, phone SPL app readings at fixed distances (documented positions) | Smartphone SPL app | Adult | No numeric NVH limit exists in target spec ("explicitly NOT yet specified" — dB) → accept-with-label: record levels + subjective notes; target-spec number deferred to Gate F per target spec | 0 |
| T-09 (F) | Efficiency at ≥3 operating points, "traceable to calibrated instruments" | Calibrated torque/speed + power instrumentation | Dynamometer-class rig, calibrated power analyzer | Professional/lab | Charter point 3 hard requirement → needs F funding; NOT certificable at cost 0 | F |
| T-10 (F) | Steel material identity check (real B-H vs M-43/1006 label) | Coupon B-H at local lab, or per-machine back-EMF/inductance characterization | Lab access | Lab technician | D-009 consequence (2) names prototype-material measurement as the upgrade path | F |
| T-11 (F) | Dynamometer torque-speed / efficiency map | Instrumented dynamometer | Dyno rig | Professional | Charter 1 "agreed speed range" full sweep + charter 3 | F |
| T-12 (F) | Megohmmeter insulation test + insulation-class verification vs "not-yet-verified" standard text | Megger at lab-class voltage | Megohmmeter, standard text access (target spec notes: IEC 60085 text not yet obtained — gap) | Professional | Pass = meets class-B requirement under verified standard | F |

**Explicitly excluded at cost 0:** NO dynamometer, NO calibrated power
analyzer, NO megohmmeter. T-09/T-10/T-11/T-12 are the F-class list; every
other row assumes no acquisition.

## 5. Data recording conventions (mirrors `reports/PHASE0_SUMMARY.md`)

1. **Labels on every datum:** `measured` (hardware reading, instrument named),
   `projected` (computed from a labeled sim/model), `assumed` (declared, not
   verified). Never merge classes in one number without a compound label.
2. **INDICATIVE ±25%** attaches to anything materially dependent on the
   M-43/1006 B-H bracket (D-009: label is permanent for Phase 0; does NOT
   silently upgrade to verified when real steel arrives — T-10 does that).
3. **Analogue of the same-extractor rule:** only same-rig, same-condition
   comparisons are quotable across test configurations; cross-rig comparisons
   carry a declared correction note or are not quoted.
4. **No purchase-dependent claim** anywhere in a cost-0 row (D-009).
5. Each RESULT document produced from this plan must state what it does NOT
   certify (pattern: `rotor_stress/RESULT.md`).

## 6. Safety review (skeleton — full review lands with drawings at Gate D)

- **Rotating machinery:** containment guard mandatory for T-04/T-06 and any
  run above standstill. Rationale (grounded in `rotor_stress/RESULT.md`):
  energy stored at our speeds is modest given SF ≈ 12–24 at 6000 rpm across
  Kt = 1.5–3; the guard rule stands anyway — the analytic check does not
  certify real corner radii, cut-edge effects, or press fits.
- **Electrical (48 V DIY class):** battery/DC-limited supply; no exposed
  live areas during rotation; locked-rotor dwells ≤60 s; current path fused
  or supply-limited (T-05 exists partly for this).
- **ESD:** n/a for these hardware tests (no exposed precision electronics
  under assembly by any cost-0 row).
- **Personnel:** first-aid kit present; fire extinguisher present (electrical-
  rated class per local availability — exact class to be verified at install,
  not asserted here); **no test without a second person present** (applies to
  all rotational and powered rows).
- **Standards:** applicable safety standards to be identified (not verified) —
  consistent with the target spec's own note that standard text access is a
  known gap (IEC 60085 referenced there as unverified).

## 7. Risks & open dependencies

| # | Risk / dependency | Effect on plan | Mitigation |
|---|---|---|---|
| R-1 | **D-012 unresolved:** committed envelope (R_ro 45.5 mm, τ_p 71.9 mm) cannot host any manufacturable 2W winding at the 3000 rpm target spec (1–2 turn bar coils @ ~200 A; hub-direct 13–20× short on torque) — `winding_spec_v0.md`, D-012 PROPOSED | Every envelope-dependent acceptance number (speeds, turns, currents) is provisional ✠ | Plan kept envelope-agnostic; §4 numbers re-derived after D-012 |
| R-2 | Target-spec internal mismatch surfaced by winding spec: peak torque ≥2.5 N·m (spec) vs 0.62 N·m continuous thermal torque on the committed frame; 1.6 N·m continuous target would need J ≈ 15.5 A/mm² vs declared 6 A/mm² | O-2 undefined until spec/envelope reconciled | O-2 text split into "record measured" + "compare vs reconciled target" |
| R-3 | Charter point 3 requires "traceable to calibrated instruments"; D-009 forbids purchases without approval | Efficiency point cannot be certified at cost 0 | Split into rough-protocol (0) and F-class T-09/T-11 — honest separation, founder decision |
| R-4 | Steel purchase (F-class) for real-material fidelity | Absolute torque/EMF vs sim stays ±25 %-indicated | T-10 as the named upgrade path (D-009 consequence) |
| R-5 | Phone-class instrumentation accuracy (IR temp, SPL, slow-mo speed) | "Measured ≠ acceptance-grade" for some rows | Rows state instrument class in the label; acceptance-grade versions live on F rows |
| R-6 | No calibrated target exists yet for efficiency, NVH (dB), exact duty cycle — target spec "explicitly NOT yet specified" | Several rows must be accept-with-label, not pass/fail | Recorded; numbers deferred to Gate F / Drive-cycle work per target spec |

## 8. Revision history

| Version | Date | Author | Note |
|---|---|---|---|
| v0 | 2026-10-21 | M1 agent, pending founder ratification of D-012 | Skeleton written before any hardware exists; envelope-agnostic pending D-012; no git commit made by this step |
