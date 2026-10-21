# RESULT - first-order iron loss at 130/50 (gates in PLAN.md)

**Script:** `simulation/scripts/iron_loss.py` (log `/tmp/opencode/m1/iron_loss.log`).
**Status:** ESTIMATE (band, not a measurement). Zero spend.

## 1. Gates

| gate | result |
|---|---|
| F1 stator volume vs (annulus - slots) | **PASS**, -0.0% (both current levels) |
| F2 B^n scaling of the functional | **PASS**, exact for n = 1.6 / 1.8 / 2.0 |
| F3 report min/max band, not a point | **PASS** (27 combos) |
| F4 interpretation rule declared in PLAN | ratio lands in the **second** branch (0.33-0.91) after the addendum-9 copper correction; see s.4 note - the branch's "80-85%" text was written against the superseded 53 W copper loss |

## 2. Field state (130 mm bore, 50.4 mm stack, delta = 26.25, M-43 bracket)

| J | region | mass | B mean | B p95 | B max |
|---|---|---|---|---|---|
| 5.34 | stator iron | 4.77 kg | 0.46 T | 0.86 T | 1.42 T |
| 5.34 | rotor iron | 4.14 kg | 0.54 T | 1.71 T | 2.73 T |
| 6.00 | stator iron | 4.77 kg | 0.51 T | 0.95 T | 1.46 T |
| 6.00 | rotor iron | 4.14 kg | 0.58 T | 1.73 T | 2.80 T |

The stator is **lightly fluxed** (mean 0.46 T, peak 1.42 T): this frame is oversized for
the torque, which is why its iron loss is small. The rotor's high B is confined to the
bridges/webs (p95 1.71 T on 4.14 kg of rotor mass), not distributed.

## 3. Iron loss at 100 Hz (electrical), 27-combo band

Band inputs: p_ref 3.3 / 4.0 / 5.3 W/kg (M350/400/530-50A guarantee at 1.5 T, 50 Hz),
n 1.6 / 1.8 / 2.0, eddy fraction at 50 Hz 0.30 / 0.45 / 0.60.

| point | min | median | max | P_fe/P_cu |
|---|---|---|---|---|
| 1.6 N.m (J=5.34) | 8.4 W | **13.5 W** | 23.4 W | 0.33-0.91 |
| 2.0 N.m (J=6.0) | 10.4 W | 16.7 W | 27.9 W | 0.32-0.85 |

Central combo (4.0 W/kg, n=1.8, s=0.45): **13.3 W**, split stator 8.4 W / rotor 5.0 W.

## 4. Efficiency

| point | copper-only | + iron (median) | band |
|---|---|---|---|
| 1.6 N.m | 95.1% | **92.7%** | 91.1-93.7% |
| 2.0 N.m | 95.1% | 92.8% | 91.3-93.7% |

Adding iron loss to the lumped thermal model (all loss charged to the winding, which is
conservative because iron loss is distributed in the core): target **~39 W total, ~15 K**
enclosed; margin point ~49 W, ~19 K. The "comfortable enclosed" conclusion stands.

> **Note on F4 (post hoc).** The declared rule described the ratio branches using the then
> current copper loss (53 W). After addendum 9 corrected the copper loss to 25.6 W the ratio
> is 0.33-0.91, i.e. iron is comparable to copper, but the efficiency consequence the rule
> predicted for that branch (80-85%) does not follow - it assumes the superseded baseline.
> The *intent* of the gate (does iron loss break the efficiency story?) is answered: no,
> it costs ~2.4 points from 95.1% copper-only. Recorded rather than retro-fitted.

## 5. What this does NOT include (declared, not hidden)

1. **Rotor slot-harmonic loss.** The 5.0 W rotor figure is a 100 Hz fundamental upper
   bound. In the rotor frame the fundamental flux is quasi-static; the real rotor loss is
   driven by slot-harmonic ripple at 36 x 50 = **1800 Hz**. With eddy scaling f^2 that term
   can be comparable or larger, but it is concentrated in the small high-B bridge volume.
   **This is the dominant remaining uncertainty in the efficiency claim.**

   Scoping arithmetic (ASSUMED ripple, not measured): a 2 mm surface layer of the rotor is
   0.32 kg; at s=0.45 and 1800 Hz the loss is 1037 W/kg per T^2 of rms ripple, so a
   0.05-0.10 T ripple gives **0.8-3.3 W**. That is small against 500 W, but the ripple
   amplitude has not been extracted from a field solution and a time-domain eddy solve is
   the only way to settle it. Do not quote this range as a result.
2. Excess (anomalous) loss, rotational loss and the building/lamination factor
   (typically +20-40% on Epstein data) are absent, so the band is a **lower bound** on the
   assembled core's contribution.
3. Steel grade is a class proxy (M-43 vs M350/400/530-50A). A real number needs the
   purchased steel or a bench test (F-class, D-009).

## 6. Conclusion

Efficiency with iron is **92.7% (91.1-93.7%)** at the target, not 95.1% copper-only.
That is good for a 0.5 kW machine, but it is bought with size: the frame carries 8.9 kg of
iron (56 W/kg of active iron), consistent with the certified 0.43 torque utilization.
The efficiency gap is closed to within the steel-uncertainty band; the remaining
unquantified term is rotor harmonic loss.

## 7. Honest correction made during this analysis

The first run used 50 Hz as the electrical frequency (it is the *mechanical* frequency at
3000 rpm; f_e = 100 Hz) and produced 3.2-7.3 W. That log is kept and the run is discarded;
the plan was corrected before any number was published. Effect: iron loss is ~2.9x the
first pass and the efficiency claim moved 95.1% -> 92.7% (addendum 9 then cut the copper
loss in half, so both of those figures replaced an earlier 90.4% / 88.2% pair).
