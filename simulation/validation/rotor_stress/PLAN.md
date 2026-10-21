# PLAN - Gate B for the deep-barrier rotor (2D plane-stress FE)

**Declared before running.** Script: `simulation/scripts/rotor_stress_fem.py`.
Log: `/tmp/opencode/m1/rotor_stress_fem.log`. Geometry: D-014 candidate S6
(4 barriers, span 44.5 mm, rib fraction 0.25, bridge 0.6 mm, 130 mm bore).

## Why a field solve

`rotor_stress_check.py` (Gate B, 2026-10-20) models the rotor as a continuous
surface annulus plus a solid-disk spoke. That is right for the shallow barrier set,
where a thick iron ring sits under the barriers. The D-014 candidate removes that
ring: four full-depth barriers leave a **0.6 mm surface bridge and three 3.8 mm arc
ribs** carrying the rim. How the centrifugal load splits between them is statically
indeterminate; a hand factor cannot answer it.

## Frozen model

- Rotor lamination only, iron; barrier polygons are traction-free holes.
- Plane stress, E = 200 GPa, nu = 0.30, rho = 7870 kg/m3 (M-43 class).
- Centrifugal body force f = rho w^2 r (rotating frame, static solve).
- Shaft bore fully fixed: the stack is pressed on a steel shaft far stiffer than the
  lamination; this is the conservative choice for the ribs.
- Sharp barrier corners produce a linear-elastic stress singularity. With constant
  strain triangles the peak grows with refinement, so the peak is **not** a physical
  stress and cannot be a pass statistic.

Not modelled (recorded, not hidden): inter-lamination shear and interlocks,
shrink-fit preload, thermal stress, fatigue, magnet-free rotor damping, stack
clamping, and out-of-plane bending.

## Frozen gates

- **M0 known answer**: solid rotating disk, 6000 rpm, 90-degree sector with symmetry
  BCs. Computed sigma_r and sigma_theta must match
  `rho w^2/8 [(3+nu)(R^2-r^2)]` and `rho w^2/8 [(3+nu)R^2-(1+3nu)r^2]` within **5%**
  over 0.55R-0.65R. If this fails, the harness is wrong and nothing else is reported.
- **M1 mesh independence**: area-weighted **p99.5** of von Mises must change < **10%**
  between 720 and 1080 rays, at both speeds.
- **M2 pass rule**: **SF = 230 MPa / p99.5 >= 2.0** at 6000 rpm (the declared peak
  envelope) and at 7000 rpm (the D-013 speed ceiling plus margin). 3000 rpm is
  reported for completeness; stress scales as w^2 so it is a quarter of 6000.
- **M3 corner rule**: a peak lying within 0.5 mm of a barrier corner is classified
  singular, reported, and excluded from M2. The p99.5 area-weighted statistic is the
  pass metric because it is dominated by the rib/bridge field, not by re-entrant
  corners.
- **M4 no adoption by association**: passing M2 certifies the D-014 *geometry at the
  declared speed and yield* only. Copper, iron loss, ripple and manufacturability
  remain separate gates.

## Interpretation rules

- Yield 230 MPa stays the declared conservative value (no paid certificate, D-009).
- The fixed bore means the model cannot show hub relief; that makes the numbers
  pessimistic, not optimistic.
- If M2 fails, the candidate is dead at that speed and the report says so; no
  retuning of the statistic.
