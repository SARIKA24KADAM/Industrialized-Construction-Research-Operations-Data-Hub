"""Deterministic fictional inputs for the dashboard demonstration."""
from __future__ import annotations

import numpy as np
import pandas as pd


def load_demo_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    projects = pd.DataFrame([
        ("P-101", "Harbourview Residences", "Toronto", "Residential", "2026-01-05", "2026-12-18", 18_500_000, 0.58, 0.55),
        ("P-204", "West Junction Transit Hub", "Toronto", "Transit", "2025-09-15", "2027-03-30", 42_000_000, 0.67, 0.62),
        ("P-318", "Northfield Logistics Centre", "Brampton", "Industrial", "2026-02-02", "2026-11-27", 12_800_000, 0.73, 0.69),
        ("P-422", "Cedar Creek Watermain", "Vaughan", "Civil", "2025-11-10", "2026-08-21", 9_600_000, 0.81, 0.77),
        ("P-507", "King Street Clinic", "Hamilton", "Healthcare", "2026-03-02", "2027-01-15", 24_300_000, 0.39, 0.36),
    ], columns=["project_id", "project_name", "city", "sector", "start_date", "finish_date", "budget", "planned_progress", "actual_progress"])
    projects["schedule_variance_days"] = [-4, 11, 6, -2, 8]
    projects["start_date"] = pd.to_datetime(projects["start_date"])
    projects["finish_date"] = pd.to_datetime(projects["finish_date"])

    rng = np.random.default_rng(24)
    days = pd.date_range("2026-10-05", periods=28, freq="D")
    labor_rows = []
    equipment_rows = []
    for p in projects.itertuples():
        base = int(rng.integers(35, 90))
        for day in days:
            if day.dayofweek < 5:
                hours = max(0, int(rng.normal(base, 7)))
                earned = hours * float(rng.normal(1.03, 0.12))
                labor_rows.append((p.project_id, day, hours, round(earned, 1), round(hours * float(rng.uniform(58, 84)), 2)))
                units = int(rng.integers(3, 10))
                equipment_rows.append((p.project_id, day, units, int(rng.integers(20, 45)), int(rng.integers(2, 11))))
    labor = pd.DataFrame(labor_rows, columns=["project_id", "work_date", "labor_hours", "earned_units", "labor_cost"])
    equipment = pd.DataFrame(equipment_rows, columns=["project_id", "work_date", "active_units", "available_hours", "downtime_hours"])
    production_rows = []
    for p in projects.itertuples():
        for day in days:
            if day.dayofweek < 5:
                planned = int(rng.integers(18, 42))
                actual = max(0, int(rng.normal(planned * float(rng.uniform(.82, 1.12)), 4)))
                production_rows.append((p.project_id, day, "Wall panels", planned, actual, int(rng.binomial(actual, .035))))
    production = pd.DataFrame(production_rows, columns=["project_id", "work_date", "component_type", "planned_units", "actual_units", "rework_units"])
    materials = pd.DataFrame([
        (p.project_id, f"PO-{i:03d}", item, pd.Timestamp("2026-10-08") + pd.Timedelta(days=i % 9), pd.Timestamp("2026-10-27") + pd.Timedelta(days=i % 13), status, int(rng.integers(8, 36)), supplier)
        for i, (p, item, status, supplier) in enumerate([
            (projects.iloc[j], item, status, supplier)
            for j in range(len(projects))
            for item, status, supplier in [("Glulam beams", "On track", "North Timber Co."), ("Facade panels", "At risk", "ModuBuild Supply")]
        ], 1)
    ], columns=["project_id", "po_id", "material", "order_date", "expected_date", "status", "lead_time_days", "supplier"])
    documents = pd.DataFrame([
        ("DOC-001", "P-101", "Progress report", "2026-10-27", "Panel installation reached level 8. Crane availability constrained two shifts; recovery plan reviewed with site team.", "Site team"),
        ("DOC-002", "P-204", "Meeting minutes", "2026-10-24", "Long-lead facade submittal remains open. Design coordination workshop scheduled; procurement to confirm revised delivery date.", "Project controls"),
        ("DOC-003", "P-318", "Quality inspection", "2026-10-23", "Three wall panels held for dimensional review. Corrective action logged; re-inspection required before dispatch.", "Quality team"),
        ("DOC-004", "P-422", "Change request", "2026-10-21", "Utility conflict may affect the north work zone. Cost and schedule impacts are under assessment.", "Engineering"),
        ("DOC-005", "P-507", "Progress report", "2026-10-20", "Mock-up review complete. Minor sealant observations assigned; no release decision until close-out evidence is filed.", "Site team"),
        ("DOC-006", "P-101", "Meeting minutes", "2026-10-17", "Weekly coordination: confirm delivery sequence and ensure the latest approved shop drawing is used on the floor.", "Project controls"),
        ("DOC-007", "P-204", "Quality inspection", "2026-10-15", "Connection torque sampling completed. One record needs a traceable component identifier before acceptance.", "Quality team"),
        ("DOC-008", "P-318", "Change request", "2026-10-13", "Alternate loading sequence proposed to reduce double handling. Safety and logistics review pending.", "Engineering"),
    ], columns=["document_id", "project_id", "document_type", "document_date", "text", "owner"])
    return projects, labor, equipment, production, materials, documents
