"""Small, transparent data quality checks for the synthetic source tables."""
from __future__ import annotations

import pandas as pd


def profile_quality(projects: pd.DataFrame, labor: pd.DataFrame, equipment: pd.DataFrame, production: pd.DataFrame | None = None, materials: pd.DataFrame | None = None, documents: pd.DataFrame | None = None) -> pd.DataFrame:
    project_ids = set(projects["project_id"])
    checks = [
        ("Projects", "Required values present", int(projects[["project_id", "project_name", "budget"]].isna().sum().sum()), "Fail if > 0"),
        ("Projects", "Unique project key", int(projects["project_id"].duplicated().sum()), "Fail if > 0"),
        ("Projects", "Positive budget", int((projects["budget"] <= 0).sum()), "Fail if > 0"),
        ("Labor", "Unique project and date", int(labor.duplicated(["project_id", "work_date"]).sum()), "Fail if > 0"),
        ("Labor", "Project key resolves", int((~labor["project_id"].isin(project_ids)).sum()), "Fail if > 0"),
        ("Labor", "Non-negative hours and cost", int(((labor["labor_hours"] < 0) | (labor["labor_cost"] < 0)).sum()), "Fail if > 0"),
        ("Equipment", "Unique project and date", int(equipment.duplicated(["project_id", "work_date"]).sum()), "Fail if > 0"),
        ("Equipment", "Downtime within available hours", int((equipment["downtime_hours"] > equipment["available_hours"]).sum()), "Fail if > 0"),
    ]
    if production is not None:
        checks.extend([
            ("Production", "Unique project, date, component", int(production.duplicated(["project_id", "work_date", "component_type"]).sum()), "Fail if > 0"),
            ("Production", "Rework does not exceed output", int((production["rework_units"] > production["actual_units"]).sum()), "Fail if > 0"),
            ("Production", "Project key resolves", int((~production["project_id"].isin(project_ids)).sum()), "Fail if > 0"),
        ])
    if materials is not None:
        checks.extend([
            ("Procurement", "Unique purchase order", int(materials["po_id"].duplicated().sum()), "Fail if > 0"),
            ("Procurement", "Expected date on or after order date", int((materials["expected_date"] < materials["order_date"]).sum()), "Fail if > 0"),
        ])
    if documents is not None:
        checks.extend([
            ("Documents", "Unique document identifier", int(documents["document_id"].duplicated().sum()), "Fail if > 0"),
            ("Documents", "Project key resolves", int((~documents["project_id"].isin(project_ids)).sum()), "Fail if > 0"),
            ("Documents", "Document text present", int(documents["text"].isna().sum()), "Fail if > 0"),
        ])
    return pd.DataFrame(checks, columns=["Source", "Check", "Failed rows", "Rule"])
