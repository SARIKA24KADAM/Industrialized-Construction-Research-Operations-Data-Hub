from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from src.demo_data import load_demo_data
from src.quality import profile_quality

st.set_page_config(page_title="Construction Operations Data Hub", page_icon="🏗️", layout="wide")
st.title("Construction Operations Data Hub")
st.caption("Integrated portfolio signals for delivery, labor productivity, equipment utilization, and data health · synthetic demo data")

projects, labor, equipment, production, materials, documents = load_demo_data()
quality = profile_quality(projects, labor, equipment, production, materials, documents)

st.sidebar.header("Portfolio filters")
sectors = st.sidebar.multiselect("Sector", sorted(projects.sector.unique()), default=sorted(projects.sector.unique()))
chosen = st.sidebar.multiselect("Project", projects.loc[projects.sector.isin(sectors), "project_name"].tolist(), default=projects.loc[projects.sector.isin(sectors), "project_name"].tolist())
filtered = projects[projects.project_name.isin(chosen)]
ids = filtered.project_id
labor_f = labor[labor.project_id.isin(ids)]
equip_f = equipment[equipment.project_id.isin(ids)]

tab_overview, tab_production, tab_search, tab_quality, tab_governance = st.tabs(["Portfolio overview", "Production & procurement", "Information search", "Data quality", "Governance"])
with tab_overview:
    if filtered.empty:
        st.info("Select at least one project to view portfolio indicators.")
    else:
        total_budget = filtered.budget.sum()
        weighted_progress = (filtered.actual_progress * filtered.budget).sum() / total_budget
        avg_variance = filtered.schedule_variance_days.mean()
        productivity = labor_f.earned_units.sum() / labor_f.labor_hours.sum() if labor_f.labor_hours.sum() else 0
        utilization = 1 - equip_f.downtime_hours.sum() / equip_f.available_hours.sum() if equip_f.available_hours.sum() else 0
        a, b, c, d, e = st.columns(5)
        a.metric("Active projects", f"{len(filtered)}")
        b.metric("Budget represented", f"${total_budget/1e6:,.1f}M")
        c.metric("Budget-weighted progress", f"{weighted_progress:.0%}")
        d.metric("Mean schedule variance", f"{avg_variance:+.1f} days")
        e.metric("Equipment availability", f"{utilization:.0%}")

        left, right = st.columns(2)
        with left:
            st.subheader("Planned vs. actual progress")
            p = filtered.melt(id_vars="project_name", value_vars=["planned_progress", "actual_progress"], var_name="Measure", value_name="Progress")
            p["Measure"] = p["Measure"].map({"planned_progress": "Planned", "actual_progress": "Actual"})
            st.plotly_chart(px.bar(p, x="project_name", y="Progress", color="Measure", barmode="group", labels={"project_name": "Project", "Progress": "Progress", "Measure": ""}, color_discrete_sequence=["#a9b8c8", "#087f8c"]), use_container_width=True)
        with right:
            st.subheader("Daily labor productivity")
            trend = labor_f.groupby("work_date", as_index=False).agg({"earned_units": "sum", "labor_hours": "sum"})
            trend["Productivity"] = trend.earned_units / trend.labor_hours
            st.plotly_chart(px.line(trend, x="work_date", y="Productivity", markers=True, labels={"work_date": "Work date", "Productivity": "Earned units per labor hour"}, color_discrete_sequence=["#087f8c"]), use_container_width=True)
            st.metric("Portfolio productivity", f"{productivity:.2f} earned units / labor hour")

        st.subheader("Project delivery snapshot")
        view = filtered[["project_name", "city", "sector", "planned_progress", "actual_progress", "schedule_variance_days", "budget"]].copy()
        view["Progress gap"] = view.actual_progress - view.planned_progress
        view = view.rename(columns={"project_name": "Project", "schedule_variance_days": "Schedule variance (days)", "budget": "Budget"})
        st.dataframe(view, hide_index=True, use_container_width=True, column_config={"planned_progress": st.column_config.ProgressColumn("Planned", format="percent", min_value=0, max_value=1), "actual_progress": st.column_config.ProgressColumn("Actual", format="percent", min_value=0, max_value=1), "Progress gap": st.column_config.NumberColumn(format="%+.0%"), "Budget": st.column_config.NumberColumn(format="$%.0f")})

with tab_quality:
    st.subheader("Source validation results")
    st.caption("Checks run in memory before the dashboard aggregates the demonstration inputs.")
    failed = int(quality["Failed rows"].sum())
    (st.success if failed == 0 else st.error)(f"{'All checks passed' if failed == 0 else f'{failed} failed rows detected'} across {len(quality)} checks.")
    st.dataframe(quality, hide_index=True, use_container_width=True)
    st.subheader("Source coverage")
    st.write(f"Projects: {len(projects):,} · Labor: {len(labor):,} project-days · Equipment: {len(equipment):,} · Production: {len(production):,} · Purchase orders: {len(materials):,} · Documents: {len(documents):,}")
    st.write(f"Labor date window: {labor.work_date.min():%b %d, %Y} to {labor.work_date.max():%b %d, %Y}")

with tab_production:
    prod_f = production[production.project_id.isin(ids)]
    material_f = materials[materials.project_id.isin(ids)]
    if filtered.empty:
        st.info("Select at least one project to view production and procurement signals.")
    else:
        prod_f = prod_f.merge(filtered[["project_id", "project_name"]], on="project_id")
        prod_f["Attainment"] = prod_f.actual_units / prod_f.planned_units.replace(0, pd.NA)
        p1, p2, p3 = st.columns(3)
        p1.metric("Units produced", f"{prod_f.actual_units.sum():,}")
        p2.metric("Plan attainment", f"{prod_f.actual_units.sum()/prod_f.planned_units.sum():.0%}" if prod_f.planned_units.sum() else "—")
        p3.metric("Rework share", f"{prod_f.rework_units.sum()/prod_f.actual_units.sum():.1%}" if prod_f.actual_units.sum() else "—")
        chart = prod_f.groupby("work_date", as_index=False)[["planned_units", "actual_units"]].sum().melt("work_date", var_name="Measure", value_name="Units")
        st.plotly_chart(px.line(chart, x="work_date", y="Units", color="Measure", markers=True, title="Daily planned and completed units", color_discrete_sequence=["#a9b8c8", "#087f8c"]), use_container_width=True)
        st.subheader("Long-lead procurement watchlist")
        st.dataframe(material_f.merge(filtered[["project_id", "project_name"]], on="project_id")[["project_name", "po_id", "material", "supplier", "status", "expected_date", "lead_time_days"]], hide_index=True, use_container_width=True)

with tab_search:
    docs_f = documents[documents.project_id.isin(ids)].merge(filtered[["project_id", "project_name"]], on="project_id")
    query = st.text_input("Search sample reports, minutes, inspections, and change requests", placeholder="Try: delivery, quality, crane, change…")
    types = st.multiselect("Document type", sorted(docs_f.document_type.unique()), default=sorted(docs_f.document_type.unique())) if not docs_f.empty else []
    matches = docs_f[docs_f.document_type.isin(types)]
    if query.strip():
        terms = [term for term in query.lower().split() if term]
        mask = matches.text.str.lower().apply(lambda value: all(term in value for term in terms))
        matches = matches[mask]
    st.caption("Keyword search over synthetic document excerpts and metadata; no external search service or AI model is connected.")
    if matches.empty:
        st.info("No matching documents in the selected project scope.")
    else:
        for doc in matches.sort_values("document_date", ascending=False).itertuples():
            with st.expander(f"{doc.document_type} · {doc.project_name} · {doc.document_date}"):
                st.write(doc.text)
                st.caption(f"{doc.document_id} · Owner: {doc.owner}")

with tab_governance:
    st.subheader("Governance at a glance")
    st.info("This demonstration contains synthetic data only. Aggregate productivity indicators are intended for project-level operational learning, not individual worker ranking.")
    st.markdown("""
    - **Project controls:** project controls owns schedule and budget definitions; resolve source conflicts with the project manager.
    - **Labor records:** the labor source owner approves access and permitted aggregation. Exclude names and employee identifiers from portfolio reporting by default.
    - **Equipment records:** equipment operations owns availability and downtime definitions, including treatment of planned maintenance.
    - **Data platform:** record source, owner, load time, schema version, validation result, and correction history for each production load.
    - **Use and retention:** apply least-privilege access, approved retention periods, and documented correction paths before connecting real systems.
    """)
    st.markdown("See `docs/governance.md` for the starter control register and `docs/architecture.md` for the proposed integration pattern.")
