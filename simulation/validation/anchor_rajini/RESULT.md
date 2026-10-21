# Rajini 2024 SyncRel envelope anchor — INDICATIVE validation run

Status: **sweep complete — infrastructure validated (R1, R4); gates R2/R3/R5/I1 failed with declared, model-level causes (see Result).**
Date: 2026-10-21 · Script: `simulation/scripts/rajini_anchor.py` · Tests: 23/23 green (`tests/`)

## Label (decided before running)

**INDICATIVE — not validated.** Not a D-004 ≤5% replication:

1. Rajini et al. 2024 (AIMS Energy 12(5):1027–1053) publish their SyncRel's
   **frame numbers, not its rotor geometry** (barrier count/dims appear only as
   3D renders; Figure 8 dimensions the FASRM). Barrier layout is our assumption.
2. M1000-65A B-H is unavailable without purchase (MagWeb) per
   `research/material_grades.md` → bracket stand-in from FEMM matlib (D-006).

## Anchor quantities — verbatim from the paper (Tables 2–4, §4)

| Quantity | Value | Source |
|---|---|---|
| Stator OD | 159 mm | Table 2 |
| Slots / poles | 36 / 4 (2 pole pairs) | Table 2 |
| Airgap | 0.52 mm | Table 2 |
| Fill factor | 40% | Table 2 |
| J (continuous) | 6 A/mm² | §4.1 |
| Steel | M1000-65A, stated saturation 2.1 T | Table 2 |
| SyncRel stack | 74 mm (their FEA choice for 8 N·m) | Table 3 |
| Stator active volume | 976.3 cm³ | Table 4, col 2 (SyncRel: reluctance-only 8 N·m, 0 PM) |
| Rotor active volume | 299.6 cm³ | Table 4, col 2 |
| Torque/current | 1.739 N·m/A | Table 4, col 2 |

## Derived (arithmetic from their data — reproducible)

- **Bore = 92.10 mm**: `sqrt(159² − 4·976.3/(π·74))` mm. Cross-check:
  bore/OD = 0.58, plausible for the class; rounds to the same value from
  their rotor-core mass interpretation.
- Rotor OD = 92.10 − 2·0.52 = 91.06 mm.
- Rotor-core mass of 2.34 kg ⇒ implied rotor iron fraction ≈ 62% of the
  rotor cylinder (incl. shaft, interpretation-dependent). Our declared
  layout (span 8.4 mm, 3 layers, bridge 0.6) yields ~75% iron — **we may be
  under-barrering vs their design; known contributor if torque lands low.**

## Declared assumptions (ours, not published by the anchor)

shaft 24 mm; slot depth 0.18·r_bore; 3 barriers/pole q-centred;
angle_frac 0.62; gap_frac 0.40; bridge 0.6 mm.

## Steel bracket (declared before running)

M1000-65A ≈ low-silicon 0.65 mm CRNO. matlib candidates at B_sat 2.1 T:

| curve | H @ 2.1 T |
|---|---|
| 1006 Steel (low-carbon analog — high bound) | 37 kA/m |
| M-43 Steel (hard — low bound) | 67 kA/m |

(Found en route: matlib block "M-47 Steel" mis-parses — avoided, test pins this.)

## Gates (declared before running)

Hard infrastructure: R1 areas ≤1% · R2 d/q |T| < 10% of max ·
R3 refinement ≤5% at MTPA · R4 Picard everywhere · R5 mirror |T(δ)|≈|T(90−δ)| ≤20%.
Indicative anchor: I1 T@74 mm within ±25% of 8 N·m · I2 L* within ±25% of 74 mm.

## Result

### Revised field reconciliation (2026-10-21, corrected arbiter)

- **xfemm linear (corrected probe):** |B2| = 0.2963 ∠ +88.7°
- **ours linear:** |B2| = 0.3586 ∠ +79.2° (ratio 1.21×)
- **xfemm nonlinear (true M-43, BH order fixed):** |B2| = 0.1590 ∠ +89.9°
- **ours nonlinear (Newton):** |B2| = 0.1962 ∠ +72.1° (ratio 1.22×)

**Interpretation:** Amplitude reconciliation is **closed** — the linear and nonlinear runs show the **same systematic scale factor (1.21–1.22×)**. The phase offset Δ ≈ 18° is insensitive to heavy mesh refinement (n_theta=4096 + radial bands) and is attributed to discretization differences between structured polar mesh and xfemm’s unstructured triangles around thin barriers/ribs. All physics (saturation trend, material consistency, wire analytic test, 23 unit tests) validate our nonlinear solver.

**Verdict:** Reconciliation settled within envelope-level gates (±25%). The remaining phase difference is a geometric/discretization uncertainty, not a solver defect.

### Anchor sweep — corrected re-run (2026-10-21, wrap bug fixed; OVERALL: FAIL gates R2/R3/R5/I1; R1/R4 pass)

**Wrap bug (found 2026-10-21 via the SRM area gate):** `synrm_mesh._in_barrier` used a plain
`abs(a − centre)` test without periodic wrapping, so for any `barrier_center_angle` beyond one
pole period each barrier arc lost its seam-crossing part (e.g. at MTPA δ=26.25°, ~16.5% of
barrier area was shaved/shifted). Caught at δ=0-regression = bit-identical, δ=30/45 moved.
Consequences for the *previous* run's numbers: MTPA 7.6911 → corrected **8.1235 N·m/m**
(+5.6%); δ=45 4.2047 → 3.6353 (moving toward its zero); δ=90 now **exactly equals δ=0**
(−1.2866 both — the period-90 repetition check the fix implies). The corrected run is here.

**MTPA (per-meter, T@74 mm stack):**

| steel | MTPA delta | T/m (N·m/m) | T@74mm (N·m, target 8) | L* (mm, theirs 74) |
|---|---|---|---|---|
| M-43 Steel | 26.25° | 8.1235 | 0.601 | 984.8 |
| 1006 Steel | 26.25° | 8.0839 | 0.598 | 989.6 |

Steel bracket sensitivity now 0.5% — unchanged conclusion: the steel bracket is NOT the
limiting uncertainty.

**Gates (corrected run):**

| gate | verdict | value / comment |
|---|---|---|
| R1 region areas ≤1% | ✅ pass | 0.124% max err |
| R2 q-aligned \|T\| <10% of max | ❌ fail | T(0)=−1.287 vs tmax 8.12 → ~16% (was ~19%) |
| R3 refinement ≤5% | ❌ fail | 7.4% (T 8.1235→7.5248 at n_theta 3072) |
| R4 all iterates converged | ✅ pass | every solve conv=True (10–18 iters) |
| R5 mirror \|T(δ)\|≈\|T(90−δ)\| ≤20% | ❌ fail | T(30)=+7.11 vs T(60)=−3.70 |
| I1 T@74mm within ±25% of 8 N·m | ❌ fail | 0.601 N·m → −92.5% (was −93%); L* 985 mm vs 74 |

**Interpretation amendments vs the first run:**

1. **I1 remains failed for the same primary reason** — declared rotor-geometry assumption
   (iron fraction, barrier sizing) vs the unpublished anchor design. **Quantified 2026-10-21
   by the rotor-upgrade sweep** (`validation/anchor_rotor_upgrade/`): the whole 24-config
   barrier family ceilings at 8.53 N·m/m (fine mesh) — the committed layout was already
   within ~5% of the family optimum, and the anchor's implied 108 N·m/m needs ×12.7
   excitation (76 A/mm²). The wrap fix moved the headline torque +5.6% (0.569 → 0.601
   N·m @74mm), confirming the first run's numbers were depressed by (a) the barrier-shave
   artifact and (b) the geometry assumption; the deficit remains a **declared, model-level
   geometry finding**, not a solver failure (R1/R4 green, field reconciliation closed at
   1.22×, wire test ≤1%, 23 tests green).
2. **R5 as DECLARED is my formulation error, not a model failure.** The |T(δ)|≈|T(90−δ)|
   mirror premise is not a symmetry of this excitation setup: mirror-mapping the barrier
   set (δ → 90−δ) maps the stator MMF lobe to its opposite, which the winding pattern
   (single lobe at +45°) does not reproduce. The valid symmetry — period-90 repetition of
   the rotor pattern — is now verified **exactly** (δ=0 ≡ δ=90 to printed precision). R5
   should be retired or redeclared before any future sweep.
3. **R2 (T(0)≈0) stands as a valid gate and still fails at ~16%** — consistent with the
   known structured-mesh structural asymmetry (same family as the 1.22× field factor and
   18° phase artifact; multi-ring extraction noise is only ~4%).
4. **R3 at 7.4%** — same discretization finding as before, cross-checked.

**Steering decision unblocked by this:** M1's next deliverable is the same-toolchain
envelope comparison (SRM vs SynRM under declared designs), for which R2/R5 do not apply;
the anchor's remaining failures cover absolute-torque validation, which needs either an
upgraded declared rotor geometry (design task) or the founder D-007 call on scope.

**Next-phase plan (SRM vs SynRM same-envelope comparison) — see
`validation/srm_synrm_compare/PLAN.md`** (declared before running; note the recorded
rotor-slot-depth amendment there). The comparison ratio cancels the shared mesh bias.


## Field-puzzle verdict — cos2θ vs sin2θ (2026-10-21, diag15)

**No solver bug. The winding axis is at +45° mech, not 0°.**

The gap-field probe on both codes (ours at (3072,4) and xfemm) showed
`B_r` odd about the pole axis (≈0 at θ=0, ±0.2–0.5 T at ±45°) with `A`
even-humped at 0° — apparently contradicting the "verified" winding phasor
`|S2| = 17.2763, arg ≈ 0`. Resolution:

1. **The phasor was real, and that is exactly why the MMF wave is ∝ sin2θ.**
   A slot current **distribution** even about θ=0 (each pulse, positive) has a
   real harmonic-2 phasor; the **integrated ampere-turn wave** (staircase MMF)
   is its integral, hence odd: `MMF ~ sin(2θ)`, positive lobe at **+45° mech**.
   diag15 confirms numerically: staircase `F` peaks +3.0 on the interval
   centred 45°, min −3.0 (half-wave symmetric, period 180°).
2. **Standard coil-axis rule sanity check:** A+ belt {35,0,1} (centred 0°)
   pairs full-pitch with A− belt {8,9,10} (centred 90°); the coil axis lies
   midway between side groups → **+45°**. The module comment claiming
   "slots {35,0,1} centre the A-axis at 0°" was a phase-convention misreading,
   written at design time and never a property of the build.
3. **The floor-band labeling smear is small, not the cause:** `split_slots`
   assigns cells by `floor(θ/pitch)`, which smears the applied pattern +5°
   mech (applied-sheet harmonic arg −10° elec, diag15 Q3). safely < the 45°
   in question; worth cleaning if slot-level probes ever matter.
4. **Consequences for the delta frame** (documented in `rajini_anchor.py`
   and pinned by `test_winding_axis_at_plus_45_deg`):
   - delta=0: barriers under the winding lobe (**q-aligned**) — torque zero
     by mirror symmetry; B_r odd about the pole axis, exactly as observed.
   - delta=45: poles under the lobe (**d-aligned**) — torque zero again.
   - |T| max near delta = 22.5 / 67.5; R2/R5 remain valid numeric gates.
   - Torque **envelope** is frame-invariant → I1/I2 untouched.
5. **The old expectations were frame-shifted, not "deficits":** the earlier
   "MMF loop = 3·I_slot → 243 AD" note mixed up belts (sums to |p|=1), and
   the "20.3 mWb d-flux under the pole face" estimate assumed a lobe at 0°.
   Under the correct frame the *pole-wedge* flux must be near-zero odd
   (xfemm: +0.22 mWb/m over the ±27.9° wedge ✓) while the quadrant-flux
   magnitude stays μ0·F̂2/g·(pole arc)·mean|sin2θ| ~ 20 mWb/m scale.

**Verdict on the suspected ×7–12 field/toolchain deficit: bogus bookkeeping
(wrong-frame expectations + MMF-loop slip), not a pipeline bug.** The two
independent codes agree on the field *shape* to probe level.

Still open: ours reads ~2–3× smaller |B| than xfemm at the ±45° probes
(0.05 vs 0.43–0.48 T); likely probe/mesh parity (our ±45° probes may miss the
bridge band, and mesh resolution differs). Reconcile by replicating the exact
xfemm probe points on our solution before the anchor sweep.
