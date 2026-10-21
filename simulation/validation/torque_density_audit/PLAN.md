# PLAN — torque-density audit (pre-literature, zero budget)

**Declared before running.** Script: `simulation/scripts/torque_density_audit.py`.

## Why

The D-012 addendum concluded "~4× density gap vs 2W-class machines". A first-principles
cross-check on our own certified operating point (A ≈ 18–20 kA/m, B̂g ~0.5–0.9 T)
suggests **~100 N·m/m**, while the certified FEM value is **8.34 N·m/m**. Either
(a) the anchor barrier design genuinely suppresses torque by an order of magnitude
(possible but suspicious), or (b) some convention in the model suppresses excitation.
Before any literature workstream or envelope freeze, this must be settled on our own
machine, with numbers.

## Method (one solve + pure post-processing)

1. Solve the committed D-010 baseline at 3072/rows4, δ=26.25° (the certified point).
2. **MMF audit:** build the staircase MMF from the actual `d_pattern()` slot ATs;
   FFT it. Report the harmonic amplitudes by pole-pair order and the fundamental
   electric loading A1 = p·F1. Gate: the dominant torque-producing harmonic must be
   p=2 (4-pole); report any higher content.
3. **Gap-field audit:** sample Br on a circle at the gap mid radius (2880 points);
   FFT → fundamental B1, mean, max.
4. **Ideal sizing:** T_ideal = (π/2)·D²·L·σ with σ = 0.5·A1·B1 (per-metre and @74 mm).
5. **Ratio** T_fem / T_ideal. Also report the surface-ring saturation (Bmax) since the
   0.6 mm continuous ring is the declared q-bridge.

## Frozen interpretation rule

- If the dominant MMF harmonic is NOT p=2 → the excitation convention is wrong; the
  campaign's SynRM torque numbers are suspect and must be re-derived before any claim.
- If the harmonic is p=2 and T_fem/T_ideal < 0.2 → the model's field utilization is
  anomalously low vs classic sizing; record as an audit flag and cross-check the same
  geometry with xfemm before changing any decision.
- If the harmonic is p=2 and T_fem/T_ideal ≥ 0.2 → the earlier "density gap" narrative
  needs re-scoping (our density is within normal sizing losses; the target spec simply
  needs a bigger machine for 1.6 N·m continuous).
- Whatever the outcome: the audit's numbers replace narrative in D-012; no silent
  adoption of a favourite conclusion.
