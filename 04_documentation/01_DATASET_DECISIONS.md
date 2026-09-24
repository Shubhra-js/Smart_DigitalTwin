# Per-Dataset Decisions

For each dataset: what was inspected, what was kept/removed and why, which
Smart-City indicators it yields, which city problem it addresses, which use
type it serves (monitoring / analysis / prediction / risk-stress /
simulation), and the ML decision.

---
## 1. Energy Requirement (`BESCOM_1_EnergyRequirement_raw.csv` → `energy_requirement_cleaned.csv`)
**Shape:** 5 rows × 4 cols, single year (FY2015-16), Approved vs Actual.

- **Kept:** metric, approved_fy1516, actual_fy1516, + derived `achievement_pct`.
- **Removed:** `Sl. No.` (row identifier, no analytical value).
- **Indicators:** Energy Sales (MU), Distribution Loss (%), Transmission Loss (%), Energy Required (MU), Plan-Achievement (%).
- **City problem addressed:** How much electricity Bengaluru's grid actually needs vs. how much was planned for, and how much is lost in the network before reaching consumers.
- **Use type:** **Monitoring** (plan-vs-actual gap) and **Analysis** (loss indicator baseline for the What-if simulator).
- **ML decision: NOT USED.** 5 rows, one year — there is nothing to train or validate a model against. Used as-is for KPI cards and as the numeric baseline for loss-reduction what-if scenarios.

---
## 2. Number of Consumers (`BESCOM_2_Consumers_raw.csv` → `consumers_cleaned.csv`)
**Shape:** printed-report layout (LT/HT sections, FY16 vs FY15) → reshaped to 14 tidy rows.

- **Kept:** category (LT/HT/TOTAL), subcategory (Domestic/Commercial/Industrial/Others/Agriculture/Totals), fy16, fy15, pct_change, and unit-normalised `fy16_count`/`fy15_count` (Lakhs → absolute, so LT and HT are on one comparable scale).
- **Removed:** blank section-header rows ("LT"/"HT" title rows with no data) and the printed row-index column.
- **Indicators:** consumer base by category, YoY consumer growth rate (%).
- **City problem addressed:** How fast is demand (measured by number of connections) growing, and in which segment (residential vs commercial vs industrial vs agricultural)?
- **Use type:** **Analysis** (segment growth comparison) and **Simulation input** (the observed 7.42% total LT+HT growth rate is the default slider baseline in the What-if simulator).
- **ML decision: NOT USED (as ML).** Only 2 time points (FY15, FY16) per segment — a regression on 2 points is not a fitted model, it's a straight line; we use the *documented* compound-growth formula transparently in the simulator instead of dressing it up as ML.

---
## 3. Number of Units Sold (`BESCOM_3_UnitsSold_raw.csv` → `units_sold_cleaned.csv`)
**Shape:** same layout as Consumers, reshaped to 13 tidy rows, in MU.

- **Kept:** category, subcategory, fy16_MU, fy15_MU, pct_change.
- **Removed:** blank section headers, row-index column.
- **Indicators:** electricity consumption (MU) by segment, YoY consumption growth (%).
- **City problem addressed:** Actual energy draw by segment — distinct from consumer *count* growth, because usage growth can diverge from connection growth (e.g. HT industrial units sold fell -3.3% even as HT industrial connections likely didn't).
- **Use type:** **Analysis** and **Simulation input** (3.79% LT+HT growth used to project future energy requirement).
- **ML decision: NOT USED**, same reasoning as Consumers (2 time points).

---
## 4. Operating Ratio (`BESCOM_4_OperatingRatio_raw.csv` → `operating_ratio_cleaned.csv`)
**Shape:** 8 cost components × 3 years (FY14–FY16), all as % of total operating cost.

- **Kept:** cost_component, fy14_pct, fy15_pct, fy16_pct.
- **Removed:** `Sl. No`, and the "Total" row (always exactly 100% by construction — an invariant, not information).
- **Indicators:** cost-structure trend (power purchase %, transmission %, O&M %, employee cost %, R&M %, admin %, depreciation %, interest %).
- **City problem addressed:** Where BESCOM's money goes, and whether the utility is investing more in maintenance/upgrade (R&M rose from 0.41% to 2.08% of cost, FY15→FY16 — a signal of increasing repair activity, consistent with an ageing asset base) vs pure power procurement.
- **Use type:** **Analysis** (3-year trend line, shown in the dashboard).
- **ML decision: NOT USED.** 3 points per series is too short to fit a trend model reliably; shown as a transparent trend chart instead.

---
## 5. Renewable Energy Purchase (`BESCOM_5_RE_Purchase_raw.csv` → `re_purchase_cleaned.csv`)
**Shape:** 12 rows, single year (2015-16), by source.

- **Kept:** source, energy_mu, amount_crore, rs_per_unit, + derived `is_aggregate_row` flag (marks Total/solar/Non-Solar rows so they aren't double-counted against individual sources in charts).
- **Removed:** nothing (all rows retained, just flagged).
- **Indicators:** renewable energy mix (MU by source), purchase cost (₹/unit by source), solar share of total RE.
- **City problem addressed:** Sustainability of the grid's energy mix and the cost premium/discount of each renewable source (e.g. Wind at ₹3.58/unit vs Solar-bundled at ₹10.61/unit in this dataset).
- **Use type:** **Monitoring** (sustainability snapshot) and **Simulation input** (solar-share slider in What-if tab).
- **ML decision: NOT USED.** Single-year snapshot, no time series.

---
## 6. Bengaluru Electrical Substations (`BESCOM_6_Substations_raw.csv` → `substations_cleaned.csv`)
**Shape:** 280 rows × 7 cols → cleaned to 280 × 10.

- **Kept:** district, taluk, substation_name, voltage_kv, commission_date, commission_year, derived `asset_age_years` (reference year 2026) and `infrastructure_tier` (Transmission EHV ≥220kV vs Distribution 66kV).
- **Removed:** `Sl. No.` (identifier); `Zone` (100% constant value "Bengaluru" across all 280 rows — zero information).
- **Corrected:** inconsistent district/taluk spellings found in the raw file (`CB Pura`/`C B pura` → `Chikkaballapur`; `Bengaluru Urban` → `Bangalore Urban`; `DB pura` → `Doddaballapura`, cross-checked against the actual substation names in those rows, e.g. "D B Pura", "KIADB (D B Pura)").
- **Indicators:** substation count and density per taluk, asset-age distribution, voltage-tier mix.
- **City problem addressed:** Physical grid infrastructure coverage and ageing — this is the **only genuinely spatial, asset-level dataset** you supplied, and is the backbone of the map and the risk index.
- **Use type:** **Monitoring** (asset registry) + **Risk/Stress Assessment** (rule-based age/tier risk score — see `02_RISK_METHODOLOGY.md`).
- **ML decision: NOT USED (deliberately).** There is no outage/failure/load history for these substations, so there is no valid label to train a predictive "will this substation fail" model on. Forcing a classifier here would mean inventing labels — explicitly against the brief. A transparent rule-based index was used instead.
- **Missing data:** 1 row has no commission date at all (age unknown, kept as null, not guessed); the 2 rows above age-NaN handling use fleet-median age-risk as a documented conservative default.

---
## 7. Air Quality, Bengaluru 2017–2018 (`AirQuality_Bengaluru_2017to2018_raw.csv` → `air_quality_cleaned.csv`)
**Shape:** 24 monthly rows, Jan-2017 to Dec-2018.

- **Kept:** date, pm25, pm10, no2, so2, o3, sensor_count.
- **Removed:** nothing (`city` retained though constant — kept deliberately so the schema can extend to other cities later without redesign).
- **Cleaned:** `O3` had the literal text "NA" for 16 months (sensor not yet deployed pre-Jun-2018) — parsed to a real null rather than 0, so downstream analysis doesn't learn a false "O3 drops to zero" pattern.
- **Indicators:** monthly PM2.5, PM10, NO2, SO2, O3 concentrations; sensor deployment count (grew from 16→21 mid-2018).
- **City problem addressed:** Ambient air-quality trend and seasonality (visibly worse Nov–Feb "winter smog" pattern, better Jun–Sep monsoon months, in the actual data).
- **Use type:** **Monitoring**, **Analysis** (seasonality), and **Prediction** (the one dataset in this project with a genuine time series long enough to justify an ML model).
- **ML decision: USED.** See `03_AQI_FORECAST_MODEL.md` for full model description, features, and — importantly — its honestly-reported low holdout accuracy.
