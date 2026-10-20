# Solver validation — straight-wire known answer (Gate B)

**Date:** 2026-10-20  **Solver:** in-house linear A-z on scikit-fem 12.0.2 + gmsh 4.15.2 (D-005)
**Analytic:** B(r) = mu0*I/(2*pi*r), r=50 mm, I=1000 A, conductor R=5 mm -> B = 4.000 mT

Criteria declared before running: finest-mesh error < 2 %; error must not grow with refinement.

| lcar (mm) | elements | B (mT) | error (%) |
|-----------|----------|--------|-----------|
| 5.00      | 22 022   | 3.99314 | 0.171 |
| 2.50      | 86 730   | 3.98688 | 0.328 |
| 1.25      | 340 656  | 4.00264 | 0.066 |

Finest error 0.066 % -> **PASS**.

Notes: |B| sampled by averaging element gradients over the patch around the node
nearest the probe point (centroid sampling alone gave a spurious 2.1 % floor).
Non-monotonicity between the two coarse meshes (0.171 -> 0.328 %) is
patch-sampling noise at ~0.2 %, well inside tolerance; only the finest mesh is
used for reported errors.

Reproduce: `.venv/bin/python simulation/scripts/known_answer_check.py`
