# Project M1

India-first electric traction motor R&D initiative.

**Guiding principle:** Research rigor first. Simulation second. Prototype third. Scale only after validation.

## Status

| Phase | Description | Status |
|---|---|---|
| 0 | Workspace initialization | ✅ Done |
| 1 | Literature review & prior art | 🔄 In progress |
| 2 | Baseline architecture selection | ⬜ Not started |
| 3 | Simulation workflow | ⬜ Not started |
| 4 | AI-assisted optimization | ⬜ Not started |
| 5 | Novelty & IP | ⬜ Not started |
| 6 | Physical prototype (target 2026-11-12) | ⬜ Not started |
| 7 | Funding & commercial validation | ⬜ Not started |

## Repository layout

- `research/` — literature review, bibliography, prior-art and gap matrices
- `requirements/` — target spec, operating envelope, safety, acceptance criteria
- `architecture/` — candidate comparison, baseline selection, EM/thermal/control design
- `simulation/` — models, scripts, configs, results, validation (never edit committed results by hand)
- `optimization/` — objectives, constraints, experiment registry, surrogates
- `prototype/` — drawings, BOM, manufacturing and test plans, test results
- `finance/` — staged budget, supplier quotes, funding milestones
- `ip/` — invention disclosures, patent search log (private — see `ip/README.md`)
- `reports/` — weekly reports, technical review, investor brief
- `tests/` — automated tests for simulation/optimization code

## Setup (reproducibility)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q
```

Pinned tool versions: see `docs/toolchain.md`.

## Ground rules

- No fabricated citations, simulation results, test data, quotes, or investor interest.
- Estimates are labelled `ESTIMATE`; only written quotations are `CONFIRMED`.
- No purchases, external commitments, or public disclosure without founder approval.
- API keys and supplier-confidential data never enter version control.
