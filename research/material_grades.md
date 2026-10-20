# Steel grades and B-H curve sourcing — Gate B

**Status:** research record, 2026-10-20. Supersedes the open item in
`simulation/validation/known_answer/RESULT_NONLINEAR.md`.

**Update (same day, later):** while wiring the full machine mesh into the
pipeline, a geometry bug was found and fixed in `synrm_geometry.py`:
`stator_profile` placed slot bottoms at `r_bore - depth` (slots poking inward
into the airgap/rotor) instead of `r_bore + depth` (slots cut outward into the
stator iron, as in every real stator). The old convention geometrically
swallowed the 0.7 mm airgap band and collided with the rotor surface. Baseline
JSON regenerated. Regression test added
(`tests/test_synrm_geometry.py::test_slots_extend_outward_from_bore`), plus mesh
area-agreement tests (`tests/test_mesh_regions.py`) that would have caught it:
every region's meshed area is now within 0.3% of its closed-form area.

## 1. Anchor grades (verbatim from full text)

| anchor | grade | thickness | designation family | quoted from |
|---|---|---|---|---|
| Kachapornkul 2022 (SRM) | **35A300** | 0.35 mm | JIS ≡ AISI 36F168 ≡ BS 300 ≡ DIN V300-35A | Energies 15(3):694, p.6 |
| Rajini 2024 (SynRM) | **M1000-65A** | 0.65 mm | EN 10106 / IEC 60404-8-4 | AIMS Energy 12(5):1027, §4.1 |

Both grades verified as real, currently-produced commercial products across
independent manufacturers (Nippon Steel, JFE, ArcelorMittal, ThyssenKrupp,
Aperam, Erdemir, CSC). This is a *product-existence* check, not a magnetic
data source.

## 2. Manufacturer catalogs do NOT contain B-H curves

Checked directly, by extracting text from the PDFs:

| source | URL | has B-H curve? |
|---|---|---|
| JFE Electrical Steel Sheets f1e-001 | jfe-steel.co.jp/en/products/electrical/catalog/f1e-001.pdf | **No** — loss (W/kg) and polarization at 800 A/m only |
| ArcelorMittal Electrical Steels brochure | ssc.arcelormittal.com/IMG/pdf/electricalsteelsbrochure_en.pdf | **No** — grade-equivalence tables and loss only |
| Aperam Electrical Steel EN | aperam.com/sites/default/files/documents/Electrical_Steel_EN.pdf | **No** — and does not list M1000-65A at all |
| JFE Super Core f1e-002 | jfe-steel.co.jp/en/products/electrical/catalog/f1e-002.pdf | Graphs only (no data tables); different product family |

JFE's own f1e-001 states: *"For detailed data and characteristic curves of each
type of electrical steel sheet, please read the relevant separate catalog."*
i.e. the curves are in a separate document that was not located as a free
public PDF with numeric data.

**Conclusion:** the "manufacturer datasheet is the likely free source" hypothesis
was **wrong**. Public catalogs give guaranteed *loss* and *polarization at a few
fixed H values*, not a tabulated B-H curve. A B-H curve needs many (H, B) pairs
to drive a nonlinear solver.

## 3. What the fixed-H specs do give us (useful, but not sufficient)

Example, Aperam standard NOES table (Table 1 of the brochure) — guaranteed
polarization at three field strengths:

| product | thickness | B@2500 A/m | B@5000 A/m | B@10000 A/m |
|---|---|---|---|---|
| M470-65A | 0.65 mm | 1.60 T | 1.70 T | 1.80 T |
| M600-65A | 0.65 mm | 1.60 T | 1.70 T | 1.80 T |

Aperam does not list M1000-65A. The Erdemir PDF that surfaced in search results
contains an M1000-65A row (B = 1.61 / 1.71 / 1.80 T at 2500 / 5000 / 10000 A/m,
which is consistent with the Aperam 0.65 mm family), but the host failed TLS
verification and it has **not** been retrieved or verified — it is recorded here
as *unverified, not used*.

These three points are a poor basis for nonlinear FEA on their own. They are,
however, usable as **sanity bounds** on any curve we do adopt (see §6).

## 4. MagWeb SMAG — the good source, but it is paid

`https://www.magweb.us/smag` — reports ~5000 soft-magnetic property curves;
the SMAG Handbook v7 documents 336 NGO electrical-steel grades with 634 B(H)
curves. Data format is documented (`.xlsx`, `BH50Hz`, 0.05 T spacing) and it is
explicitly smoothed for FEA convergence.

**It is a paid subscription** ($50/month or $400/year), and the "free trial"
does not grant redistribution or archival rights. Adopting it is a **spend
decision** and requires founder approval before use. Not used in any result so
far. Logged in `finance/`.

## 5. Local library: two different curves both named "M-19"

The FEMM library `/usr/local/share/xfemm/release/matlib.dat` contains **two**
entries matching the string "M-19", with materially different data:

| entry | BH points | Mu_x | d_lam | section | H at 1.5 T | implied μr at 1.5 T |
|---|---|---|---|---|---|---|
| `M-19 Steel` | 47 | 4416 | 0.635 mm | laminated steel | 1108 A/m | **1077** |
| `M-19` | 33 | 1 | 0 (non-laminated) | handbook curves | 3342 A/m | **357** |

A 3× difference in μr at a typical operating flux density. `load_bh_curve()`
matches on the exact string, so `load_bh_curve("M-19 Steel")` gets the 47-point
laminated entry — which is what the validated toroid test used.

**Neither is an anchor grade.** `M-19 Steel` is 0.635 mm (25 mil, AISI), not
Kachapornkul's 0.35 mm 35A300 nor Rajini's 0.65 mm M1000-65A.

Note the trap: `M-19 Steel`'s `d_lam` of 0.635 mm is *numerically identical* to
Rajini's 0.65 mm. Thickness agreement is not grade agreement — these are
different steels with different silicon content and different loss classes.

## 6. Decision for now

- The nonlinear solver is validated (Ampère, 0.49%/0.18%). That stands.
- **No anchor torque comparison will be run on M-19 or on any substitute grade.**
- If the MagWeb subscription is declined, the honest fallback is to digitize the
  B-H curve **from the anchor paper's own figure**, cite it as a digitization
  with stated reading error, and label the comparison *indicative, not
  validated*. That is weaker than a measured curve but is at least the *right
  material*, which M-19 is not.

## Open items
- [ ] Founder decision: MagWeb subscription ($400/yr) — yes / no / defer
- [ ] Retrieve and verify the Erdemir M1000-65A row (currently unverified)
- [ ] Locate JFE's separate detailed NGO catalog with characteristic curves
- [ ] Digitize anchor-paper B-H figures as the no-spend fallback
- [ ] Confirm JIS/EN loss-class readings against a standards text (the "300" and
      "1000" readings are currently convention-derived, not measured)
- [ ] Verify which of the two "M-19" entries is intended for which use in FEMM
