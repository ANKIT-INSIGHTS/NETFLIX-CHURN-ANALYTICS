# Power BI Guide — Netflix Churn Dashboard

This folder contains a BI-ready CSV export (`netflix_churn_powerbi.csv`) with all the
engineered fields pre-computed, plus the DAX measures and dashboard layout needed to
rebuild the analysis as a Power BI report.

## 1. Import the data

1. Power BI Desktop → **Get Data → Text/CSV** → select `netflix_churn_powerbi.csv`.
2. In Power Query Editor, confirm column types:
   - `customer_id` → Text
   - `age`, `number_of_profiles`, `last_login_days`, `churned` → Whole Number
   - `monthly_fee`, `annual_value`, `watch_hours`, `avg_watch_time_per_day`, `revenue_at_risk` → Decimal Number
   - Everything else (`gender`, `region`, `device`, `subscription_type`, `age_group`,
     `payment_method`, `favorite_genre`, `engagement_level`, `recency_flag`,
     `churn_status`) → Text
3. **Close & Apply.**

## 2. Recommended DAX measures

Create these in a new measures table (Modeling → New Table → name it `_Measures`, then
add each as New Measure):

```dax
Total Customers = COUNTROWS('netflix_churn_powerbi')

Churned Customers = CALCULATE([Total Customers], 'netflix_churn_powerbi'[churned] = 1)

Churn Rate % =
DIVIDE([Churned Customers], [Total Customers], 0)

Retained Customers = [Total Customers] - [Churned Customers]

Total Monthly Revenue = SUM('netflix_churn_powerbi'[monthly_fee])

Revenue at Risk = SUM('netflix_churn_powerbi'[revenue_at_risk])

Revenue at Risk % = DIVIDE([Revenue at Risk], [Total Monthly Revenue], 0)

Avg Watch Hours = AVERAGE('netflix_churn_powerbi'[watch_hours])

Avg Daily Watch Time = AVERAGE('netflix_churn_powerbi'[avg_watch_time_per_day])

Avg Days Since Login = AVERAGE('netflix_churn_powerbi'[last_login_days])

At-Risk Customers = CALCULATE([Total Customers], 'netflix_churn_powerbi'[recency_flag] = "At Risk")

High Engagement Churn Rate =
CALCULATE([Churn Rate %], 'netflix_churn_powerbi'[engagement_level] = "High")

Low Engagement Churn Rate =
CALCULATE([Churn Rate %], 'netflix_churn_powerbi'[engagement_level] = "Low")

Churn Rate % (Formatted) = FORMAT([Churn Rate %], "0.0%")
```

## 3. Suggested report pages & visuals

### Page 1 — Executive Overview
- **KPI cards** (top row): Total Customers, Churn Rate %, Revenue at Risk, Avg Days Since Login
- **Donut chart**: `churn_status` split
- **Clustered bar chart**: Churn Rate % by `subscription_type`
- **Clustered bar chart**: Churn Rate % by `region`
- **Slicers**: `subscription_type`, `region`, `device`, `age_group` (synced across pages)

### Page 2 — Engagement Deep-Dive
- **Scatter chart**: `avg_watch_time_per_day` (X) vs `last_login_days` (Y), colored by `churn_status`, sized by `monthly_fee` — this is the single most useful chart since it visually separates the "at-risk cluster" (low X, high Y) from loyal customers
- **Matrix/heatmap visual**: rows = `device`, columns = `subscription_type`, values = Churn Rate %
- **Line/area chart**: Churn Rate % by `engagement_level` (Low/Medium/High) — should show a clear downward staircase
- **Histogram**: `watch_hours` distribution split by `churn_status` (note: consider excluding the top 0.5% outliers per `reports/DATA_PROFILE.md`)

### Page 3 — Revenue Impact
- **Waterfall or bar chart**: Total Revenue → Revenue at Risk → Net Retained Revenue
- **Table**: Revenue at Risk by `subscription_type`, sorted descending
- **Card**: Estimated annual revenue impact (`Revenue at Risk` × 12)
- **Bar chart**: Churn Rate % by `payment_method`

### Page 4 — Customer Explorer
- **Table/matrix** with drillthrough: list individual customers with `customer_id`,
  `subscription_type`, `watch_hours`, `last_login_days`, `churn_status` — filterable by
  the slicers on Page 1, useful for spot-checking specific accounts

## 4. Formatting tips

- Use a **dark theme** with Netflix red (`#E50914`) as the single accent color for
  anything churn-related, and a neutral green/gray for "retained" to keep the visual
  language consistent with the rest of this project.
- Apply **conditional formatting** (red/green background) to the Churn Rate % column
  in any table/matrix visual.
- Pin the KPI cards row and add a **bookmark** that resets all slicers, for demo/presentation use.

## 5. Known caveats to carry into the report

- `monthly_fee` has only 3 distinct values and is fully determined by
  `subscription_type` — don't treat them as independent dimensions in the same chart.
- See `reports/DATA_PROFILE.md` for the outlier finding in `watch_hours` /
  `avg_watch_time_per_day` — consider adding a filter to exclude the top 0.5% in any
  visual using those raw fields, or use `engagement_level` (already tertile-binned)
  instead where a clean categorical view is preferable.
