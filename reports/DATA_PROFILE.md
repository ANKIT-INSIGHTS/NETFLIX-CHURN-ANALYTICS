# Data Profiling & Quality Report

This report documents a full column-by-column audit of `netflix_customer_churn.csv`,
in the style of a pre-analysis data quality check — the kind of step a data analyst
runs before trusting any downstream chart or model.

![Column overview](figures/column_overview.png)

---

## Dataset shape

| | |
|---|---|
| Rows | 5,000 |
| Columns | 14 |
| Duplicate rows | 0 |
| Missing values (any column) | 0 |
| Memory footprint | ~0.55 MB |

---

## Column-by-column profile

| Column | Type | Missing | Unique values | Summary |
|---|---|---|---|---|
| `customer_id` | string (UUID) | 0 | 5,000 (100%) | Fully unique — safe as a primary key |
| `age` | int | 0 | 53 | min 18, mean 43.9, median 44, max 70 — roughly uniform |
| `gender` | string | 0 | 3 | Female 34.2% · Male 33.1% · Other 32.7% — balanced |
| `subscription_type` | string | 0 | 3 | Premium 33.9% · Basic 33.2% · Standard 32.9% — balanced |
| `watch_hours` | float | 0 | 2,343 | min 0.01, mean 11.65, median 8.0, max 110.4 — **right-skewed, see anomaly below** |
| `last_login_days` | int | 0 | 61 | min 0, mean 30.1, median 30, max 60 — uniform 0–60 range |
| `region` | string | 0 | 6 | South America 17.5% · Europe 17.3% · N. America 17.0% · Asia 16.8% · Africa 16.1% · Oceania 15.3% |
| `device` | string | 0 | 5 | Tablet 21.0% · Laptop 20.1% · Mobile 20.1% · TV 19.9% · Desktop 19.0% |
| `monthly_fee` | float | 0 | 3 | Only 3 distinct values (8.99 / 13.99 / 17.99) — directly tied to `subscription_type` |
| `churned` | int (target) | 0 | 2 | 1 = 50.3% · 0 = 49.7% — well-balanced target, no resampling needed |
| `payment_method` | string | 0 | 5 | Debit Card 20.6% · PayPal 20.5% · Crypto 19.9% · Gift Card 19.5% · Credit Card 19.5% |
| `number_of_profiles` | int | 0 | 5 (1–5) | Roughly uniform, ~20% each |
| `avg_watch_time_per_day` | float | 0 | 505 | min 0.0, mean 0.87, median 0.29, max 98.42 — **right-skewed, see anomaly below** |
| `favorite_genre` | string | 0 | 7 | Nearly even split across all 7 genres (~13.9–14.6% each) |

---

## ⚠️ Data quality finding: implausible watch-time outliers

While profiling `avg_watch_time_per_day`, the 99th percentile is only **10.9 hours**,
but the column maximum is **98.42** — a physically implausible value (more than 24
hours of viewing in a single day). Investigating further:

- **10 rows (0.2% of customers)** have `avg_watch_time_per_day` > 24
- **25 rows (0.5%)** have `watch_hours` above the 99.5th percentile (>71)
- Every one of these rows also has `last_login_days` equal to 0 or 1

**Interpretation:** this pattern (impossible daily average + very recent login) suggests
these are either data-generation artifacts (this is a synthetic Kaggle dataset) or a
divide-by-a-very-small-number edge case in whatever formula produced
`avg_watch_time_per_day`. It is not evenly distributed noise — it is concentrated in a
specific, identifiable slice of rows.

**Recommendation for downstream analysis:**
- For visualizations, clip or log-scale `watch_hours` / `avg_watch_time_per_day` to
  avoid a handful of outliers compressing the rest of the distribution (done in
  `column_overview.png` above and in the EDA notebook).
- For modeling, tree-based models (Random Forest) are naturally robust to this kind of
  outlier via split-based partitioning. Linear models (Logistic Regression) are more
  sensitive since `StandardScaler` uses the mean/variance — worth re-validating
  coefficients with and without these 10–25 rows if this were a production dataset.
- **This is exactly the kind of finding that separates a "ran `.describe()` and moved
  on" analysis from a validated one.** Always check `max()` against the 95th/99th
  percentile before trusting a numeric column.

---

## Relationships worth noting

- `monthly_fee` is fully determined by `subscription_type` (Basic=$8.99, Standard=$13.99,
  Premium=$17.99) — treat these as one signal, not two independent features, when
  interpreting model coefficients or correlation output.
- `customer_id` is a high-cardinality unique identifier and should never be fed into a
  model as a feature (it is excluded in `src/churn_model.py`).
- All categorical columns are close to perfectly balanced across categories, which is
  a strong signal this dataset was synthetically generated rather than collected from
  a real subscriber base — useful context when interpreting "surprisingly small"
  demographic effects on churn (see Q4–Q6 in the EDA notebook).

---

*Generated as part of the `netflix-churn-analytics` project. Reproduce with the
profiling code in `src/data_loader.py` plus the column-overview chart script noted in
the main README.*
