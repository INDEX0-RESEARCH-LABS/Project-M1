# Rotor mechanical check — RESULT

Status: **PASS — margins are enormous.** Script: `simulation/scripts/rotor_stress_check.py`
(models declared frozen in `PLAN.md` before the run). First Gate-D deliverable; zero spend.

## Verdict table (σ_max = Kt × max(M-A ring, M-B spoke), σ_y = 230 MPa)

| rpm | SF @Kt=1.5 | SF @Kt=2.0 | SF @Kt=3.0 |
|---|---|---|---|
| 3000 (continuous rating) | 97.8 | 73.3 | 48.9 |
| 6000 (peak envelope) | 24.4 | 18.3 | 12.2 |
| 10000 | 8.8 | 6.6 | 4.4 |
| 15000 | 3.9 | 2.9 | 2.0 |

Frozen pass rule (SF ≥ 2 at 3000 and 6000 rpm across the whole Kt band): **PASS with
factor ≥12 headroom.** SF crosses 2.0 only at ~15,000 rpm even at worst-case Kt=3 —
five times the declared peak envelope. Identical for both bridge variants (0.6 mm
committed, 0.4 mm winner-family): thin-ring self stress is bridge-thickness
independent, and the inboard spoke path (as a solid-disk slice) is weaker than —
actually below — the ring mechanism, so the ring is the only design-carrying member.

**Airgap-closure sanity:** ring dilation ~9 µm at 15,000 rpm vs the 520 µm airgap —
negligible; no electromagnetic-mechanical coupling risk from spin growth.

## What this certifies (and what it doesn't)

- **Certifies (analytic, declared models):** the architecture is *not* mechanically
  bridge-limited at any plausible 2W traction speed; the thin-bridge barrier family
  survives spin with two orders of margin at rating. The winner-family bridge 0.4 mm
  carries no mechanical penalty — the D-011 topology conclusions stand unmodified by
  mechanics.
- **Does not certify:** stress concentrations from actual barrier-mouth corner radii
  (Kt is a declared band, Kt=3 covers the sharp-corner case); residual/laser-cut edge
  effects; press-fit or shaft-hub interference fits; burst containment beyond yield
  (never relevant at these margins); rotor end effects.
- **Standing caveat:** a real prototype's spin test at ≥1.2× peak envelope speed remains
  the Gate E acceptance item; this analytic result only licenses *designing to* that
  test, not skipping it.

## Next Gate-D zero-spend deliverables open

winding spec v0 (turns/current/voltage from committed constants), dimensioned
drawings from `SynRMGeometry`, test-plan skeleton. "BOM with quotes" stays
founder-gated (D-009).
