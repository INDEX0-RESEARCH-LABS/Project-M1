# Torque extraction validation — full machine

**Status:** solver shakeout, 2026-10-20. Steel = M-19 Steel from the FEMM
library — a **placeholder** (D-006/D-007 prohibit M-19 for anchor
comparisons). Every number here is indicative of solver quality only.

## What was built

- `synrm_first_solve.py` — first full nonlinear machine solve: 24-slot winding
  table, per-slot current regions, d/q-axis alignment checks, Maxwell torque
  at 4 stator MMF angles, co-energy cross-check attempt.
- `synrm_torque_sweep.py` — rotor-rotation instrument: barrier-set centre angle
  shifted in fine steps (2–8 deg) against a fixed d-axis stator pattern, both
  torque instruments at matched strides.
- `synrm_torque_convergence.py` — **adopted validator**: mesh-refinement
  convergence of the Maxwell-stress torque + radius independence inside the
  airgap.
- Mesh upgrades in `synrm_mesh.py`: rays aligned to slot/barrier boundary
  angles (no centroid stair-stepping at material edges), extra airgap element
  rows (`n_gap_rows`), plus the barrier-centre-angle parameter wired into both
  the geometry module and the mesh classifier.

## Checks and results (torque_convergence, K1–K4)

| level | rays | gap rows | elems | iters | T_mid | radius spread | worst region err |
|-------|------|----------|-------|-------|-------|---------------|------------------|
| L0    | 768  | 2 | 51 448  | 32 | +0.02897 | 45.4% | 0.122% |
| L1    | 1536 | 4 | 109 880 | 32 | +0.02941 | 3.7%  | 0.016% |
| L2    | 3072 | 4 | 212 792 | 32 | +0.03017 | 2.4%  | 0.075% |

- K1 region areas vs closed form ≤0.14% at every level — **PASS**
- K2 finest-two torque agreement: 2.6% (gate 5%) — **PASS**
- K3 radius independence ≤3% at finest (was 45% at L0) — **PASS**
- Converged Maxwell torque at the test operating point (MMF at 15 deg mech,
  6 A/mm² Cu at 40% fill, 64 mm stack, M-19 placeholder):  **T ≈ 0.030 ± 0.001 N·m**

Other structural checks from `first_solve`/`sweep` (older unrefined mesh):
d-axis and q-axis alignment both read |T| ≈ 0 as symmetry requires; torque is
antisymmetric under reversal of the excitation pattern; Newton–Picard
converges in 31–36 iterations everywhere.

## Why the co-energy cross-check was withdrawn

The original plan used T ≈ dW'/dθ from two neighbouring solves as the torque
cross-check, per the sheet-pair failure earlier. On the machine it fails as an
*instrument*, not because the physics is violated: the signal (small-stride
ΔW′) is ≈2% of the total co-energy W′ ≈ 0.230–0.235 J (per 64 mm stack), below
the solve-to-solve reproducibility floor of the Picard fixed point. The
30-deg-stride version also averages the torque over a range where dT/dθ is
large, so it is not comparable to a pointwise reading. The instrument was
replaced by the convergence study above — the standard FEM route — and any
future co-energy use is restricted to large ΔW′ (e.g. total d↔q inductance
difference) where the signal clears the noise floor.

## Known limitations

- M-19 placeholder steel; anchor-grade B (M1000-65A / 35A300) still blocked on
  sourcing (MagWeb decision pending, fallback: digitize from anchor paper).
- The winding table is a 2-slot-per-belt double-layer-equivalent pattern;
  end-windings are outside the 2D domain (standard).
- The torque at the tested operating point (~2 A-turns/slot level) is ~1×
  lower than the machine's capability estimate; higher-current anchor
  operating points will exercise saturation harder and need their own
  convergence pass at those levels.
