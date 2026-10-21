# D-012 envelope sizing scan — proposal

**Status: scan complete; the finding is decisive — the binding constraint is torque
DENSITY, not envelope sizing.** Script: `simulation/scripts/envelope_sizing.py`
(reproducible, formulas + self-checks in the docstring). All numbers ESTIMATE class.

## What was scanned

n_poles {2,4,6,8} × D_rotor {90,110,130} mm × L_stack {30,50,74} mm, at 3000 rpm,
48 V SVPWM, J=6 A/mm² continuous (declared thermal), fill 0.40, q=3, B̂g=0.9 T,
slot area from the annulus (42% slot fraction), torque from the **certified
single-ring anchor density** (642 Pa shear at 242.6 AT/slot, linear in AT — the
optimistic extrapolation is declared in the script).

## Results

- **Windable at 48 V / 3000 rpm: 1 of 36 candidates.** Turns/coil at this
  voltage/speed are geometry-forced: N_c ∝ 1/(B̂g·D·L). Only the **2-pole,
  D=90 mm, L=30 mm** point lands in the buildable 6–12 turns/coil band
  (N_c = 6.1, I ≈ 21 A).
- **That one windable candidate delivers 0.26 N·m continuous / 1.03 N·m peak**
  (linear estimate) — ≈6× short of the 1.6 N·m continuous target and ≈2.4× short
  of the 2.5 N·m peak.
- **Candidates meeting both torque targets: 0 of 36.** The two constraints pull
  opposite ways: windability wants small D×L (low flux per turn), certified
  torque wants large D⁴·L — there is **no intersection at 48 V / 3000 rpm with
  the certified torque density**.
- Voltage is not a fix either: N_c ∝ V (96 V doubles the windable window) but
  torque-per-AT is unchanged, so the torque gap remains.

## The real number under the mismatch

Target 1.6 N·m at a realistic 2W frame (D≈100 mm, L≈40 mm) implies a gap shear
of ≈2.5 kPa. The campaign's **certified** shear is ≈0.64 kPa. That is the gap to
close — a **~4× density gap** (not the anchor's ×12.7, which compares against the
paper's own claim). Density is not a sizing variable: it comes from topology,
current density, and material working points.

## Recommendation to the founder (supersedes the three options in D-012 as written)

1. **Do not freeze an envelope yet.** Any envelope that is windable at 48 V/3000
   rpm is torque-starved by the certified density; any envelope with the torque
   is unwindable at that voltage/speed.
2. **Open a zero-budget density workstream first** (research + existing FEM):
   - comparative analysis of published 2W-class SynRM/IPM machines: pole counts,
     J values (continuous/peak), B̂g, slot/pole geometry, reported N·m/L;
   - re-examine our own J/AT convention against those machines (this campaign's
     642 Pa at 242 AT/slot is suspiciously low vs literature shear levels);
   - then decide: topology upgrade, spec revision, or voltage/architecture change.
3. **Spec revision remains available** (honest fallback): the certified-reachable
   continuous rating at 48 V/3000 rpm with a windable frame is ≈0.26 N·m
   (≈0.08 kW) — far from a 2W product, which is exactly why step 2 comes first.

## Re-validation plan (when an envelope is chosen)

Cheap, on existing machinery: rebuild `SynRMGeometry` for the candidate →
`expected_areas` sanity → mesh at 1536/3072 → certified single-ring extraction at
rows=40 (the campaign standard) → same-extractor ratio checks only → anchor
envelope comparison labels unchanged (INDICATIVE ±25%, D-009).

## Caveats

- Linear AT→torque extrapolation is optimistic at high AT (saturation) — flagged;
  it does not change the windability conclusion (which is purely ψ₁/EMF algebra).
- B̂g=0.9 T single point (band 0.6–1.0 → ±~40% on turns/coil and torque).
- Slot-area/annulus proportions are declared assumptions (42% / 14 mm radial build).
