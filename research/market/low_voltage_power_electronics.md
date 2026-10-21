# Low-Voltage Traction Power Electronics: Market, Supply, and Entry Analysis

**Scope:** 24–72 V DC traction controllers/inverters for Indian e-2W and e-3W, 0.5–6 kW.
**Prepared for:** Project M1 strategic pivot assessment (design-only, zero-capex team).
**Date:** 2026-10-21. **FX:** ₹94.93/USD (S13).

**Evidence labels used throughout**

- **CONFIRMED** — stated in a primary document (regulator, OEM filing, official release, live listing) and read directly.
- **ESTIMATE** — derived arithmetic, single-marketplace listing, vendor claim, or secondary reporting. Do not quote as fact.
- **UNSOURCED** — asserted in this project or common knowledge, but no dated source was found. Treat as a hypothesis to test.

---

## (a) Market size and price

### Volumes — CONFIRMED

FADA CY2025 retail registrations (S1):

| Segment | CY2025 units | YoY | EV share of segment |
|---|---:|---:|---:|
| Electric 2W | 12,79,951 | +11.36% | 6.31% |
| Electric 3W | 7,97,733 | +15.39% | 60.91% |

Total addressable controller demand: **20,77,684 units/year**, assuming one controller per vehicle. This assumption holds for e-rickshaws and e-2W; it understates nothing material, and overstates only if some 3W use dual motors (not observed in the price listings reviewed).

Note the asymmetry: e-3W is ~62% of the unit pool and already 61% electrified, so its growth is now replacement-driven, not conversion-driven. e-2W is the growth pool but only 6.3% electrified.

### Revenue pool — ESTIMATE

At an assumed OEM transfer price of ₹1,500–3,500 per controller:

> 20,77,684 × ₹1,500 = **₹312 crore**
> 20,77,684 × ₹3,500 = **₹727 crore**

So: **₹310–730 crore/year** of controller revenue in India, at the low-voltage end. Arithmetic checked in `low_voltage_math_check.py`.

Context for how small that is: a single tier-1 (Sona Comstar) books several thousand crore of revenue. A 5% share of this pool is ₹15–35 crore — a viable small company, not a venture-scale outcome. **This is the single most important number in this document.**

### Prices — mixed

Listed retail prices, IndiaMART, read 2026-10-21 (S10). These are *listed* prices, typically ex-GST, negotiable, and not OEM volume prices:

| Product as listed | Price |
|---|---:|
| 48 V DC, 35 A BLDC controller ("Trump") | ₹1,500 |
| 48/60 V controller (generic) | ₹1,680 |
| 40 A sine-wave controller | ₹1,880 |
| 48/60 V, 800–1000 W, 30 A | ₹3,300 |
| 72 V, 2500 W (Okinawa Praise Pro replacement) | ₹3,699 |
| 60 A sine-wave e-scooter/e-motorcycle | ₹6,800 |
| 48 V, 1500 W, with differential | ₹9,700 |
| "Kelly controller supplier in India" | ₹10,550 |

Chinese FOB listings, Alibaba showroom, read 2026-10-21 (S11): 48/60 V 800–1000 W controllers **$5.80–12** at 1,000+ unit MOQ, i.e. **₹551–1,139**.

Landed-cost arithmetic — ESTIMATE:

- HS 8537 10 00 (control boards/panels ≤1000 V — the heading most controller imports are declared under, though classification varies by importer): BCD 15%, SWS 10% of BCD, IGST 18% (S12). Non-recoverable duty = **16.5% of CIF**; IGST is recoverable as input credit. S12 is a customs broker, not the CBIC tariff — verify before modelling.
- ₹551–1,139 × 1.165 = **₹642–1,327** landed, before freight, clearance, and distributor margin.

**Interpretation.** The gap between Chinese landed cost (~₹650–1,350) and Indian listed retail (₹1,500–3,300) is roughly **1.5–2.5×, not 10×**. Once freight, working capital, warranty, and the fact that a ₹650 controller is a 6-MOSFET unsensored square-wave board are accounted for, the cost gap is real but narrow. Anyone claiming Chinese imports make Indian design "uneconomic" is overstating it. The genuine problem is different and worse: **the Indian price is itself set by the imported board.** Every Indian listing above sits just above the landed import cost, which means there is no price umbrella to design under.

---

## (b) Supply landscape

### Indian, motor + controller integrated — CONFIRMED

| Player | Position | Evidence |
|---|---|---|
| **Sona Comstar** | Motor T family with "optimised controller family"; controller platforms <2 kW, ≤5 kW, ≤10 kW; 180,000+ EV traction motors since Nov 2020; claims 96% efficiency for Motor T | S4 (2022-03-23). Efficiency is a **company claim**, not third-party measured |
| **Napino** | Motor controllers 48–72 V, 1.2–5 kW, regenerative braking; also BLDC motors, DC-DC, BMS | S6 |
| **Ather** | In-house "Ather Drive Controller"; ~51% cost reduction on that component attributable to in-house design | S5, p. on BOM reduction |

Ather's 51% is the clearest available signal on where the margin sits: **controller design is high-value, and the value is captured by internalising it.** That is the structural threat to any external design house.

### Indian design services already in this exact niche — CONFIRMED

**eInfochips (Arrow) + Vishay**: scalable low-voltage traction inverter reference design, **36–96 V, 3–15 kW**, modular, targeting 48/72/96 V LEVs, NXP S32K3, ASIL B / IEC 61508 pre-compliance (S7, 2025-07-09). This is an Indian design-services firm with an existing, published, exactly-overlapping offer. Any "we will design LEV inverters" pitch competes with them on day one.

### Imported brands — CONFIRMED presence, prices partly UNSOURCED

Kelly (US/China, 24–144 V), Votol (Taizhou, 48–96 V), Lingbo, Sabvoton, Sevcon/BorgWarner Gen4 (48/80 V MOSFET, 6-switch, 8/12 kHz). These set the performance and features benchmark (FOC, regen, CAN, configurable current limits) at prices Indian generic boards do not match on features.

### Indian EMS capable of building controllers — CONFIRMED capability

Syrma SGS (IATF 16949; explicitly lists "Motor Controller Unit", BMS, VCU, MCU; 39 SMT lines), Avalon (IATF 16949 PCBA), Kaynes, Dixon. A design-only team does not need a factory. This is the one part of the M1 thesis that holds cleanly.

---

## (c) Technical differentiation — what is actually true

### Claim to reject: "48 V is inefficient, so 72/96 V wins"

At fixed power, conduction loss is `I²R`. Raising voltage cuts current and therefore conduction loss quadratically — but the absolute numbers are tiny at these power levels. With a 1.5 mΩ conduction path (two devices in path, four 3 mΩ MOSFETs paralleled per switch):

| Power | 48 V | 60 V | 72 V | 96 V |
|---|---:|---:|---:|---:|
| 1 kW — current | 20.8 A | 16.7 A | 13.9 A | 10.4 A |
| 1 kW — conduction loss | 0.65 W (0.07%) | 0.42 W | 0.29 W | 0.16 W |
| 5 kW — current | 104.2 A | 83.3 A | 69.4 A | 52.1 A |
| 5 kW — conduction loss | 16.3 W (0.33%) | 10.4 W | 7.2 W | 4.1 W |

Switching loss scales as `V·I·f`, which is **flat at fixed power** — raising voltage does not help it. So going 48 V → 96 V at 1 kW recovers about **0.5 W out of 1,000 W**. That is 0.05 percentage points. It is not a product.

The real 48 V penalties are mechanical and thermal, not conversion efficiency:

- 104 A at 5 kW means busbar, connector, and harness cross-section, and I²R in the *cabling*, which is often worse than in the bridge.
- Paralleling 4–6 MOSFETs per switch to spread heat creates current-sharing and body-diode reverse-recovery problems (S8, and TI 48 V app notes).
- Thermal density in a potted, fanless enclosure is the actual design constraint.

**Therefore: efficiency is not a defensible moat in this market, at any voltage in the 24–96 V band.** Any pitch built on "our inverter is 98% efficient" is competing with a claim that is already true of a ₹1,500 board.

### The measured evidence base is genuinely thin — CONFIRMED gap

- TI TIDUCB6 (S8): 48 V, 5 kW forklift inverter, 130 A RMS, ~98% at 8 kHz. This is the best public 48 V data point and it is a **forklift**, not a scooter, and a decade old.
- The most directly-titled Indian paper — "Loss Comparison of GaN, SiC, and IGBT Based Inverters for **Low Voltage High Current Two-Wheeler** EV Applications", IEEE PEDES 2024 (S9) — actually simulates **10 kW at 120 V line-line**. Even the paper that claims this niche does not operate at 48 V.
- No public dataset compares measured 48 V vs 72 V vs 96 V inverter efficiency at 1–10 kW on the same hardware. **UNSOURCED / literature gap.** This confirms M1's `research_gaps.md` item 4 rather than resolving it.

That gap cuts both ways. There is no benchmark to beat, and no benchmark to prove you are better. A design-only team cannot sell "better efficiency" without funding its own measurement campaign — which is cheap (a few lakh of bench equipment) and would itself be a genuine, publishable differentiator.

---

## (d) Entry path, certification, cost, timeline

### The structural opening — CONFIRMED, and it is regulatory, not technical

PM E-DRIVE's Phased Manufacturing Programme for e-2W/e-3W (S2, v9) lists at item 7:

> "**Traction Motor controller including inverter** — Assembly ... which mainly includes assembly of electronic components/semiconductors/connectors on the PCB, wiring, connector fitment, heat-sink fitment, enclosure fitment, software/firmware flashing shall be domestically performed."

And in the notes:

> "Direct or indirect import of finished PMP components or any other vehicle component ... **shall not be permitted**."

And:

> "In the case of integrated unit consisting of multiple PMP components (e.g. 3-in-1 combo unit consisting of DC-DC converter, on-board charger and motor controller including inverter), PMP verification ... shall be carried out **separately for individual PMP component**."

Three consequences, all favourable to a domestic designer:

1. A finished Chinese controller **cannot** go into a PMP-eligible vehicle. The import threat is bounded by policy, not by price.
2. The 3-in-1 combo (DC-DC + OBC + controller) that Chinese suppliers sell as one board must be **unbundled and verified separately** — which favours a specialist controller design.
3. "Software/firmware flashing" being an explicitly domestic step means firmware is a recognised locus of value, not an afterthought.

Caveat: **the notification date from which item 7 is enforced is not in the v9 document** and was not found elsewhere. **UNSOURCED.** Confirm before building a business case on it.

### Certification — the burden is smaller than commonly assumed

A controller sold to an OEM does **not** need vehicle type approval; the OEM holds that (ARAI: full type approval 45 working days, partial 30, documentation 10 — S3, published 2025-09-03). A controller supplier needs:

- **AIS-004 Part 3** EMC (component level)
- Environmental/ingress and vibration to the OEM's DVP (typically IP67, −10 to +55 °C, random vibration)
- **AIS-041** only where net-power declaration is involved; **AIS-156** is the vehicle-level L-category standard, not a controller standard (do not conflate with AIS-038, which is M/N)

Cost: **ESTIMATE and weakly sourced.** No published ARAI/ICAT fee schedule was found. An SEO-tier source quotes ₹3–5 lakh for indicative 2W homologation and ₹50,000–1 lakh for motor+controller testing (npelectronics.net, 2026-05-23) — **treat as an order-of-magnitude guess only.** The defensible statement is: component EMC + environmental validation is **lakhs, not crores**, and 3–6 months of calendar time per test-fix-retest cycle.

### Realistic path (ESTIMATE on timings)

1. **Do not build a 48 V/1 kW generic controller.** The BOM at 1,000 units is roughly ₹1,500–2,500 (6–12 MOSFETs, gate driver, MCU, bus caps, PCB, heatsink, enclosure, connectors); at that volume it cannot undercut a ₹1,500 retail board, and at 100k units it only reaches ~₹900–1,300 — which requires scale a design-only firm does not have. **This is the economic kill-shot on the commodity end.**
2. **Target 72/96 V, 3–6 kW L5 cargo 3W** — where PMP applies, where Chinese boards are weakest on thermal and regen at sustained load, and where 60–100 A is high enough that layout and paralleling actually matter.
3. **Sell design + firmware to one OEM**, manufacture at Napino/Syrma/Avalon under the OEM's PPAP. Revenue = NRE + per-unit royalty, not unit margin.
4. **Build the missing benchmark**: your own 48/72/96 V loss and thermal dataset on one rig. It is the only asset in this space that is both cheap to produce and genuinely absent (see (c)).

Timeline to SOP: design 6–9 months, EMS NPI 3–4, EMC + validation 3, OEM PPAP 3 → **12–18 months**, overlapping.

---

## (e) Verdict: controller vs motor accessibility

**The controller is dramatically more accessible than the motor — and still a hard business.**

**Why accessible (relative to M1's motor effort):**

- No magnets, no torque-density physics problem (D-012 does not apply), no winding, no factory. The entire product is a PCB, firmware, and a thermal design.
- The market is 2.08M units/year with an existing, IATF-certified EMS base to build it.
- Policy actively excludes the finished-import competitor for PMP-eligible vehicles (S2).
- The technical barrier at 1 kW is low enough that a competent firmware/analog team can reach a working prototype in months, not years.

**Why it is still hard:**

- **The price is set by a ₹650 imported board.** There is no umbrella. Retail Indian listings cluster at ₹1,500–3,300 precisely because that is what the landed import plus a margin costs.
- **Efficiency is not a differentiator** (section c). Neither is "FOC" — it is table stakes on a ₹1,880 board.
- **OEMs internalise the design when it matters** — Ather's 51% saving (S5) is the proof. The best customers are the ones most likely to do it themselves.
- **eInfochips/Vishay already occupy the "Indian design house for 36–96 V LEV inverters" slot** with a published ASIL B reference design (S7).
- **The revenue pool is ₹310–730 crore for the entire country.** Even dominant share is a modest company.

**Bottom line.** For a zero-capex, software-led team, the controller is the *only* tractable hardware pivot in this project — the motor is blocked by physics and capex, the controller is blocked only by incumbents and price. That is a much better problem. But the winning position is **not** "cheaper 48 V controller". It is **"the 72/96 V, 3–6 kW, thermally-honest, PMP-compliant controller design partner for one or two 3W OEMs, with the measurement data nobody else has."** If the team cannot name the OEM and the voltage class, it should not build the board.

---

## (f) Unknowns

Ranked by how much they would change the answer.

1. **Enforcement date of PMP item 7.** If already enforced, the import competitor is legally excluded and the entire analysis improves. If deferred to 2027+, the window is narrower. Not found in S2 — **UNSOURCED**. Highest-value thing to confirm.
2. **Actual OEM transfer prices.** All Indian prices here are *listed retail*. OEM volume prices could be ₹900–1,400, which would make the BOM arithmetic in (d) fatal rather than merely difficult. Needs 2–3 supplier quotes.
3. **Whether Chinese controllers are already being imported at scale for non-subsidised vehicles.** If e-rickshaw assemblers (outside PM E-DRIVE) are importing finished boards, the addressable market is smaller than 2.08M.
4. **Measured 48/72/96 V efficiency and thermal data at 1–10 kW.** Confirmed absent from public literature (S9 is 120 V; S8 is a forklift). Either a gap to fill or a reason the segment is under-engineered.
5. **Warranty/field failure rates** for Indian vs imported controllers in e-rickshaw duty (high load, dust, 45 °C ambient, abuse). This, not efficiency, is where a design house could actually win — and no public data exists. **UNSOURCED.**
6. **Certification cost and schedule at ARAI/ICAT** for a controller-only programme. No official fee schedule found; the ₹3–5 lakh figure is a weak secondary source.
7. **Whether a royalty model is acceptable to Indian OEMs at all.** Ather, Sona, and Napino all internalise; the market may have no appetite for externally-licensed controller IP regardless of quality.

---

## Sources

| ID | Source | Date | URL |
|---|---|---|---|
| S1 | FADA, "CY 2025 and December 2025 Vehicle Retail Data" (PDF) | 2026-01 | https://fada.in/images/press-release/1695cc82c07602FADA%20releases%20CY%202025%20and%20December%202025%20Vehicle%20Retail%20Data.pdf |
| S2 | MoHI, PMP for EVs under PM E-DRIVE, e2W/e3W incl. e-rickshaw, v9 (PDF) | 2024-10-11 | https://pmedrive.heavyindustries.gov.in/docs/policy_document/PMP%20PM%20E-DRIVE%20-%20e2W%20and%20e3W%20V9.pdf |
| S3 | ARAI, Vehicle Type Approval timelines | 2025-09-03 (mod. 2026-04-01) | https://www.araiindia.com/certification/certification/vehicle |
| S4 | Sona Comstar, "Motor T" press release, NSE archive (PDF) | 2022-03-23 | https://archives.nseindia.com/corporate/SONACOMS_23032022214535_SonaComstarMotorT.pdf |
| S5 | Ather Energy DRHP (Yes Securities), BOM/cost section | 2024-09-17 | https://images.assettype.com/bloombergquint/2024-09-17/dy1cr6c5/Yes_Securities_Ather_Energy_DRHP.pdf |
| S6 | Napino Auto & Electronics, e-mobility | undated, read 2026-10-21 | https://www.napino.com/e-mobility |
| S7 | eInfochips + Vishay, scalable LEV traction inverter reference design (36–96 V, 3–15 kW) | 2025-07-09 | https://www.einfochips.com/scalable-traction-inverter-reference-design-for-light-electric-vehicles/ |
| S8 | TI, TIDUCB6 — 48 V, 5 kW inverter design | 2016-10 | https://www.ti.com/lit/pdf/tiducb6 |
| S9 | Suyal, Dutta, Yadav, "Loss Comparison of GaN, SiC, and IGBT Based Inverters for Low Voltage High Current Two-Wheeler EV Applications", IEEE PEDES 2024 | 2024 | https://doi.org/10.1109/PEDES61459.2024.10961671 |
| S10 | IndiaMART, BLDC motor controller category listing | read 2026-10-21 | https://dir.indiamart.com/impcat/bldc-motor-controller.html |
| S11 | Alibaba, 48 V 1000 W controller showroom | read 2026-10-21 | https://www.alibaba.com/showroom/48v-1000w-electric-bike-controller.html |
| S12 | ImportsFromChina, HS 8537 10 00 duty breakdown (BCD 15%, SWS 1.5%, IGST 18%) | FY2026-27 | https://importsfromchina.com/hs-code/85371000-control-panel-switchboard-up-to-1000-v/ |
| S13 | Frankfurter, USD/INR reference rate 94.93 | 2026-10-20 | https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR |
| S14 | 3Shul Motors (Ahmedabad) — Indian performance controller maker, no public price list | read 2026-10-21 | https://3shulmotors.com/ |

**Notes on sources.** S10/S11 are live marketplace pages: prices change and listings are not contractual. S4's 96% is a company claim. S5's 51% is a company filing describing its own cost reduction, not an audited figure. S12 is a commercial customs broker, not the CBIC tariff itself — the 15% BCD is consistent with the FY26-27 structure but should be re-checked against the tariff before use in a financial model.
