# Project M1 — Where the money is, and how to win

**Date:** 2026-10-21 · **Basis:** four sourced deep-research passes in this directory
(`e3w_market.md`, `motor_supply_landscape.md`, `low_voltage_power_electronics.md`,
`funding_and_revenue_routes.md`). Prices below are **asking prices unless marked contract**;
every unverified item is listed in §6.

## 1. Verdict in four lines

1. **Do not compete on a 0.5–1 kW motor.** It is a commodity at ₹3,200–5,100/kW with a
   ₹2,749/kW Chinese import floor (FOB, MOQ 200). M1's certified point (1.84 N·m cont,
   ESTIMATE) is 2.5× short of the L3 market machine anyway.
2. **Magnet-free is already occupied** at 2W/3W: Chara, Conifer, Sona Comstar, Ola,
   Simple Energy, Sterling/AEM are funded and OEM-engaged. It is not a white space.
3. **The one attackable weakness is regulatory, not technical:** 100% NdFeB import
   dependence (~90% China, 13–19% of motor price), and Oct-2025 Chinese controls reach
   *motors as components containing* Chinese REE. Domestic-content rules now also exclude
   imported traction controllers (PM E-DRIVE PMP v9, item 7 + Note 5).
4. **M1's only sellable asset today is the certified toolchain and the labelling
   discipline.** Sell that first; it invoices in weeks, not grant cycles.

## 2. Win thesis

> Win the **regulated domestic-content niche at 3–6 kW**, not the commodity 1 kW hub.
> Enter as a **design partner** (paid analysis → controller co-design → motor IP license),
> never as a motor factory.

The motor at 1 kW has no moat. A **domestic** 72/96 V, 3–6 kW controller for L5 cargo 3W
does — because the regulator removed the import competitor. That is the rare case where
an Indian entrant wins without a price advantage.

## 3. The three wedges, ranked by time-to-cash

| # | Wedge | Cash | Time | Evidence | Main risk |
|---|---|---|---|---|---|
| 1 | **Paid design/validation audit** — sell the certified FEA + thermal + optimization chain (motor or controller) to Indian OEMs/tier-1s/startups | ₹75k–5 L/engagement | **2–6 weeks** | `funding_and_revenue_routes.md` §3 | Demand is relationship-led; needs a portfolio sample |
| 2 | **Domestic 72/96 V, 3–6 kW controller co-design** with one named L5 cargo OEM | Design fee + per-unit royalty | 3–9 months | PM E-DRIVE PMP v9 excludes imported finished controllers | Enforcement date unknown; OEMs may internalise (Ather, Sona, Napino do) |
| 3 | **Magnet-free motor IP at 3–10 kW e-3W / 10–30 kW LCV** — where magnets are 13–19% of BOM and demag margin bites | License / royalty | 9–18 months | `e3w_market.md` §3; Sona validated LCV design but announced no production | Torque-density wall (0.64 vs ~2.5 kPa) is unfixed; needs the 2-pole/4-pole chain validated first |

**Funding to pair with them:** NIDHI-PRAYAS ₹10 L, equity-free, 3–6 months, explicitly
covers the design→prototype gap. It is the only scheme that fits M1's stage.

## 4. What to kill

- The **0.5–1 kW / 3000 rpm** target spec as a *market* target. Keep it only as a bench
  demonstrator if you want the physics result.
- **Competing with funded magnet-free players** at 2W/3W. They have factories and OEM
  relationships; M1 has neither.
- **Any plan whose first revenue is hardware.** No capex, no certification budget, no
  inventory.
- **Chasing PLI-Auto / PM E-DRIVE grants.** PLI needs ₹250 cr new investment; PM E-DRIVE
  is demand-side only. Both are categorically closed to M1.

## 5. 90-day sequence (zero capex)

1. **Weeks 1–2** — package the toolchain as a sellable audit: one-page offer, two public
   case studies from Phase 0 (`extractor_convergence`, `torque_density_audit`), fixed
   price. Register proprietorship + GST (prerequisite for invoicing).
2. **Weeks 2–6** — pitch 10 Indian OEMs/tier-1s/EV startups for one paid audit. Target:
   one engagement at ₹75k–2 L.
3. **Weeks 3–8** — apply to NIDHI-PRAYAS through an empanelled centre. Prerequisites in
   `funding_and_revenue_routes.md` §4.
4. **Weeks 4–12** — validate the geometry chain at the **real market spec**
   (1–1.2 kW / ~4.5 N·m cont / ~22 N·m peak / 48–72 V) before any controller or licence
   conversation. This is the Gate-B-style pass on the new envelope D-012 demanded.
5. **Weeks 8–12** — approach one L5 cargo OEM with the domestic-controller thesis and a
   named design-partner proposal. Do not build hardware first.

## 6. Explicitly unverified

- PM E-DRIVE PMP v9 **enforcement date** — not stated in the document.
- All motor/controller prices are **asking prices** (IndiaMART/TradeIndia/Alibaba), not
  contract prices. Contract prices will be lower.
- PRAYAS 2.0 ceiling; state (TN/MH/KA) R&D clauses; EVolutionS intake; TPEM call status;
  ANIC cycle deadline.
- Deal-size bands are ESTIMATE against Tata Elxsi's ₹31 L revenue/engineer-year.
- L3 NdFeB mass inferred at 0.1–0.2 kg/vehicle; the 500 g figure found is L5-class.
- No market data exists yet in this repo for e-2W — only e-3W was researched.

## 7. Standing rule

Nothing in this plan overrides the ground rules: no fabricated quotes, results, or
investor interest; `ESTIMATE` stays labelled; no purchase or external commitment without
founder approval. A paid audit is a sale of *method*, and the method's only asset is that
its numbers are labelled honestly — selling it carelessly destroys the asset.
