# Data governance starter register

This register is a proposal for discovery, not evidence of an existing company policy. Confirm each owner, classification, lawful purpose, and retention rule with the organization before connecting operational systems.

| Data domain | Proposed owner | Sensitivity | Dashboard treatment | Open decision |
|---|---|---|---|---|
| Project master and schedule | Project controls | Internal commercial | Project-level | Source of truth and schedule calendar |
| Budget and cost | Project controls / finance | Confidential commercial | Authorized project scope | Currency, commitments, actuals, and forecast definitions |
| Timekeeping and labor | Workforce operations | Restricted personal / employment | Aggregate by project and date | Approved purpose, aggregation minimums, access, retention |
| Equipment telemetry | Equipment operations | Internal operational | Project-level | Planned maintenance and downtime semantics |
| Production / quality | Manufacturing or site operations / quality | Internal commercial | Project and component-type aggregate | Definition of planned quantity, accepted output, and rework |
| Procurement | Procurement | Confidential commercial | Project-scoped order and delivery risk | Supplier visibility, delivery status, and lead-time calendar |
| Project documents | Document owner / records management | Varies by record | Metadata and approved excerpts | Record classes, authoritative version, retention, and search permissions |

## Minimum controls before production

- Document an accountable data owner and steward for each source and metric.
- Approve purpose, access groups, retention, and correction process before ingestion.
- Keep direct employee identifiers out of broad portfolio views; review small-group disclosure risk.
- Preserve lineage, transformation versions, load manifests, validation outcomes, and audit logs.
- Define freshness and reconciliation thresholds with owners; surface stale or incomplete data clearly.
- Review metric changes and dashboard use with project controls, operations, workforce, and privacy stakeholders.

The synthetic dashboard is a design demonstration. Its productivity and schedule indicators are not validated for workforce decisions, contract claims, safety decisions, or forecasting.
