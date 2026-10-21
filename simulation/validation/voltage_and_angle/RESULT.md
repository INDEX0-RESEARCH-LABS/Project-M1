# RESULT - 48 V / 96 V, and whether current angle can buy PF

Log: `/tmp/opencode/m1/pf_angle.log`. Gates: `PLAN.md`. Tests:
`tests/test_voltage_scaling.py` (V1/V2, 1e-12).

## 1. Voltage table (exact turns scaling - DERIVED, no new solve)

At constant slot ampere-turns: `V ~ k`, `I ~ 1/k`, `R ~ k^2`, `P_cu` invariant, speed
ceiling `~ 1/k`, and **`S = 1.5 Vhat i` invariant**. Pinned at 1e-12.

| bus | k | turns/coil | I peak | R_ph | Vhat @3000 | speed ceiling | S | PF |
|---|---|---|---|---|---|---|---|---|
| 48 V | 2 (D-013) | 10 | 51.0 A | 6.12 mOhm | 13.0 V | 6,058 rpm | 999 VA | 0.53-0.58 |
| 96 V | 2 | 10 | 51.0 A | 6.12 mOhm | 13.0 V | **12,115 rpm** | 999 VA | 0.53-0.58 |
| 96 V | 4 | 20 | **25.5 A** | 24.5 mOhm | 26.1 V | 6,058 rpm | 999 VA | 0.53-0.58 |

**The 96 V option does not reduce apparent power by one VA.** It buys (i) twice the speed
ceiling at the same winding, or (ii) half the current if the turns are doubled, at the
cost of twice the cells and a 20-turn coil of 1 x 1.2 mm. Controller VA is set by PF:
`S = P_in/PF` = 981 VA at PF 0.55, 899 VA at 0.60, **1,087 VA at the corrected current**
(see `torque_extractor/RESULT.md` section 3).

Consequence: the D-012 framing "accept ~1 kVA, or go to 96 V" is a **false binary**. The
real choice is in section 4.

## 2. Current-angle sweep at J = 5.34 (SOLVED, one solve per angle)

| delta | T [N.m] | Vhat | PF | S | at 0.5 kW: i' | P_cu' | PF' | S' |
|---|---|---|---|---|---|---|---|---|
| 12 | 0.209 | 3.88 | 0.151 | 594 | 282 | 182 | 0.166 | 4,107 |
| 16 | 1.065 | 4.70 | 0.498 | 720 | 125 | 36 | 0.506 | 1,059 |
| 20 | 1.131 | 5.26 | 0.471 | 805 | 121 | 34 | 0.477 | 1,118 |
| 24 | 1.034 | 5.52 | 0.413 | 844 | 127 | 37 | 0.420 | 1,277 |
| **26.25** | **1.592** | 6.44 | **0.532** | 986 | 102 | 24 | **0.531** | **986** |
| 28 | 1.510 | 6.67 | 0.488 | 1,021 | 105 | 25 | 0.489 | 1,074 |
| 32 | 0.881 | 6.87 | 0.286 | 1,051 | 137 | 43 | 0.294 | 1,850 |
| 36 | 1.761 | 8.00 | 0.471 | 1,225 | 97 | 22 | 0.469 | 1,112 |
| 40 | 1.351 | 8.27 | 0.354 | 1,267 | 111 | 28 | 0.356 | 1,482 |
| 44 | 0.519 | 8.00 | 0.153 | 1,225 | 179 | 73 | 0.161 | 3,560 |

`PF'`/`S'` are the equal-0.5-kW columns (ESTIMATE: `T ~ J^2`, `lam_par ~ i^0.90`), which
is the only fair comparison - a lower-torque angle has less power, not better PF.

- **A1 regression: PASS.** At 26.25 deg the harness reproduces T = 1.592 N.m (0.0%) and
  PF = 0.532, inside the published bracket.
- **A2: FAIL as declared.** No angle delivers +0.03 PF at >=98% of the target torque;
  26.25 deg is the best measured point on both counts.
- **A3: gain 0.000, far inside the 0.05 bracket width** -> not resolvable as a real gain.

## 3. But A2 is weak evidence, and the reason is worth stating

The torque column is **not physically smooth**: 0.881 at 32 deg then 1.761 at 36 deg.
That is a 100% swing in 4 deg, far beyond the few percent a q = 3 SynRM can ripple. The
torque-extractor check (`validation/torque_extractor`) shows why: a single Maxwell
sampling circle on the coarse mesh scatters by 11%, and the fine mesh moves the operating
point by -9%. The sweep shares that defect.

So the honest reading is:

- **26.25 deg is not beaten by any measured angle**, and it is retained as the operating
  point.
- **The sweep cannot prove it is the true MTPA**, and it cannot resolve a 0.03 PF
  difference. Locating MTPA needs a ring-averaged torque, a finer gap mesh, and
  continuation between angles (start each solve from the previous one, so a saturated
  solve cannot jump to a different flux pattern).
- No angle lever is claimed. **PF is a rotor property** (saliency and saturation), not a
  controller setting - that part of the conclusion stands, because every angle at equal
  output is worse than 26.25 deg by 3% or more.

## 4. What the founder is actually choosing

| option | what it costs | what it needs |
|---|---|---|
| A. Accept 48 V, ~1.0-1.1 kVA, 51-54 A | controller/harness sized for ~1.1 kVA | nothing new; cells stay 13S |
| B. Hold 51 A, accept 454 W (-9% torque) | 9% less shaft power at the same controller | nothing new; restate the spec |
| C. Raise PF by rotor saliency | zero spend, but a new barrier family and re-certification | ~1-2 days of solve time; may not reach 0.65 |
| D. 96 V | 2x cells, 20-turn winding; **S unchanged** | only if current or speed is the binding problem |

D is not a solution to the PF blocker. A and B are the zero-cost choices; C is the only
route that moves S, and it is the one worth funding in compute (not money) if 1 kVA is
unacceptable.

## 5. Not done / limitations

- No cost figures (F-class, D-009): controller and pack prices must be quotes.
- No field weakening modelled; the speed ceilings are voltage ceilings, not torque
  capabilities at speed.
- The equal-output `PF'` column is exponent-scaled, not re-solved; it is an ESTIMATE with
  the same +/-10% extractor uncertainty as the underlying torque.
