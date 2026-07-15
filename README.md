# Ethiopia Financial Inclusion Forecasting

A forecasting system for Ethiopia's digital financial transformation, built for
Selam Analytics' consortium of stakeholders (development finance institutions,
mobile money operators, the National Bank of Ethiopia). Forecasts the two
Global Findex pillars -- **Access** (Account Ownership Rate) and **Usage**
(Digital Payment Adoption Rate) -- for 2025-2027, and models how policies,
product launches, and infrastructure investments drive those outcomes.

## Quickstart

```bash
pip install -r requirements.txt

# Run the analytical pipeline (Tasks 1-4)
python src/data_loader.py      # load + schema-validate the unified dataset
python src/eda.py              # coverage summary, 5 key insights, figures -> reports/figures/
python src/event_impact.py     # event x indicator association matrix + Telebirr validation
python src/forecasting.py      # forecast table (base/optimistic/pessimistic, 2025-2027)

# Run tests
pytest tests/ -v

# Dashboard (Task 5) — FastAPI backend + React frontend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
# in a second terminal:
cd frontend && npm install && npm run dev   # http://localhost:5173
```

The frontend works even without the backend running (falls back to static
JSON snapshots in `frontend/public/data/`) — useful for a Vercel-only demo
deploy. See `frontend/README.md` for the design system and deploy notes.

## Project Structure

```
ethiopia-fi-forecast/
├── data/
│   ├── raw/                          # ethiopia_fi_unified_data.csv, reference_codes.csv
│   └── processed/                    # event_indicator_matrix.csv, forecast_table.csv (generated)
├── src/
│   ├── data_loader.py                # load, dtype, schema-validate the unified dataset
│   ├── eda.py                        # coverage, trends, gender gap, event overlays, 5 insights
│   ├── event_impact.py               # association matrix + lagged event-effect model
│   └── forecasting.py                # trend + event-augmented forecasts, 3 scenarios, CIs
├── backend/
│   ├── main.py                       # FastAPI: wraps src/ pipeline as 8 JSON endpoints
│   └── requirements.txt
├── frontend/                         # React + Vite + Tailwind v4 dashboard (see its README)
│   ├── src/
│   │   ├── components/               # Sidebar, LedgerStrip, Panel, MetricCard, Loading, ErrorState
│   │   ├── pages/                    # Overview, Trends, Forecasts, Projections
│   │   └── lib/api.js                # live backend + static-fallback data client
│   └── public/data/                  # static JSON snapshots (fallback / offline demo)
├── notebooks/                        # 01-04, executed with real outputs, mirror src/ modules
├── tests/
│   └── test_pipeline.py              # 10 tests covering schema, model validation, forecast sanity
├── reports/
│   ├── figures/                      # generated PNGs (access trajectory, event overlays)
│   └── impact_links_methodology.md   # evidence basis + limitations for every impact_link
└── data_enrichment_log.md            # documents every record added beyond the starter dataset
```

## What the model does

1. **Data layer** (`data_loader.py`) -- loads the unified `record_type` schema
   (`observation` / `target` / `event` / `impact_link`) and validates every
   categorical field against `reference_codes.csv`.
2. **EDA** (`eda.py`) -- coverage and confidence summaries, the Access
   trajectory (2011-2024), event-timeline overlays, and five data-grounded
   insights (e.g. why +65M mobile money accounts produced only +3pp Access
   growth).
3. **Event impact model** (`event_impact.py`) -- turns `impact_link` records
   into an event x indicator association matrix, and an `event_effect_at()`
   function that ramps each event's effect in via a logistic curve centered
   on `event_date + lag_months`. **Validated**: the modeled Telebirr + M-Pesa
   effect on mobile money account ownership lands within 0.3pp of the actual
   2024 Findex figure (9.14% modeled vs. 9.45% observed).
4. **Forecasting** (`forecasting.py`) -- baseline trend regression (OLS on
   Findex survey points) plus the *incremental* event effect accrued after
   the last observation (explicitly avoids double-counting events already
   reflected in the historical trend). Three scenarios scale the event
   contribution 0.5x/1.0x/1.5x; confidence intervals widen with horizon.
5. **Dashboard** (`dashboard/app.py`) -- 4 pages, 4+ interactive Plotly
   visualizations, CSV downloads, and a scenario selector against the
   NFIS-II 70% Access target.

## Key findings (see `reports/impact_links_methodology.md` for full detail)

- Account ownership growth decelerated sharply (+13pp, +11pp, then only +3pp
  in the most recent Findex round) despite mobile money accounts more than
  doubling -- explained by Ethiopia's near-zero mobile-money-only user rate,
  so most new registrants were already banked.
- Base-case 2025 Access forecast (54.6%) falls **~15pp short** of the
  NFIS-II 70% target.
- The largest-magnitude modeled events (Fayda ID, M-Pesa/EthSwitch
  interoperability, EthioPay) all launched in 2024-2025 with no post-period
  Findex data yet -- 2026-2027 forecasts lean heavily on literature-based,
  not empirically validated, event effects. Treat the optimistic/pessimistic
  spread as the honest range, not the base case as a confident point estimate.

## Known data gaps / next steps

- `USG_DIGITAL_PAYMENT` (the Usage forecast target) has only **one**
  historical observation (35%, 2024) -- there is no fitted trend, only a
  flat-line fallback (flagged in the dashboard and in `forecast_table.csv`
  via `trend_is_single_point_fallback`). Sourcing a 2021 or earlier
  digital-payment figure from Findex microdata would materially improve
  this forecast.
- Urban/rural disaggregation and Sheets B-D of the enrichment guide
  (agent density, POS terminals, smartphone penetration, etc.) were not
  yet incorporated -- see `data_enrichment_log.md` for what's included
  vs. still open.
