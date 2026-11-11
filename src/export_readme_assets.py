"""Export reproducible synthetic CSVs and SVG charts for the README."""
from __future__ import annotations

import html
import math
from pathlib import Path

import pandas as pd

from src.demo_data import load_demo_data

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "graphs"
DATA = ROOT / "data" / "demo"
WIDTH, HEIGHT = 900, 440
TEAL, SLATE, INK, MUTED, GRID = "#087f8c", "#a9b8c8", "#17324d", "#66788a", "#e7edf2"


def esc(value: object) -> str:
    return html.escape(str(value))


def shell(title: str, subtitle: str, content: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="100%" height="100%" rx="18" fill="#ffffff"/>
<style>text{{font-family:Inter,Segoe UI,Arial,sans-serif}} .title{{font-size:23px;font-weight:700;fill:{INK}}} .sub{{font-size:13px;fill:{MUTED}}} .tick{{font-size:11px;fill:{MUTED}}} .label{{font-size:12px;fill:{INK}}} .grid{{stroke:{GRID};stroke-width:1}}</style>
<text x="34" y="42" class="title">{esc(title)}</text><text x="34" y="65" class="sub">{esc(subtitle)}</text>
{content}</svg>'''


def progress_chart(projects: pd.DataFrame) -> str:
    left, right, top, bottom = 235, 850, 112, 352
    plot_w = right-left
    rows = projects.sort_values("actual_progress").reset_index(drop=True)
    out = []
    for tick in range(0, 101, 20):
        x = left + plot_w*tick/100
        out.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" class="grid"/>')
        out.append(f'<text x="{x}" y="{bottom+22}" text-anchor="middle" class="tick">{tick}%</text>')
    row_h = (bottom-top)/len(rows)
    for i, row in rows.iterrows():
        y = top+i*row_h+row_h/2
        out.append(f'<text x="{left-12}" y="{y+4}" text-anchor="end" class="label">{esc(row.project_name)}</text>')
        for offset, key, color in [(-8,"planned_progress",SLATE),(8,"actual_progress",TEAL)]:
            val=float(row[key]); bw=plot_w*val
            out.append(f'<rect x="{left}" y="{y+offset-5}" width="{bw:.1f}" height="11" rx="5" fill="{color}"/>')
            out.append(f'<text x="{left+bw+7:.1f}" y="{y+offset+4}" class="tick">{val:.0%}</text>')
    out += [f'<rect x="{left}" y="395" width="12" height="12" rx="3" fill="{SLATE}"/><text x="{left+18}" y="406" class="tick">Planned</text>',
            f'<rect x="{left+100}" y="395" width="12" height="12" rx="3" fill="{TEAL}"/><text x="{left+118}" y="406" class="tick">Actual</text>']
    return shell("Planned vs. actual project progress", "Synthetic portfolio snapshot · status values are illustrative", "".join(out))


def line_chart(title: str, subtitle: str, series: list[tuple[str, list[float], str]], labels: list[str], y_label: str, suffix: str = "") -> str:
    left, right, top, bottom = 72, 860, 112, 355
    flat=[v for _, values, _ in series for v in values]
    low=min(flat); high=max(flat)
    pad=(high-low)*0.16 if high>low else max(abs(high)*0.16,1)
    low=max(0,low-pad); high=high+pad
    out=[]
    for j in range(5):
        value=low+(high-low)*j/4
        y=bottom-(bottom-top)*j/4
        out.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="grid"/>')
        out.append(f'<text x="{left-10}" y="{y+4}" text-anchor="end" class="tick">{value:.1f}{suffix}</text>')
    n=max(len(labels),1)
    for idx,label in enumerate(labels):
        if idx % max(1, math.ceil(n/7)) == 0 or idx==n-1:
            x=left+(right-left)*idx/max(n-1,1)
            out.append(f'<text x="{x}" y="{bottom+22}" text-anchor="middle" class="tick">{esc(label)}</text>')
    for name,values,color in series:
        points=[]
        for i,value in enumerate(values):
            x=left+(right-left)*i/max(len(values)-1,1)
            y=bottom-(bottom-top)*(value-low)/(high-low)
            points.append((x,y))
        out.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}"/>')
        for x,y in points:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')
    legend_x=left
    for name,_,color in series:
        out.append(f'<line x1="{legend_x}" y1="397" x2="{legend_x+20}" y2="397" stroke="{color}" stroke-width="3"/><text x="{legend_x+27}" y="401" class="tick">{esc(name)}</text>')
        legend_x += len(name)*7+72
    return shell(title, subtitle, "".join(out))


def main() -> None:
    projects, labor, equipment, production, materials, documents = load_demo_data()
    DATA.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    tables={"projects":projects,"labor_daily":labor,"equipment_daily":equipment,"production_daily":production,"procurement_orders":materials,"documents":documents}
    for name, frame in tables.items():
        frame.to_csv(DATA/f"{name}.csv",index=False)

    (ASSETS/"project_progress.svg").write_text(progress_chart(projects),encoding="utf-8")
    labor_daily=labor.groupby("work_date",as_index=False).agg({"earned_units":"sum","labor_hours":"sum"})
    labor_daily["productivity"]=labor_daily.earned_units/labor_daily.labor_hours
    date_labels=labor_daily.work_date.dt.strftime("%b %d").tolist()
    (ASSETS/"labor_productivity.svg").write_text(line_chart("Daily labor productivity","Synthetic project portfolio · earned units per labor hour",[("Productivity",labor_daily.productivity.tolist(),TEAL)],date_labels,"Earned units per labor hour"),encoding="utf-8")
    prod_daily=production.groupby("work_date",as_index=False)[["planned_units","actual_units"]].sum()
    prod_labels=prod_daily.work_date.dt.strftime("%b %d").tolist()
    (ASSETS/"production_plan_vs_actual.svg").write_text(line_chart("Daily planned and completed production","Synthetic component output · all selected projects",[("Planned",prod_daily.planned_units.tolist(),SLATE),("Completed",prod_daily.actual_units.tolist(),TEAL)],prod_labels,"Units"),encoding="utf-8")
    print(f"Exported {len(tables)} CSV datasets and 3 SVG charts.")


if __name__ == "__main__":
    main()
