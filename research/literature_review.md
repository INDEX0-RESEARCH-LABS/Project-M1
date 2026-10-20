# Literature Review — Project M1 (Gate A)

**Compiled:** 2026-10-20 · Four parallel search passes: (1) SRM/SynRM architectures & India context,
(2) torque ripple/control/thermal, (3) AI-assisted optimization, (4) patent prior art (see `prior_art.md`).

**Verification policy:** every row was checked against Crossref/OSTI/NASA NTRS/repo APIs or full text
where possible. Rows marked *abstract only* / *metadata only* had **no numbers quoted from them** —
treat everything in those rows as unknown. No citation in this file was invented.

---

## 1. SRM and SynRM architectures; magnet-free motivation; India context

| # | Title | Authors | Year | Venue | DOI / URL | Arch. | Method | Key results (only as seen) | Evidence | Access |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Opportunities and Challenges of Switched Reluctance Motor Drives for Electric Propulsion: A Comparative Study | Bostanci, Moallem, Parsapour, Fahimi | 2017 | IEEE TTE 3(1):58–75 | 10.1109/TTE.2017.2649883 | SRM vs IPM/IM | Comparative | — | not verified | Abstract only |
| 2 | Making the Case for Switched Reluctance Motors for Propulsion Applications | Bilgin, Howey, Callegaro, Liang, Kordic, Taylor | 2020 | IEEE TVT 69:7172–7186 | 10.1109/TVT.2020.2993725 | SRM (e-bike, HEV) | Design study | Qualitative: low-cost, secure supply chain | not verified | Abstract only |
| 3 | Review of SRM Converters and Torque Ripple Minimisation Techniques for EV Applications | Abdel-Aziz, Elgenedy, Williams | 2024 | Energies 17(13):3263 | 10.3390/en17133263 | SRM + converters | Review | Topology recommendations | Review | Abstract only |
| 4 | Overview of multi-phase SRM drives for electric vehicles | Han, Diao, Sun | 2021 | Adv. Mech. Eng. | 10.1177/16878140211045195 | Multi-phase SRM | Review | Full-bridge converter suitable; TSF/DTC/DITC main ripple controls | Review | Abstract only |
| 5 | Control techniques of SRMs in EV applications: torque ripple reduction strategies | Saleh, Al-Amyal, Számel | 2024 | AIMS EEE 8(1) | 10.3934/electreng.2024005 | SRM | Review | Ripple + audible noise = main SRM drawbacks; method taxonomy | Review | **Full text** |
| 6 | A review on switched reluctance machines for EVs | Zabihi, Gouws | 2016 | IEEE ISIE | 10.1109/ISIE.2016.7744992 | SRM | Review | — | Review | Metadata only |
| 7 | Comparative Study of IPM, Induction, and SRM Drives for EV/HEV | Yang, Shang, Brown, Krishnamurthy | 2015 | IEEE TTE 1:245–254 | 10.1109/TTE.2015.2470092 | IPM/IM/SRM | Comparative | — | not verified | Metadata only |
| 8 | Torque Density and Efficiency Improvements of an SRM Without Rare-Earth Material | Chiba et al. | 2011 | IEEE TIA | 10.1109/TIA.2011.2125770 | SRM (no rare-earth) | — | — | not verified | Metadata only |
| 9 | 60 kW PMSM, EESM, SynRM under steady-state and drive cycle | Paulraj, Obulesu | 2025 | IEEE Access 13 | 10.1109/ACCESS.2025.3606372 | PMSM/EESM/SynRM | Drive-cycle eval | — (car-class, not 2W) | not verified | Abstract only |
| 10 | A Review of Synchronous Reluctance Motor-Drive Advancements | Heidari et al. | 2021 | Sustainability 13(2):729 | 10.3390/su13020729 | SynRM | Review | **Skewing can halve torque ripple; asymmetric barriers ~⅔ ripple; industrial SynRM reaches IE5** | Review | **Full text** |
| 11 | Advances in Analytical Modelling and Design of SynRM for EVs | Abdulsamad, Dhulipati, Chaoui | 2026 | Machines 14(7):796 | 10.3390/machines14070796 | SynRM | Review | Open challenge: cut computational cost while preserving accuracy | Review | **Full text** |
| 12 | Adoption of SynRM in EVs: flux-weakening focus | Credo, Villani, Fabri, Popescu | 2023 | IEEE TTE 9(1):805–818 | 10.1109/TTE.2022.3204435 | SynRM | Vehicle model + 2 case studies | **Poor flux weakening → peak-power oversizing for high performance; viable for modest demands** | Model-based | Abstract only |
| 13 | Drive-cycle optimization of rare-earth-free SynRM (coupled thermal+magnetic networks) | López-Torres, Garcia Espinosa, Riba, Romeral | 2018 | IEEE TVT 67:196–205 | 10.1109/TVT.2017.2739020 | Rare-earth-free SynRM | Lumped networks | — | not verified | Metadata only |
| 14 | Performance Improvement of an SRM Drive for an Electric Motorcycle | Kachapornkul et al. | 2022 | Energies 15(3):694 | 10.3390/en15030694 | 6/4 & 8/6 SRM | **FEA + prototype + bench** | **3.5 kW 6/4: ≈82% max eff, 82 km/h, 98 km @40 km/h; 6/4 vs 8/6: +13.2% torque, +14.7% torque/weight, −9.8% eff, +6.5% Cu+Fe cost** | **Experimental** | **Full text** |
| 15 | External-Rotor Direct-Drive E-Bike SRM | Howey, Bilgin, Emadi | 2020 | IEEE TVT 69:2552–2562 | 10.1109/TVT.2020.2965943 | 12/16 ext-rotor SRM | FEM + GA + validation | Sized vs commercial PM e-bike motor; efficiency maps | Experimental validation | Abstract only |
| 16 | External-rotor SRM for an electric scooter | Sandesh, Jogi, Pitchaimani, Gangadharan | 2023 | Mater. Today Proc. | 10.1016/j.matpr.2023.03.696 | Ext-rotor SRM | Design/optimization | — | not verified | Metadata only |
| 17 | 8/18 multi-teeth vs 8/10 in-wheel SRM for an e-scooter | Sandesh Bhaktha et al. | 2024 | Automatika | 10.1080/00051144.2024.2329492 | In-wheel SRM | Comparative | — | not verified | Metadata only |
| 18 | EM design, sensitivity, optimization, multiphysics of rare-earth-free SynRM for an electric trike | Rajini, Nagarajan, Harikrishnan, Kolhe | 2024 | AIMS Energy 12(5):1027–1053 | 10.3934/energy.2024049 | SyncRelM / ferrite-assisted | FEA + DoE + ELM surrogate + **1.2 kW prototype** | **Six powertrains compared; SyncRelM/ferrite-assisted judged superior on EM+thermal+vibration; prototype tested on Indian drive cycle** | **Experimental + FEA** | **Full text** |
| 19 | Development and performance analysis of SRM for E-rickshaw | Phatak, Mandake, Bankar | 2021 | Indian J. Sci. Technol. 14(38) | 10.17485/IJST/v14i38.1713 | 8/6, 48 V, 0.5 kW SRM | FEA + hardware | Qualitative ("Make in India" framing) | FEA + prototype (no numbers) | **Full text** |
| 20 | Techno-economic assessment of motors for three-wheeler e-auto (Indian context) | Vaidehi, Dhar, Jayakumar, Lavanya, Dinesh Kumar | 2021 | Mater. Today Proc. 45 | 10.1016/j.matpr.2020.11.711 | Multiple | Techno-economic | Frames choice around low weight, high power density, affordability | Comparative | Abstract only |
| 21 | Motor and battery selections for three-wheeler EV | Sreejith R., Rajagopal | 2016 | IEEE ICPEICES | 10.1109/ICPEICES.2016.7853494 | 2 kW SRM (per listing) | Design/opt. | — | not verified | Abstract snippet only |
| 22 | AIS-156 (L-category powertrain + REESS safety); AIS-137 Pt 5 (power measurement); AIS-039/040/041 (consumption, range, net power); AIS-017 Pt 6 (e-rickshaws) | ARAI (CMVR) | 2020– | Indian standards | araiindia.com (index verified) | Standard | Regulatory | **No motor-topology-specific clause found**; power measurement in AIS-137 Pt 5 | Regulatory | Index only; PDFs paywalled |
| 23 | Promoting Clean Energy Usage Through Accelerated Localization of E-Mobility Value Chain | NITI Aayog | 2022 | Govt. of India report | niti.gov.in (PDF opened) | — | Policy | **India "heavily dependent on specific geographies for Rare-Earth Permanent Magnet…"; e-motor magnets "still imported"** | Policy | **Full text** |
| 24 | Rare-earth-free propulsion motors for EVs: a technology review | Riba, López-Torres, Romeral, Garcia | 2016 | Renew. Sustain. Energy Rev. | 10.1016/j.rser.2015.12.121 | All PM-less | Review | Motivation: shortage, price volatility, geographic concentration | Review | Abstract only |
| 25 | Electric Vehicle Motors Free of Rare-Earth Elements — An Overview | Rangarajan, Shiva, Collins, Senjyu | 2025 | Machines 13(8):702 | 10.3390/machines13080702 | EESM/IM/SRM/SynRM | Review | **SRM: no magnets → no rare-earth exposure; wound-field flagged most promising near-term PM-less path** | Review | **Full text** |

## 2. Torque ripple, noise, control, inverter losses, thermal

| # | Title | Authors | Year | Venue | DOI / URL | Topic | Key results (as seen) | Evidence | Access |
|---|---|---|---|---|---|---|---|---|---|
| 26 | Analysis and Reduction of Vibration and Acoustic Noise in the SRM Drive | Wu, Pollock | 1995 | IEEE TIA 31(1) | 10.1109/28.363045 | SRM noise | — | not confirmed | Abstract only |
| 27 | Acoustic noise cancellation techniques for SRM drives | Pollock, Wu | 1997 | IEEE TIA 33(2) | 10.1109/28.568013 | SRM noise | Radial-force smoothing, staged commutation | mixed | Abstract only |
| 28 | Vibration modes and acoustic noise in a 4-phase SRM | Colby, Mottier, Miller | 1995 | Conf. (OSTI 419531) | osti.gov/biblio/419531 | SRM noise | Modal + impulse testing | **Experimental** | Abstract (OSTI) |
| 29 | Active Cancellation of Vibration in SRM (impulse response method) | Kimpara et al. (Fahimi group) | 2019 | IEEE TEC 34(3) | 10.1109/TEC.2019.2916401 | 8/6 SRM | Active cancellation | Experimental (per abstract) | Abstract only |
| 30 | Rotor Flux-Barrier Design for Torque Ripple Reduction in SynRM/PMa-SynRM | Bianchi, Bolognani, Bon, Dai Pre | 2009 | IEEE TIA 45(3) | 10.1109/TIA.2009.2018960 | SynRM | Barrier design for ripple | Simulated | Abstract only |
| 31 | Design Optimization of SynRM for Low Torque Ripple | Credo et al. | 2019 | AIRO Springer | 10.1007/978-3-030-25842-9_5 | SynRM | Numerical opt + FEM | Simulated | Abstract only |
| 32 | Design of low-torque-ripple synchronous reluctance motors | Vagati, Pastorelli, Francheschini, Petrache | 1998 | IEEE TIA 34(4) | 10.1109/28.703969 | SynRM | Design rules for low ripple | mixed | Abstract only |
| 33 | Acoustic Noise Reduction of SRM With Reduced RMS Current and Enhanced Efficiency | Bayless, Kurihara, Sugimoto, Chiba | 2016 | IEEE TEC 31(2) | 10.1109/TEC.2015.2496968 | SRM | Control-side profiling cuts noise *and* raises efficiency | not confirmed | Abstract only |
| 34 | Acoustic Noise Mitigation in High Pole Count SRMs Utilizing Skewing | Gundogmus et al. | 2022 | IEEE TIE 69(6) | 10.1109/TIE.2021.3095808 | SRM | Stator+rotor skewing | not confirmed | Abstract only |
| 35 | Design and control for torque ripple reduction of a 3-phase SRM | Marcsa, Kuczmann | 2017 | Comput. Math. Appl. 74(1) | 10.1016/j.camwa.2017.01.001 | 3-ph SRM | FEM co-simulation + control | Simulated | **Full text** |
| 36 | Noise and Vibration in SRMs: Review of structural materials, dampers, impedance, masking | Sahu, Emadi, Bilgin | 2023 | IEEE Access 11 | 10.1109/access.2023.3257124 | SRM | Passive/structural countermeasures | Review | Abstract only |
| 37 | Radial Force Shaping for Acoustic Noise Reduction in SRMs | Callegaro, Bilgin, Emadi | 2019 | IEEE TPEL 34(10) | 10.1109/TPEL.2019.2891050 | SRM | Radial force waveform shaping | not confirmed | Abstract only |
| 38 | Direct instantaneous torque control for SRM considering mutual coupling | Weiss, Schoeler, De Doncker | 2019 | J. Eng. 2019(17) | 10.1049/joe.2018.8136 | SRM | DITC + mutual coupling | Simulated + FEM corr. (ref machine 4.9 Nm; 4th/8th/12th harmonics) | **Full text** |
| 39 | PWM-based DITC with duty cycle interlock (FPGA) | von Hoegen, Woerndle, De Doncker | 2020 | ICEMS | 10.23919/ICEMS50442.2020.9291031 | SRM | FPGA implementation | Simulated | Metadata |
| 40 | DITC with improved-convergence sliding mode control for vehicle SRM | Wu et al. | 2025 | Sci. Rep. 15:27130 | 10.1038/s41598-025-06550-4 | 8/6, 4 kW, 20 Nm, 1500 rpm | **Ripple 9.08% vs 12.84%; error −20–29%; startup −32%** | **Simulated only** | **Full text** |
| 41 | Sensorless SynRM drives: adaptive projection vector position estimation | Varatharajan, Pellegrino | 2020 | IEEE TIA 56(2) | 10.1109/TIA.2019.2961986 | SynRM | Sensorless estimation | not confirmed | Abstract only |
| 42 | Sensorless SynRM drives: projection vector, stator resistance immunity | Varatharajan, Pellegrino | 2020 | IEEE TIA 56(5) | 10.1109/TIA.2020.3009641 | SynRM | Sensorless estimation | not confirmed | Abstract only |
| 43 | Design Optimization of a SynRM Based on Operating Cycle | Credo, Pescetto | 2020 | ICEM | 10.1109/ICEM49940.2020.9271012 | SynRM | Cycle-weighted optimization | not confirmed | Abstract only |
| 44 | Loss Comparison of GaN, SiC, and IGBT Inverters for Low Voltage High Current Two-Wheeler EV | Suyal, Dutta, Yadav | 2024 | IEEE PEDES | 10.1109/PEDES61459.2024.10961671 | 2W inverter | Loss comparison | — (abstract level) | Abstract only |
| 45 | IGBT vs SiC inverter loss for 400/800 V EV drivetrains | Allca-Pekarovic et al. | 2020 | IEEE ECCE | 10.1109/ECCE44975.2020.9236202 | EV inverter | Loss modelling + test | **~5% energy/range improvement full SiC (400/800 V, not 24–48 V)** | Exp. + sim | Abstract + numbers |
| 46 | SiC/GaN devices: theoretical comparison + experimental evaluation | Li, Evans, Johnson | 2018 | IET EST 8(1) | 10.1049/iet-est.2017.0022 | Devices | Loss theory + experiment | GaN-HEMT lower conduction+switching (qualitative) | Experimental | Open access |
| 47 | LPTN validation of an IPM motor (parametric investigation) | Sequeira, Bennion, Cousineau et al. | 2022 | ASME J. Electron. Packag. 144(2) | 10.1115/1.4053121 | IPM | LPTN vs FEA vs exp | **LPTN within 4% of experiment; contact resistance most sensitive parameter** | **Experimental** | **Full text** |
| 48 | Temperature field + cooling optimization for PM in-wheel motor (EM-thermal coupling) | Wang et al. | 2023 | Energies 16(3):1527 | 10.3390/en16031527 | PM in-wheel | EM-thermal FEM | — | Simulated | Abstract only |
| 49 | EM-thermal co-optimization to minimize case-to-winding temperature rise | Liu, Luta, Pekarek, Weibel | 2024 | Appl. Therm. Eng. 238:122132 | 10.1016/j.applthermaleng.2023.122132 | PM machine | Co-optimization formulation | — | not confirmed | Abstract only |
| 50 | Combined EM and thermal design optimization of in-slot cooling for UAM motors | Tallerico, Smith (NASA Glenn) | 2022 | NASA NTRS 20220008023 | ntrs.nasa.gov/citations/20220008023 | Traction motor | EM+thermal+mech opt, Pareto | **Pareto: 92–95% eff at 15–35 kg** (aerospace class) | Simulated | **Full PDF** |

## 3. AI-assisted optimization & surrogate modelling

| # | Title | Authors | Year | Venue | DOI / URL | Method | Application / key gains | Evidence | Access |
|---|---|---|---|---|---|---|---|---|---|
| 51 | A physics-informed Bayesian optimization method for rapid development of electrical machines | Asef, Vagg | 2024 | Sci. Rep. 14:4526 | 10.1038/s41598-024-54965-2 | BO (GP, physics-informed) | EESM; **45% faster than NSGA-II; SFF +20%; torque +12%** | Simulated (no prototype) | **Full text** |
| 52 | Global multi-objective BO framework for machine design using GPR | Rossmann, Kamper, Hackl | 2024 | TechRxiv | 10.36227/techrxiv.172305090.03395409/v1 | MOBO + GPR | RSM, 14 variables, 3 objectives | Simulated | Preprint, abstract only |
| 53 | AI-Assisted BO of a PMSM for E-Bike Applications | Guesmia, Pham, Pan | 2026 | Machines 14(2):160 | 10.3390/machines14020160 | BO + LLM/RAG priors | PMSM; Pareto eff ≈93.3–93.6%, ripple ≈12.8–14.2% (snippet-level) | Simulated | Abstract only |
| 54 | Enhanced MOO of salient-pole reluctance magnetic gear using BO-tuned ANN | Shoaei, Farshbaf-Roomi, Wang | 2025 | IET EPA | 10.1049/elp2.70017 | BO(ANN) + MOO | **avg torque +11.7%, ripple −47.2%** (abstract snippet) | Simulated | Abstract only |
| 55 | PMaSynRM design: Kriging surrogate + NSGA-II + Taguchi | Kumar, Srinivas | 2024 | IEEE TENCON | 10.1109/TENCON61640.2024.10902704 | Kriging+NSGA-II | PMaSynRM rotor geometry | not verified | Metadata only |
| 56 | Automatic design of SynRM focusing on barrier shape optimization | Pellegrino, Cupertino, Gerada | 2015 | IEEE TIA 51(3) | 10.1109/TIA.2014.2345953 | MOGA + FEM | Canonical SynRM barrier optimization reference | Simulated | Metadata only |
| 57 | Barrier shapes and minimum set of rotor parameters in automated SyR design | Pellegrino, Cupertino, Gerada | 2013 | IEEE IEMDC | 10.1109/IEMDC.2013.6556286 | GA + FEM | Barrier parametrization study | Sim + prototypes noted | Abstract |
| 58 | FEM-based overall optimization of SRM using NSGA-II | El-Nemr, Afifi, Rezk, Ibrahim | 2021 | Mathematics 9(5):576 | 10.3390/math9050576 | NSGA-II + FEM | SRM geometry, multi-objective | Simulated | Abstract only |
| 59 | Intelligent optimization of SRM using genetic aggregation response surface + NSGA-II | Abunike, Okoro, Aphale | 2022 | Energies 15(16):6086 | 10.3390/en15166086 | Surrogate + NSGA-II | **eff 85% → 94.05% @2000 rpm (simulated; FEM cross-check, no prototype)** | Simulated | Abstract + numbers |
| 60 | Evolutionary multi-objective pole shape optimization of SRM | Balaji, Kamaraj | 2012 | Int. J. EPES | 10.1016/j.ijepes.2012.05.011 | NSGA-II | SRM pole shape | Simulated | Abstract only |
| 61 | FEM design + multi-objective optimization of four-pole reluctance motor (NSGA-II) | Abunike, Okoro, Davidson | 2021 | IEEE AFRICON | 10.1109/AFRICON51333.2021.9570964 | NSGA-II + FEM | **torque +15%, eff +13.2%, ripple −1.55%, loss −30.1%** | Simulated | Abstract |
| 62 | Design, optimization, and prototyping of PM-assisted SynRM using NSGA-II | Shafiei Khouzani, Mirsalim, Moghani | 2026 | SSRN | 10.2139/ssrn.7233541 | NSGA-II | PMaSynRM | not verified | Preprint, metadata only |
| 63 | Surrogate modeling of electrical machine torque using ANNs | Tahkola et al. | 2020 | IEEE Access | 10.1109/ACCESS.2020.3042834 | ANN / GBDT surrogate | PMSM torque from FEA | Simulated | Abstract only |
| 64 | Multi-objective motor design with physics-assisted neural network model | Sakamoto et al. (MERL) | 2023 | IEEE IEMDC | 10.1109/IEMDC55163.2023.10238886 | Physics-assisted NN surrogate | Less training data than pure NN; Pareto re-validated with FEA | Simulated | Abstract |
| 65 | A review of data-driven surrogate models for design optimization of electric motors | Cheng, Zhao, Dhimish, Qiu, Niu | 2024 | IEEE TTE | 10.1109/TTE.2024.3366417 | Survey | Open problems: generalization, material data, validation | Review | **Full text (author PDF)** |
| 66 | Review of surrogate-model-assisted MOO of electrical machines | Liu et al. (incl. Zhu, Ma) | 2025 | Renew. Sustain. Energy Rev. 215 | 10.1016/j.rser.2025.115609 | Survey | — | Review | Abstract only |
| 67 | Topology optimization of electric machines: a review | Gadiyar, Wang | 2022 | IEEE ECCE | 10.1109/ECCE50734.2022.9948073 | Survey | Hybrid two-step TO: ~40% ripple reduction + 0.5% avg-torque gain (as summarized) | Review | Partial PDF |
| 68 | Robust design optimization of electrical machines: multi-objective approach | Lei, Bramerdorfer, Ma, Guo, Zhu | 2021 | IEEE TEC | 10.1109/TEC.2020.3003050 | Robust MOO | Tolerance/uncertainty-aware design | not verified | Metadata only |
| 69 | Bayesian calibration of computer models | Kennedy, O'Hagan | 2001 | J. R. Stat. Soc. B | 10.1111/1467-9868.00294 | Methodological | Model discrepancy foundation | Methodological | Metadata only |
| 70 | Learning about physical parameters: the importance of model discrepancy | Brynjarsdóttir, O'Hagan | 2014 | Inverse Problems 30:114007 | 10.1088/0266-5611/30/11/114007 | Methodological | **Ignoring model discrepancy → biased, over-confident parameter estimates that do not improve with more data** | Methodological | **Full text** |
| 71 | When and why PINNs fail to train: an NTK perspective | Wang, Yu, Perdikaris | 2022 | J. Comput. Phys. 449:110768 | 10.1016/j.jcp.2021.110768 | Methodological | PINN failure analysis | Methodological | Metadata only |
| 72 | Kriging metamodeling in simulation: a review | Kleijnen | 2009 | Eur. J. Oper. Res. | 10.1016/j.ejor.2007.10.013 | Methodological | Surrogate validation practice | Methodological | Metadata only |

**Also verified (book):** Oberkampf & Roy, *Verification and Validation in Scientific Computing*,
CUP 2010, 10.1017/cbo9780511760396 — supports the "simulation ≠ physical validation" stance.

---

## Cross-cutting synthesis

1. **Magnet-free motivation is real and documented** (records 23, 24, 25): India's rare-earth import
   dependence is stated in a Government of India policy report; SRM has no magnets at all; SynRM has none.
2. **SRM's known blockers remain torque ripple and audible noise** (5, 26–37) — but the mitigation
   toolbox is mature: design-side (pole count, skew, barrier/pole shaping) and control-side (DITC,
   current profiling, radial force shaping).
3. **Experimental prototypes in M1's power band exist and are few**: 3.5 kW e-motorcycle SRM (14),
   1.2 kW Indian-drive-cycle ferrite-assisted SynRM trike (18), 0.5 kW/48 V e-rickshaw SRM (19).
   All quantitative efficiency claims at this scale cluster around the low-to-mid 80s % for SRM.
4. **SynRM is strong in industry (IE5) but nearly absent in 2W/3W prototypes** (10, 12, 18): flux-
   weakening weakness matters less for low-speed e-2W/e-3W duty — a possible opening.
5. **AI-optimization gains are all simulation-conditional** (51–64); validation practice is
   "re-run FEA on Pareto points", i.e. validating the surrogate against its own teacher.
   Brynjarsdóttir & O'Hagan (70) is the corrective nobody in the EM papers cites.
