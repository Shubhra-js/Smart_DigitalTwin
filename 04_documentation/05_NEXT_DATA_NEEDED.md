# Extending the Twin — What Data Would Unlock What

The architecture (cleaning → indicators → risk → what-if → dashboard) is
generic and ready for more layers. Nothing below is built yet — it is a
scoped roadmap so the next data drop can be absorbed without a redesign.

| If you later supply... | It would unlock... |
|---|---|
| Substation GPS coordinates | Replace the curated/jittered map with a real geo-accurate infrastructure map |
| Outage / fault / maintenance log per substation | A genuine ML failure-risk model (logistic regression or survival model), replacing the current rule-based index |
| Taluk- or ward-level consumer & demand data | Real demand-supply stress mapping per taluk, instead of today's supply-side-only asset view |
| Daily/weekly (not monthly) air-quality readings | A meaningfully validated forecast model — 20× more training points for the same time span |
| Population / household data by ward | Per-capita consumption indicators, demand-growth tied to population growth rather than connection-count growth alone |
| Water supply / sewage infrastructure data | A parallel "water twin" layer using the exact same pipeline pattern |
| Traffic / mobility data | A congestion-linked NO2 exposure model (NO2 is already in the AQ dataset, currently unused beyond display) |

Each new dataset should go through the same 4-stage script pattern in
`05_analysis_ml/`: clean → derive indicators → decide monitoring/analysis/
risk/ML honestly based on what the data can support → feed into
`04_build_dashboard_dataset.py`.
