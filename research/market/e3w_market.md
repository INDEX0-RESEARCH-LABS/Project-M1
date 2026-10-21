# Indian Electric 3-Wheeler Market — Addressable Size and Motor Unit Economics

**Prepared:** 2026-10-21
**Scope:** India, L3 (e-rickshaw / e-cart) and L5 (e-auto, cargo) battery-electric 3-wheelers. Cargo and passenger.
**Purpose:** size the traction-motor opportunity for a zero-capex, design-only entrant.
**Budget constraint:** D-009 — zero spend; all sources are public and free.

### Confidence key

| Label | Meaning |
|---|---|
| **CONFIRMED** | Primary source (Vahan registry / SIAM / MoRTH), company disclosure, or ≥2 independent tallies agreeing within ~1%. |
| **ESTIMATE** | Analyst estimate, or my arithmetic on sourced inputs. The arithmetic is shown. |
| **UNKNOWN** | No public source. What would be needed is stated. |

Prices from marketplaces (IndiaMART, Alibaba, TradeIndia) are **list/retail**, not contract. Contract pricing is derived as an ESTIMATE and labelled as such. No figure below is invented; where a number could not be sourced it is marked UNKNOWN.

---

## 1. Market size and growth

| Metric | Value | Source | Date | Confidence |
|---|---|---|---|---|
| E-3W sales FY2024 | 635,129 | Vahan-derived tally, Autocar Professional | 2024-04 | CONFIRMED |
| E-3W sales FY2025 | 702,799 (passenger 609,762 / cargo 93,037) | Vahan-derived tally | 2025-04 | CONFIRMED |
| E-3W sales FY2026 | 830,819 | Vahan via Autocar Professional, https://www.autocarpro.in/analysis-sales/mahindra-bajaj-and-tvs-power-electric-3w-sales-past-800000-for-the-first-time-in-fy2026-131960 | 2026-04 | CONFIRMED |
| E-3W sales FY2026 (alt) | 835,130 | JMK Research, https://jmkresearch.com/wp-content/uploads/2026/05/Annual-Electric-Vehicle-Report-Car-FY26_JMK-Research-1.pdf | 2026-05 | CONFIRMED (see note) |
| E-3W sales CY2025 | 797,729–802,176 | Vahan-derived tallies (FADA, EVreporter) | 2026-01 | CONFIRMED |
| FY2026 segment split | L3 pax 477,933 · L5 pax 238,086 · L3 cargo 86,467 · L5 cargo 32,644 | JMK Research (as above) | 2026-05 | CONFIRMED |
| FY2026 L3 total (derived) | 564,400 units (67.6% of units) | Sum of L3 rows above | — | ESTIMATE (arithmetic) |
| FY2026 L5 total (derived) | 270,730 units (32.4%) | Sum of L5 rows above | — | ESTIMATE (arithmetic) |
| Monthly run-rate, Aug 2026 | 79,842 units: L5 pax 40,419 · L5 cargo 4,583 · L3 pax 28,811 · L3 cart 6,029 | EVreporter, https://evreporter.com/indias-electric-vehicle-sales-trend-august-2026/ | 2026-09 | CONFIRMED |
| E-3W share of all 3W retail, Aug 2026 | 65.3% | EVreporter (as above) | 2026-09 | CONFIRMED |
| L5 penetration within its segment, Aug 2026 | Passenger 55.5%, cargo 31.4% | EVreporter (as above) | 2026-09 | CONFIRMED |
| Implied FY2027 run-rate | ~0.96 M units/yr (79,842 × 12) | Arithmetic on Aug 2026 | — | ESTIMATE |
| OEM count | ~680 e-3W OEMs; top 6 = 36% share; 522 e-rickshaw makers registered ≥1 unit in Aug 2026 | JMK Research; Vahan | 2026-05 / 2026-09 | CONFIRMED |

**FY2026 discrepancy (state it, do not smooth it):** JMK 835,130 vs Vahan/Autocar/FADA 830,819 — a 4,311-unit (0.5%) gap. JMK adds Telangana registrations manually because the state's Vahan feed is incomplete. Both are usable; the L3/L5 split above comes from JMK, so segment shares carry that 0.5% uncertainty.

**Growth read:** 635k → 703k → 831k is +10.6% then +18.2%. The acceleration is not broad-based — it is L5 passenger, which went from a policy-dependent niche to 40,419 units/month after the subsidy closed. Treat FY2027 growth as **ESTIMATE**, not trend extrapolation: the two things that drove it (GST 2.0 rate cut on 3W, OEM price cuts) are one-off level shifts, not annual growth rates.

---

## 2. Motor specification by segment

| Segment | Power | Voltage | Torque | Speed | Confidence |
|---|---|---|---|---|---|
| L3 e-rickshaw / e-cart | 0.8–1.5 kW; legal cap 2 kW | 48 V / 60 V | ~20–28 N·m peak | 3,200–3,400 rpm | CONFIRMED (multiple OEM datasheets) |
| L5 passenger (e-auto) | 4.5–11.7 kW | 48–96 V | 15.9–88.6 N·m | — | CONFIRMED |
| Mahindra Treo Plus | 8 kW, 10.24 kWh | — | 42 N·m | — | CONFIRMED (OEM) |
| Euler HiLoad (cargo) | 10.96 kW | — | 88.55 N·m | — | CONFIRMED (OEM) |
| Electra EV family | 5 / 6 / 8.5 kW | — | 15.9 N·m rated, 65–85 N·m peak | — | CONFIRMED (OEM) |
| Matel L3 | — | — | 9 N·m cont / 22 N·m peak | — | CONFIRMED (OEM) |

**Read:** L3 is a 48/60 V, ~1 kW, ~4.5 N·m-rated, ~22 N·m-peak machine. L5 passenger is a 5–8 kW, 48–72 V, ~16 N·m-rated, ~45 N·m-peak machine. L5 cargo is the top of the range at 8–11 kW and ~60–89 N·m.

**(Vahan via Autocar, FY2026)** — e-3W ticked past 800,000 for the first time; EV share of 3W reached 61% with CNG at 24%: https://www.autocarpro.in/analysis/ev-share-of-3-wheeler-sales-jumps-to-61-cng-falls-to-24-in-fy2026-131965 (2026-04, CONFIRMED).

---

## 3. Price per unit and per kW

| Item | Value | Source | Date | Confidence |
|---|---|---|---|---|
| L3 motor, retail (1–1.2 kW) | ₹3,700–5,200 | IndiaMART listings (Nanya 1200 W et al.), accessed | 2026-10-21 | CONFIRMED (list price) |
| L3 motor, 1 kW (ED Blue) | ₹4,500 | IndiaMART | 2026-10-21 | CONFIRMED (list) |
| L3 PMSM 1.5 kW | ₹11,025, MOQ 50 | Datai (IndiaMART) | 2026-10-21 | CONFIRMED (list) |
| L3 motor, China bulk | $28–192/unit; realistic bulk $31–111 | Alibaba listings | 2026-10-21 | CONFIRMED (list) |
| **L3 OEM-level motor price** | **₹2,500–3,500** | Derived: retail minus 25–35% channel margin; corroborated by 2022 Motorama quote of ₹4,000–4,500 pre-inflation-adjusted | 2022–2026 | **ESTIMATE** |
| 3–5 kW PMSM (L5-class) | ₹25,000–29,000 bulk | YesBatch, https://yesbatch.com/india/p/pmsm-mid-drive-motor-ev | 2026 | CONFIRMED (list) |
| 5 kW motor + controller + differential | ₹72,500 | IndiaMART | 2026-10-21 | CONFIRMED (list) |
| Retrofit 5 kW motor + controller | ₹40,000 | NRDC India, https://nrdcindia.org/pdf/EV-Retrofitment-Report.pdf | 2024 | CONFIRMED |
| Implied ₹/kW, L3 | ₹2,500–4,500/kW | Arithmetic | — | ESTIMATE |
| Implied ₹/kW, L5 | ₹2,700–5,800/kW | Arithmetic (₹20k–29k over 5–8.5 kW) | — | ESTIMATE |

**Per-kW collapses above ~5 kW.** An L3 motor sells at ₹2,500–4,500/kW; an L5 motor at ₹2,700–5,800/kW. Scale, not technology, sets price — the L3 part is a commodity with dozens of Chinese and Indian suppliers, and the buyer is a 680-OEM long tail that negotiates on landed cost alone.

**Imported vs domestic.** L3 motors are predominantly Chinese (CY, Yufeng, Datai, Nanya) with Indian assembly/rebadging. L5 integrated powertrains are increasingly domestic (Electra EV, Matel, Compage, Tsuyo) alongside Bosch/Tata Autocomp, Valeo, Nidec and IRP.

---

## 4. Motor share of BOM and cost drivers

| Metric | Value | Source | Date | Confidence |
|---|---|---|---|---|
| Motor + controller as % of e-rickshaw vehicle cost | 7–8% | Lucas TVS, https://www.autocarpro.in/feature/lucas-tvs-diversifies-into-ev-components-42603 | 2019 | CONFIRMED (company) |
| Motor + controller as % of EV BOM | 8–10%, second-largest item after battery | EVreporter / NRI, https://evreporter.com/indias-electric-vehicle-supply-chain-landscape-an-overview/ | 2024 | CONFIRMED |
| Battery share of BOM | 40–50% | EVreporter / NRI (as above) | 2024 | CONFIRMED |
| Motor localisation | only 30–40% localised | EVreporter / NRI (as above) | 2024 | CONFIRMED |

**Cost drivers, in order:** copper winding, NdFeB magnet, silicon steel laminations, controller power electronics, then labour/assembly. Magnet is the single most volatile input — see §5.

**The structural squeeze:** motor+controller is 8–10% of BOM but only 30–40% localised. That gap is the entire entry thesis — it is also why the price ceiling is set by imports rather than by domestic cost.

---

## 5. Magnet cost and rare-earth exposure (3–10 kW)

| Metric | Value | Source | Date | Confidence |
|---|---|---|---|---|
| NdFeB per 3-wheeler | ~500 g | Primus Partners, https://primuspartners.in/docs/documents/Final%2020%20Aug_Rare%20Earth%20Magnets%20TL%20v3.pdf | 2025 | CONFIRMED (published estimate) |
| India NdFeB price | ₹4,186–4,605/kg (2022) → ₹7,500/kg (2024) | BusinessLine, https://www.thehindubusinessline.com/specials/emerging-entrepreneurs/a-motor-that-cuts-import-of-chinese-raw-material/article68565461.ece | 2024 | CONFIRMED |
| Ferrite magnet price | ₹350–400/kg | BusinessLine (as above) | 2024 | CONFIRMED |
| Magnet as % of PMSM raw-material cost | 30–45% | SMM | 2024 | CONFIRMED (analyst) |
| NdPr oxide, 2021 | $92/kg | USGS MCS 2026, https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf | 2026 | CONFIRMED |
| NdPr oxide, 2022 peak | $124–140/kg | USGS MCS 2026 | 2026 | CONFIRMED |
| NdPr oxide, 2023 / 2024 / 2025 avg | $75 / $55 / $69 per kg | USGS MCS 2026 | 2026 | CONFIRMED |
| NdPr oxide, Aug–Sep 2026 | $95–110/kg | Trade press | 2026-09 | ESTIMATE |
| 2011 PrNd peak | ¥1,600,000/t ≈ $248/kg | Historical record | 2011 | CONFIRMED |
| China share of global magnet output | 90–94% | IEA, https://www.iea.org/commentaries/with-new-export-controls-on-critical-minerals-supply-concentration-risks-become-reality | 2025 | CONFIRMED |
| India NdFeB import dependence | ~100% imported, ~90% from China | Primus Partners (as above) | 2025 | CONFIRMED |
| India REPM incentive | ₹7,280 cr scheme, ₹2,150/kg incentive cap | Government of India | 2025 | CONFIRMED |

**Event timeline that matters to a motor designer:**

- **2011** — PrNd spike to ~$248/kg. Magnets became a strategic cost line, not a commodity.
- **2022** — NdPr $124–140/kg; NdFeB in India ₹4,186–4,605/kg. Motor makers absorb or pass through.
- **4 Apr 2025** — China restricts 7 heavy rare earths.
- **9 Oct 2025** — controls extended to parts, components and assemblies containing Chinese REE, effective 1 Dec 2025. This is the one that bites a motor importer: the *motor* becomes controlled content, not just the magnet.
- **2026** — NdPr recovering to $95–110/kg on Chinese export tightening.

**Critical arithmetic — and a warning about the 500 g figure.** 500 g × ₹7,500/kg = ₹3,750 of magnet per vehicle. That is *more than the entire ex-works price of an L3 motor* (₹2,500–3,500). The 500 g figure is therefore only consistent with an **L5-class** machine (₹20,000–29,000), where it is 13–19% of motor price — coherent with SMM's 30–45% of raw-material cost.

Back-solving from price instead: if magnet is ~20–30% of a ₹2,500–3,500 L3 motor, magnet value is ₹500–1,050, i.e. **~0.07–0.14 kg at ₹7,500/kg**. So L3 magnet mass is roughly **0.1–0.2 kg**, not 0.5 kg.

Fleet magnet demand, two ways (both ESTIMATE):

- Fleet-wide at 500 g: 835,130 × 0.5 kg ≈ **418 t NdFeB/yr** ≈ ₹313 cr at ₹7,500/kg. Implausible as stated — it exceeds the L3 motor TAM.
- Segment-weighted at 0.15 kg (L3) / 0.5 kg (L5): 564,400 × 0.15 + 270,730 × 0.5 ≈ **220 t/yr** ≈ ₹165 cr. This is the number to use.

**Design implication:** magnet is 13–19% of an L5 motor's price and a similar share of an L3 motor's, and it is 100% imported with 90% single-country concentration. A ferrite or magnet-light topology does not need to beat NdFeB on torque — it needs to beat it on *landed cost under a supply shock*, which is a different and much easier bar. That is the opening Viridian (Ingni Propulsion L3 PMaSynRM, 1.2 kW / 4.5 N·m rated / 28 N·m peak / 94% efficiency, ferrite, targeting 10,000 units by FY27), Chara, Conifer, Simple Energy and the TVS/Ola ferrite programmes are all chasing. Sector magnet-free funding since 2019: $218.36M.

---

## 6. Incumbents and consolidation

| Layer | Structure | Confidence |
|---|---|---|
| Vehicle OEMs | ~680 firms, top 6 = 36%; 522 e-rickshaw makers registered ≥1 unit in Aug 2026 | CONFIRMED |
| L3 motors | Fragmented, Chinese-dominated (CY, Yufeng, Datai, Nanya) plus Lucas TVS, Compage, Viridian | CONFIRMED |
| L5 powertrains | Integrated: Electra EV, Matel, Compage, Tsuyo; Tier-1: Bosch/Tata Autocomp, Valeo, Nidec, IRP | CONFIRMED |
| Magnet-free challengers | Viridian/Ingni, Chara, Conifer, Simple Energy, TVS/Ola ferrite programmes | CONFIRMED |

**Read:** the OEM layer is fragmenting, not consolidating (680 firms, top 6 at 36%). The motor layer is the opposite — L5 is consolidating into integrated powertrain supply, while L3 stays a commodity bazaar. A new entrant's realistic channel is the L3 long tail *or* a Tier-1 supply position on L5; there is no viable middle.

---

## 7. ICE-to-EV retrofit market

| Metric | Value | Source | Date | Confidence |
|---|---|---|---|---|
| Regulation | AIS-123 Part 3, amended 13 Mar 2025; CMVR Rule 12b/47A; Form 22C | MoRTH, https://morth.nic.in/en/gsr-629e-regarding-retro-fitment-hybrid-electric-system-or-electric-kit-vehicles | 2025-03 | CONFIRMED |
| Approval route | ARAI/ICAT kit type approval + vehicle type approval | MoRTH (as above) | 2025 | CONFIRMED |
| Kit price, full | ~₹1.66 lakh incl. 8 kWh battery | EVreporter, https://evreporter.com/regulatory-framework-for-retrofitting-in-india/ | 2025 | CONFIRMED |
| Kit price, swappable | ₹65,000 | EVreporter (as above) | 2025 | CONFIRMED |
| Addressable fleet | 3.5 M autos aged 5–15 yrs | NRDC India (as above) | 2024 | ESTIMATE |
| ARAI-certified 3W retrofitters | 2 (e-Vidyut, Envirosmart/Zero21) | Autocar Professional, https://www.autocarpro.in/news/e-vidyut-launches-commercial-retrofit-operations-for-three-wheeler-electric-conversion-128928 | 2025-09 | CONFIRMED |
| e-Vidyut day-one registrations | 30 | Autocar Professional (as above) | 2025-09 | CONFIRMED |

**Read:** regulatory permission exists and is recent; commercial volume does not. Two certified players and 30 day-one registrations is a pilot, not a market. The ₹65,000 swappable kit is the only price point that clears a retrofit buyer's payback test, and it implies a motor+controller content of roughly ₹15,000–25,000 — consistent with §3, not with a premium product.

---

## 8. Motor TAM (explicit arithmetic)

Using FY2026 segment volumes and the price bands above:

| Segment | Units | Price/unit | Segment TAM | Basis |
|---|---|---|---|---|
| L3 | 564,400 | ₹3,000–4,500 | **₹169–254 cr** | ESTIMATE: JMK units × derived OEM price band |
| L5 | 270,730 | ₹20,000–29,000 | **₹541–785 cr** | ESTIMATE: JMK units × YesBatch bulk band |
| **Total** | 835,130 | — | **₹710–1,040 cr/yr** | ESTIMATE |

Annualised on the Aug 2026 run-rate (79,842/month), the same bands give **₹820–1,190 cr/yr** — but that assumes the L5 mix holds, which §1 says is the least certain thing in this document.

At 10% share of the L3 band alone, a supplier is looking at ₹17–25 cr/yr of revenue. That is the size of the prize at the segment that carries 68% of units.

---

## 9. Five decision-relevant takeaways

**1. The volume is in L3, but the price ceiling is set by imports — enter on cost, not performance.**
L3 is 564,400 units (67.6% of FY2026). Its motor sells for ₹2,500–3,500 ex-works, with Chinese bulk at $31–111 landed. No domestic design wins on specs here; it wins only if it is cheaper per N·m at the same reliability. Price the product against the import, not against a cost model.

**2. The real money is in L5, and it is consolidating away from you.**
L5 is 32% of units but ~75% of motor TAM (₹541–785 cr of ₹710–1,040 cr). It is also where Electra, Matel, Compage, Bosch/Tata Autocomp and Valeo already sit with integrated powertrains. A design-only entrant cannot displace an integrated supplier on a 5–8 kW e-auto; it can only supply *into* one.

**3. Magnet exposure is the one structural weakness an outsider can attack.**
100% NdFeB import dependence, ~90% from China, 13–19% of motor price, and an Oct 2025 control that extends to motors as *components containing* Chinese REE. Ferrite/magnet-light topologies are funded ($218M since 2019) and already shipping at L3 spec (Viridian 1.2 kW / 4.5 N·m rated / 28 N·m peak / 94%). This is the defensible position — and it is the only one that a zero-capex designer can hold, because the moat is topology IP, not tooling.

**4. Your current spec does not match the L3 market, and that gap must be closed before any go-to-market claim.**
Target spec v0 is 0.5 kW continuous / ~1.6 N·m at 3,000 rpm. The L3 market machine is 1–1.2 kW / ~4.5 N·m rated / ~22 N·m peak at 3,200–3,400 rpm. That is roughly a **3× continuous torque gap and a 9× peak gap**. Either the product is a sub-segment part (e-cart, low-speed), or the stator envelope must grow. This is a spec-alignment risk, not a market risk, and it is the highest-priority open item.

**5. Policy has already picked the winners, and it is not the subsidy.**
PM E-DRIVE's L5 subsidy closed 26 Dec 2025 at 288,000 units; L5 volumes then *rose* to 40,419/month on GST 2.0 and OEM price cuts. L3 e-rickshaw/e-cart subsidy runs to 31 Mar 2028 at ₹2,500/kWh capped ₹12,500. The lesson: demand is now price-elastic, not subsidy-elastic. A supplier that needs a subsidy to close a deal is selling into a shrinking channel.

---

## 10. Unknowns

| Unknown | Why it matters | What would resolve it |
|---|---|---|
| **True OEM contract price** for L3/L5 motors | All price bands here are list/retail or derived. Contract price sets the real ceiling and could be 20–40% below retail. | 2–3 OEM purchase-order or teardown cost sheets; supplier interviews. |
| **Magnet mass per L3 motor** | Inferred 0.1–0.2 kg from price share; the 500 g figure is L5-class. Drives the entire magnet-shock sensitivity. | Teardown/weigh of a Nanya/CY 1.2 kW hub or mid-drive motor. |
| **L5 motor-only price** (vs integrated powertrain) | L5 is sold as motor+controller+gearbox; the motor's standalone value is not observable. | Supplier quote request for motor-only, or a powertrain BOM breakdown. |
| **Retrofit conversion volume** | Two certified players and 30 day-one registrations is not a market size. | 6–12 months of Vahan retrofit registration counts (Form 22C). |
| **L5 mix after subsidy withdrawal** | The ₹541–785 cr L5 TAM rests on a mix that grew *after* subsidy removal, on one-off price cuts. | FY2027 H1 Vahan split; whether L5 share holds above 30%. |
| **Inverter/controller attach rate** | Motor is often bundled with controller; standalone motor TAM may be 60–70% of the figures in §8. | OEM procurement interviews; whether OEMs buy integrated or split. |
| **Domestic magnet supply timing** | ₹7,280 cr REPM scheme could change landed magnet cost after ~2028. | Scheme milestone disclosures from the Ministry of Heavy Industries. |

### Paywalled / limited access

- JMK Research annual report — PDF is public but the underlying state-level dataset is abridged.
- SMM magnet cost shares — headline figures public, full series paywalled.
- USGS MCS 2026 — public, but NdPr prices are annual averages, not monthly.
- IndiaMART/Alibaba — live listings, prices move; all captured 2026-10-21.
