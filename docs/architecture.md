# Reference architecture

This MVP keeps the source integration boundary explicit. The dashboard reads shaped project, labor, equipment, production, procurement, and document datasets.

## Production flow

1. **Ingest:** approved, read-only adapters pull from project controls, timekeeping, and equipment systems. Persist source identifiers, extraction time, and source schema version.
2. **Land:** retain immutable, access-controlled raw snapshots with load manifests and replay capability.
3. **Validate:** enforce required fields, key uniqueness, valid dates and units, referential integrity, and freshness SLAs. Quarantine invalid batches and alert the named owner.
4. **Conform:** map source project identifiers to a governed project key; standardize timezone, cost currency, workday, labor, and equipment definitions.
5. **Serve:** publish documented, least-privilege aggregate marts with lineage to source and transformation version.
6. **Monitor:** track load freshness, row counts, rejected records, reconciliation variance, and metric changes.

The current app implements only deterministic synthetic tables, keyword search over sample document excerpts, and a subset of validation. It has no production connectors, persistent storage, access control, BIM model link, AI retrieval, or scheduling.

## Core grain and keys

| Entity | Grain | Key | Example measures |
|---|---|---|---|
| Project | One row per project | `project_id` | budget, planned and actual progress |
| Labor | One row per project and work date | `project_id`, `work_date` | aggregate hours, cost, earned units |
| Equipment | One row per project and work date | `project_id`, `work_date` | active units, availability and downtime hours |
| Production | One row per project, date, and component type | `project_id`, `work_date`, `component_type` | planned, completed, and rework units |
| Procurement | One row per purchase order | `po_id` | supplier, material, expected date, lead time |
| Documents | One row per information item | `document_id` | type, date, project, owner, text excerpt |

Metric definitions must be approved by their business owners before production use. Earned units are intentionally generic in the demo; a real productivity measure needs a scope-specific quantity and approved earned-value method.
