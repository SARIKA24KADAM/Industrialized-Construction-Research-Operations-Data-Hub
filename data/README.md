# Demo data provenance

All CSVs under `data/demo/` are fictional exports from the deterministic generator in `src/demo_data.py`. There are no external databases, contractor systems, worker records, or public datasets behind these files. The generator uses a fixed NumPy seed so the examples remain reproducible.

Regenerate the six CSV files and the three README graph images from the repository root:

```powershell
python -m src.export_readme_assets
```

The CSVs are provided as inspectable flat-file examples of the shaped tables an eventual integration could produce. They are not source-of-truth operational records. See `docs/architecture.md` for a proposed production integration pattern and `docs/governance.md` for ownership and handling questions to resolve before connecting real systems.
