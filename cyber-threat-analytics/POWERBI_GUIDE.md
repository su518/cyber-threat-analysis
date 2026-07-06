# Power BI Report — Build Guide

Two files to import (in `data/`):
- `incidents_for_powerbi.csv` — the 3,000 incidents, friendly column names, includes a `High Severity` flag
- `industry_risk_clusters.csv` — lookup table mapping each industry to its risk group (from the clustering analysis)

## Step 1: Load & relate

1. Power BI Desktop → **Get Data → Text/CSV** → import both files.
2. **Model view** → drag `Target Industry` (incidents table) to `Target Industry` (clusters table) to create the relationship.

## Step 2: Add these measures (Home → New Measure)

```
Total Financial Loss = SUM(incidents_for_powerbi[Financial Loss (Million USD)])

Total Incidents = COUNTROWS(incidents_for_powerbi)

Total Users Affected = SUM(incidents_for_powerbi[Users Affected])

Avg Resolution Time = AVERAGE(incidents_for_powerbi[Resolution Time (Hours)])

High Severity Incidents = 
CALCULATE([Total Incidents], incidents_for_powerbi[High Severity] = "High")

High Severity Rate = DIVIDE([High Severity Incidents], [Total Incidents])
```

## Step 3: Pages

**Page 1 — Executive Overview**
- 4 KPI cards across the top: `Total Incidents`, `Total Financial Loss`, `Total Users Affected`, `Avg Resolution Time`
- Line chart: `Year` (axis) vs `Total Incidents` (values) — the trend line your forecast script projects forward
- Bar chart: `Target Industry` (axis) vs `Total Financial Loss` (values), sorted descending
- Slicer: `Year` (so the whole page can be filtered by year range)

**Page 2 — Risk Grouping**
- Matrix or bar chart: `Risk Cluster` (axis) vs `Total Incidents` and `Total Financial Loss` (values) — shows the clustering result as a business-facing chart, not just a scatterplot
- Table: `Target Industry`, `Risk Cluster`, `Attack Source` (most common per industry — use a DAX measure or just a slicer-driven table)
- This page directly answers "which industries share our risk profile"

**Page 3 — Severity & Escalation**
- Donut chart: `High Severity` split (share of incidents that are "High")
- Scatter chart: `Financial Loss (Million USD)` (X) vs `Users Affected` (Y), colored by `High Severity` — visually shows the near-zero correlation your analysis found
- Table sorted by `Financial Loss (Million USD)` descending, filtered to `High Severity = High` — the "escalate these first" list

**Page 4 — Attack Patterns**
- Matrix: `Attack Source` (rows) vs `Vulnerability Type` (columns), values = count — the correlation structure from your analysis, as a heatmap-style matrix (conditional formatting → color scale)
- Bar chart: `Defense Mechanism` (axis) vs `Avg Resolution Time` (values) — a natural add-on question: does defense mechanism affect how fast incidents get resolved?

## Step 4: Polish

- Apply a single theme (View → Themes) — pick one and use it consistently across all 4 pages.
- Add page navigation buttons (Insert → Buttons → Page Navigation) so it feels like one report, not four disconnected pages.
- Publish, then grab the shareable link or export a PDF snapshot for your portfolio/GitHub (screenshot each page into the README).

## Why this structure

Each page maps to one of the business questions already in your GitHub README — reviewers can see the same analysis translated from Python/notebook into a BI tool, which is exactly the range Technica's posting asks for (Python/SQL tools *and* reporting/dashboarding).
