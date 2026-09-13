# Tableau Guide — Netflix Churn Dashboard

This folder contains a Tableau-ready CSV export (`netflix_churn_tableau.csv`) with all
engineered fields pre-computed, plus the calculated fields and dashboard layout needed
to rebuild the analysis in Tableau Desktop or Tableau Public.

## 1. Connect the data

1. Tableau → **Connect → Text File** → select `netflix_churn_tableau.csv`.
2. On the data source screen, confirm field types:
   - `customer_id`, `gender`, `region`, `device`, `subscription_type`, `age_group`,
     `payment_method`, `favorite_genre`, `engagement_level`, `recency_flag`,
     `churn_status` → **String / Dimension**
   - `age`, `number_of_profiles`, `last_login_days`, `churned` → **Number (whole) / can act as Dimension or Measure**
   - `monthly_fee`, `annual_value`, `watch_hours`, `avg_watch_time_per_day`,
     `revenue_at_risk` → **Number (decimal) / Measure**
3. Right-click `churned` in the Data pane → convert to a Dimension so it can be used
   directly in filters/color legends without aggregation surprises.

## 2. Recommended calculated fields

Right-click in the Data pane → **Create Calculated Field** for each:

```
// Churn Rate (%) — use as a table calc or with LOD depending on the view
Churn Rate =
SUM([churned]) / COUNTD([customer_id])

// Revenue lost, already precomputed in the CSV as revenue_at_risk,
// but useful to have as a Tableau-native calc for what-if filtering:
Revenue at Risk (calc) =
IF [churned] = 1 THEN [monthly_fee] ELSE 0 END

// Flag for the "high risk" segment used throughout the project
High Risk Flag =
IF [engagement_level] = "Low" AND [recency_flag] = "At Risk" THEN "High Risk"
ELSEIF [engagement_level] = "High" AND [recency_flag] = "Active" THEN "Low Risk"
ELSE "Medium Risk"
END

// Bucketed watch-hours for outlier-safe histograms (see DATA_PROFILE.md)
Watch Hours (Capped) =
IF [watch_hours] > 71 THEN 71 ELSE [watch_hours] END

// Annualized revenue at risk
Annual Revenue at Risk =
[Revenue at Risk (calc)] * 12
```

## 3. Suggested worksheets

| Sheet name | Chart type | Fields |
|---|---|---|
| `Churn Overview` | Donut / Pie | `churn_status` (color + label), COUNTD(customer_id) |
| `Churn by Plan` | Horizontal bar | `subscription_type` (rows), Churn Rate (measure), sorted descending |
| `Churn by Region` | Filled map or bar | `region` (rows), Churn Rate |
| `Engagement Scatter` | Scatter plot | `avg_watch_time_per_day` (X), `last_login_days` (Y), color = `churn_status`, size = `monthly_fee` |
| `Engagement Tiers` | Bar | `engagement_level` (rows, sorted Low→High), Churn Rate |
| `Device x Plan Heatmap` | Highlight table | `device` (rows), `subscription_type` (columns), color = Churn Rate |
| `Revenue Waterfall` | Bar/Gantt | Total Revenue, Revenue at Risk, Net Revenue |
| `Customer Detail` | Text table | `customer_id`, `subscription_type`, `watch_hours`, `last_login_days`, `churn_status` — for drill-down |

## 4. Dashboard layout

Build one dashboard combining:
1. **Top strip** — 4 KPI text tiles: Total Customers, Churn Rate, Revenue at Risk, Avg Days Since Login (use "Single Value" worksheets with big bold text)
2. **Left panel** — `Engagement Scatter` (the highest-value single chart; visually separates at-risk vs loyal clusters)
3. **Right panel, stacked** — `Churn by Plan` and `Device x Plan Heatmap`
4. **Bottom strip** — `Revenue Waterfall`
5. **Filters shelf** (apply to all sheets via "Use as Filter" + Actions): `region`, `subscription_type`, `age_group`, `device`

## 5. Actions & interactivity

- Add a **Dashboard Action**: click a bar in `Churn by Plan` → filters `Customer Detail`
  table below it, so a presenter can drill from "Premium has high churn" straight to
  the actual customer rows.
- Add a **Highlight Action** on `engagement_level` so hovering one chart highlights the
  same customers across the scatter plot and heatmap.

## 6. Color palette (consistency with the rest of the project)

- Churned: `#E50914` (Netflix red)
- Retained: `#3FC17F` (green)
- Neutral/background bars: `#4C72B0` (blue)
- Use this 2–3 color palette consistently — avoid Tableau's default 10-color palette
  for a categorical field with only 2–3 meaningful states like churn status.

## 7. Known caveats to carry into the workbook

- `monthly_fee` has only 3 distinct values, fully determined by `subscription_type` —
  avoid double-encoding the same signal in one visual (e.g. don't color by
  `monthly_fee` AND facet by `subscription_type` in the same chart).
- See `reports/DATA_PROFILE.md`: ~0.2–0.5% of rows have implausible
  `avg_watch_time_per_day` / `watch_hours` values. Use the `Watch Hours (Capped)`
  calculated field above for any histogram or axis using raw watch-hours, or prefer
  the pre-binned `engagement_level` field where a clean categorical view will do.
