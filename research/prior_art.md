# Patent Prior-Art Search — Reluctance Traction Motors

**Preliminary search, 2026-10-20.** Sources: Google Patents, plus institutional/secondary listings where
noted. Statuses are as displayed on Google Patents (which disclaims them as assumptions, not legal
analysis). Rows marked *snippet only* had only the search-result abstract seen.

> **This is not a freedom-to-operate or patentability opinion. Qualified Indian patent counsel review
> is required before any filing decision, product commitment, or public disclosure.**

| ID | Number | Title | Applicant | Juris. | Year | Subject | Relevance to M1 | Access |
|---|---|---|---|---|---|---|---|---|
| P1 | US10707798B2 | Low-noise, high rotor pole SRM | Turntide Technologies | US grant | 2020 | High-rotor-pole geometry for low acoustic noise | Pole-count lever for low-noise SRM | Full text |
| P2 | EP0814558A2 | Switched reluctance motor | Samsung Electronics | EP app | 1997 | Rotor pole flare/chamfer to smooth torque | Pole-arc shaping is old art — constrains naive shaping claims | Snippet only |
| P3 | US20060097596A1 | Switched reluctance machine | Illinois Inst. of Technology | US app | 2006 | R = 2S−2 pole-count relationship | Pole-count selection space | Snippet only |
| P4 | WO2019116389A1 | Unitary stator, slit rotor SRM | IISc Bangalore (PCT/IN) | PCT (IN) | 2019 | Unitary stator + slit rotor structure | Closest verified Indian SRM structural filing; status shown "Ceased" | Full text |
| P5 | US6239526B1 | Flux barrier synchronous reluctance motor | LG Electronics | US grant | 2001 | Multi-layer flux-barrier layout | Foundational barrier prior art; expired | Full text (Expired) |
| P6 | US8638012B2 | Rotor for a synchronous reluctance machine | ABB Research Ltd (Moghaddam) | US grant | 2014 | Barrier sizing/rib arrangement, high saliency | **Active family (~2029), litigation tag — live FTO risk** | Full text (Active) |
| P7 | US9825515B2 | SynRM with q-axis slit width config for power factor | Mitsubishi Electric | US grant | 2017 | q-axis slit width profile | Power-factor lever → inverter sizing | Full text (Active ~2034) |
| P8 | WO2026008363A1 | Rotor and SynRM comprising same | Schaeffler Technologies | PCT | 2026 | Multiple arc-shaped barriers | Very recent barrier topology; space still filing | Snippet only |
| P9 | JP2011083066A | PM-assisted SynRM | Osaka Prefecture Univ. (Sanada, Morimoto) | JP app | 2011 | Ferrite magnets in arc slits, anti-demag | Rare-earth-light PMa-SynRM route | Full text (Pending) |
| P10 | WO2016189445A1 | SynRM assisted by permanent magnets (fam. US10707733B2) | D&M Holding SpA | PCT | 2016 | Curvilinear magnet slots | High-speed PMa rotor concept | Full text (Ceased) |
| P11 | DK3767796T3 | Rotor structure, PMa reluctance sync motor for EV | Zhuhai Gree | DK/EP | 2018– | PMa reluctance rotor, explicitly EV | Directly in EV traction space | Snippet only |
| P12 | US5818140A | Synchronous reluctance motor, low torque-ripple design | Alfredo Vagati | US grant | 1998 | Low-ripple SynRM design | Classic ripple prior art | Snippet only |
| P13 | CN110635591A/B (fam. US12051941B2, EP4037152B1) | Synchronous Reluctance Motor | Gree Electric | CN | 2019 pub / 2025 grant | Ns/2p = Bs+1 relation + barrier-end angle windows, ripple <5% | Numeric ripple windows claimed — parameterized-barrier claims risky | Full text (Active) |
| P14 | US10637386B2 | Torque ripple reduction in SRM | Enedym / McMaster (Bilgin, Emadi) | US grant | 2020 | Control-side current profiling | Ripple claimed in software too; active to ~2038 | Full text (Active) |
| P15 | IN 202421078426 (+202621050377, 202521127533) | PMa-SynRM fluid-shaped barriers; segmented-stator SRM; magnetic-gear-integrated SRM | IIT Bombay (Fernandes group) | IN | 2024–26 | Indian academic reluctance filings | Nearest Indian prior art to likely M1 designs | **Number unverified** (faculty page only) |
| P16 | IN 590023 (app. 202211054118) | Robust Rotating Transformer Excited Synchronous Motor | Phyntelligence India / Volektra / Vimag | IN grant | 2022→2026 | Magnet-free excited sync motor | Indian magnet-free traction activity (adjacent) | **Number unverified** (secondary source) |
| P17 | 202341032548 | Predictive current control for SRM in EVs | SRMIST | IN | 2023 | SRM control method | Indian SRM control filing space is thin | **Number unverified** (institutional listing) |
| P18 | US8686608B2 | SynRM using rotor flux barriers as cooling channels | ABB Schweiz | US grant | 2014 | Barriers as cooling ducts | Magnet-free cooling combo; status Expired-Fee Related | Full text |

## Landscape observations (non-legal)

- **Crowded:** multi-layer flux-barrier topology (P5, P6, P7, P8, P11); generic "plurality of arc-shaped
  barriers" will not look novel.
- **Crowded:** geometric ripple reduction — Gree's numeric windows (P13) and Vagati (P12) cover it.
- **Crowded:** control-side ripple (P14, active).
- **Crowded:** basic SRM pole-arc shaping (back to 1996 priority, P2).
- **Moderate:** ferrite PMa-SynRM — a decade of filings; anti-demagnetization geometry is narrower.
- **Open-ish:** barriers-as-cooling (P18 expired; combinations with partitioned rotors thin);
  Indian-origin structural SRM filings rare (P4 ceased).
- **Open:** Indian 2W/3W OEM reluctance filings — none verifiable in this pass.
