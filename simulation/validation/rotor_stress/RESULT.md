# RESULT - Gate B on the deep-barrier rotor: SF 12.2 at 7000 rpm (PASS)

Log: `/tmp/opencode/m1/rotor_stress_fem.log`. Gates: `PLAN.md` (declared before the run).
Script: `simulation/scripts/rotor_stress_fem.py`. Geometry: D-014 candidate S6
(4 barriers, span 44.5 mm, rib fraction 0.25, bridge 0.6 mm, 130 mm bore).

## 1. The harness is validated, not assumed

The old `rotor_stress_check.py` is a closed-form ring/spoke model that assumes a
continuous surface annulus. The deep rotor removed that annulus, so its answer would have
been an extrapolation. This run solves the field.

Known answer first: solid rotating disk, 6000 rpm, 90-degree sector with symmetry BCs.
Computed principal stresses vs the exact field at 0.55-0.65 R:

| | error |
|---|---|
| sigma_r | **0.17%** |
| sigma_theta | **0.12%** |
| peak sigma_theta | 5.33 MPa vs 5.33 analytic |

**M0 PASS.** (First attempt failed at 25% because the comparison mixed Cartesian and polar
stress components; the fix is in the script and is recorded here, not hidden.)

## 2. Rotor stress

Plane stress, fixed shaft bore, centrifugal body force, 53k and 80k elements:

| rpm | rays | elements | max [MPa] (r, corner dist) | p99.5 | p99 | bridge | corner area |
|---|---|---|---|---|---|---|---|
| 6000 | 720 | 53,408 | 24.2 (52.1 mm, 0.25 mm) | 13.8 | 13.0 | 16.5 | 0.49% |
| 6000 | 1080 | 80,128 | 23.3 (52.1 mm, 0.26 mm) | 13.8 | 13.0 | 16.0 | 0.51% |
| 7000 | 720 | 53,408 | 32.9 (52.1 mm, 0.25 mm) | 18.8 | 17.6 | 22.4 | 0.49% |
| 7000 | 1080 | 80,128 | 31.7 (52.1 mm, 0.26 mm) | 18.8 | 17.7 | 21.7 | 0.51% |

- **M1 mesh independence: PASS.** p99.5 changes +0.3% between meshes at both speeds.
- **M2 pass rule: PASS.** SF = 230/13.8 = **16.6** at 6000 rpm, 230/18.8 = **12.2** at
  7000 rpm, against the declared rule of 2.0.
- **M3 corner rule:** the peak sits 0.25 mm from a barrier corner and *decreases* 3.6%
  with refinement, so it is a resolved corner concentration, not an unbounded
  singularity. Even if it is used as-is: **SF 9.5 at 6000 rpm, 7.3 at 7000 rpm.**
- **Airgap closure:** rotor OD grows **3.8 um** at 7000 rpm against a 520 um airgap
  (0.7%). Negligible.

Physical read: the 0.6 mm surface bridge carries `rho w^2 r^2` = 12.9 MPa at 6000 rpm,
exactly what the thin-ring bound predicts, and the three 3.8 mm arc ribs share the rim
load rather than dumping it on the bridge. The pessimistic "bridge carries the whole rim"
hand bound of ~420 MPa is **refuted** by the field solve: the ribs carry it, as they must.

## 3. Interpretation limits (stated, not hidden)

- 2D plane stress, no inter-lamination shear, no interlocks, no shrink-fit preload, no
  thermal stress, no fatigue. Plane stress is the right 2D idealisation for a lamination
  stack; the rest are separate checks.
- The bore is fully fixed. That removes hub relief and therefore over-predicts stress.
- Yield 230 MPa remains the declared conservative value (D-009, no paid certificate).
- Stress scales as w^2: at the D-014 speed ceiling (~6,840 rpm) the p99.5 is ~17.9 MPa,
  SF ~12.9.

## 4. Verdict

**Gate B PASS with a factor of >7 even on the absolute peak.** Mechanical integrity is
not the failure mode for the deep-barrier rotor; it was the risk that could have killed
the idea and it did not.
