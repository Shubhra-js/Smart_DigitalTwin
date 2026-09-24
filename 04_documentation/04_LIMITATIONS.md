# Limitations & Curated-Data Disclosure

Stated up front, per the brief's instruction not to invent information or
unsupported claims.

## 1. No true GPS coordinates for substations
The source substation dataset has Zone/District/Taluk text only — no
lat/lon. `03_curated_reference_data/taluk_centroids_curated.csv` supplies
**approximate taluk-town centroid coordinates** (public geographic
knowledge, not measured/surveyed) so the dashboard map can render at all.
Each substation's plotted point is this centroid **plus random jitter**
(±0.025°, ~2.5km) purely so 280 points don't overlap — **individual pin
positions are not real locations**, only the taluk grouping is meaningful.
This is stated on the dashboard itself.

## 2. No taluk-level electricity demand data
Consumer counts, units sold, and losses are only available at whole-city
(BESCOM-wide) level in the source data. The taluk-level view in the
Infrastructure tab is therefore a **supply-side / asset-condition view
only** (substation count, age, risk) — the twin does **not** claim to know
which taluk has a demand-supply electricity gap, because that data was not
provided.

## 3. CPCB AQI bands are a published external reference, not measured data
`03_curated_reference_data/aqi_category_reference_CPCB.csv` reproduces the
publicly published CPCB India National AQI category breakpoints (Good /
Satisfactory / Moderate / Poor / Very Poor / Severe), used only to label
this project's *monthly mean* concentrations for interpretability. The
official CPCB AQI is defined on a 24-hour average, so applying the same
bands to a monthly mean is an approximation, explicitly flagged wherever it
appears.

## 4. Time series are short everywhere except Air Quality
Most BESCOM tables are single-year snapshots or 2–3 year comparisons. Growth
rates and cost trends shown are the **actual reported %-change figures** in
those tables, not fitted models — treat multi-year projections (What-if
tab) as scenario arithmetic, not statistical forecasts.

## 5. Reference/analysis year
Substation "asset age" is computed against 2026 (this project's build year)
since the dataset itself carries no "as-of" date; commission dates
themselves are exactly as given in the source file.

## 6. Scope
All 7 datasets are electricity-grid (BESCOM) or air-quality (CPCB) data. No
water, traffic/mobility, waste, or population dataset was supplied, so this
digital twin models those two layers only. See `05_NEXT_DATA_NEEDED.md`.
