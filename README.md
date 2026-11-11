# Industrialized Construction Research & Operations Data Hub

A portfolio MVP for integrating construction project, labor, equipment, production, procurement, and document information into a governed operations view. The app uses deterministic synthetic data so it can run without access to company systems or real worker information.

## Run locally

Requires Python 3.10+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Use the sidebar to filter the sample portfolio. Explore project delivery, labor and equipment indicators, production plan attainment, procurement lead times, and keyword search across sample reports, meeting notes, quality inspections, and change requests. Data Quality exposes validation checks; Governance summarizes ownership and handling expectations.

## Data and integration scope

`src/demo_data.py` creates stable, fictional project, daily labor, equipment, production, purchase order, and document datasets. `src/quality.py` checks required fields, uniqueness, valid ranges, and referential integrity before metrics are calculated. The sample has no external connectors and is not representative of any real contractor.

For a production integration, replace the demo generator with approved source adapters, preserve source keys and load timestamps, define incremental recovery and reconciliation, and obtain data-owner approval before exposing person-level records. See `docs/` for the starter architecture and governance register.

## Repository map

- `app.py` — interactive Streamlit dashboard.
- `src/demo_data.py` — repeatable synthetic source datasets.
- `src/quality.py` — reusable validation checks.
- `docs/architecture.md` — proposed integration pattern and operational controls.
- `docs/governance.md` — starter ownership, classification, and use guidance.

## Limitations

All records and targets are simulated for demonstration. Productivity measures are aggregate indicators, not individual performance scores. Schedule variance and cost indicators are simplified examples and must not be used for commercial, safety, labor, or employment decisions.
