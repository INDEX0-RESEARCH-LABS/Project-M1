# PLAN - dq model (Ld, Lq, flux linkage, PF) from the 130/50 solutions

**Script:** `simulation/scripts/dq_model.py`.
**Basis:** certified 130 mm bore / 50.4 mm stack frame
(`../envelope_point_design/RESULT.md`), single-ring extractor, M-43 bracket.

## Question

Replace the ESTIMATE power-factor upper bound with a dq model extracted from the
*same* field solutions: what are Ld, Lq, the saliency ratio, the terminal voltage at
3000 rpm, the real PF, and what winding actually fits the 48 V bus?

## Method (declared before running)

- Flux linkage of phase A from the slot stream function:
  `lambda_A = L_stack * N_c * ( sum_{A+} Abar_k - sum_{A-} Abar_k )`, where `Abar_k` is
  the area-weighted mean of the nodal A over slot k and the A+/A- slots come from
  `slot_phase36`. This is geometric (valid with saturation); it is identical to
  `(1/i_A) * int J_A . A dV` for a uniform slot current.
- `L = lambda_A / i_A` with `i_A = AT_slot / N_c`, `AT_slot = J * FILL * A_slot`.
  L therefore scales as `N_c^2` - reported at the current 48 V design winding and at
  the rescaled winding.
- **Ld** from rotor d-alignment (delta = 45 deg), **Lq** from q-alignment (delta = 0),
  both at the operating current. Operating point delta = 26.25 -> beta = 18.75 deg
  from the d-axis, `i_d = I cos(beta)`, `i_q = I sin(beta)`.
- `T_dq = 1.5 * p * (Ld - Lq) * i_d * i_q`, p = 2.
- Steady state: `v_d = R i_d - w Lq i_q`, `v_q = R i_q + w Ld i_d`, `w = 2 pi f`,
  `R = rho * 12 * N_c^2 * MTL / (FILL * A_slot)`.
- PF from the FEM torque: `PF = (P_cu + T_FEM * w) / (1.5 * Vhat * Ihat)`,
  `P_cu = 1.5 * R * Ihat^2`. Iron loss excluded -> PF is an upper bound.

## Declared checks (before running)

- **D1** saliency: `Ld > Lq` (a negative/zero result would mean the extraction or the
  winding mapping is wrong).
- **D2** model vs solve: `|T_dq - T_FEM| / T_FEM <= 25%` at the operating point. A
  first-order two-parameter model that ignores cross-saturation is allowed to be
  sloppy, not to be silent; if it fails, report the gap, do not tune factors.
- **D3** extraction convergence: operating point re-run at 3072 rays / rows 10;
  `|L(3072) - L(1536)| / L <= 10%`.
- **D4** bus fit: report `Vhat` against the 26.33 V peak phase ceiling and the turns
  rescaling that brings `Vhat` to <= 24 V, with the resulting phase current.

## Declared prediction

From `B1 = 0.27 T` at J = 6 (lambda ~ 12.7 mWb at 109 A): **L ~ 0.1-0.2 mH at the
current winding**, saliency ratio 2-4, `Vhat ~ 8-15 V` (large voltage headroom), PF
0.4-0.6, and a turns rescale of ~2-3x cutting the phase current to ~40 A at unchanged
copper loss. If the measurement contradicts this, the prediction is what was wrong.

## Limits

- 2D, single-ring extractor, M-43 bracket (same limits as the parent result).
- No iron loss, no end-winding inductance, no cross-saturation closure: the dq model
  is a first-order description, labelled as such in the result.
