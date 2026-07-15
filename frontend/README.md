# Ethiopia Financial Inclusion — Frontend

React + Vite + Tailwind v4 dashboard for the Ethiopia Financial Inclusion
Forecasting project. Consumes the FastAPI backend in `../backend`, with a
static-JSON fallback in `public/data/` so the dashboard still works if no
backend is deployed (e.g. a Vercel-only demo).

## Design system
- **Palette**: deep navy canvas, warm gold for the Access pillar, teal for
  the Usage pillar, coral for gaps/alerts — a "financial terminal" feel
  suited to a DFI/central-bank/operator audience.
- **Type**: Fraunces (display), IBM Plex Sans (body), IBM Plex Mono (every
  number — tabular data should scan like a ledger).
- **Signature element**: the top ledger strip — its gold bar is literally
  the % progress from the base 2025 forecast to the NFIS-II 70% target,
  not decoration.

## Run locally

```bash
npm install
cp .env.example .env   # point VITE_API_URL at your backend, or leave as-is for localhost:8000
npm run dev             # http://localhost:5173
```

Start the backend separately for live data:
```bash
cd ../backend
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload --port 8000
```

Without a running backend, the dashboard automatically falls back to the
static snapshots in `public/data/` (generated from the same pipeline —
see `../src/`).

## Build & deploy

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally
```

Deploy `dist/` to Vercel/Netlify. Set `VITE_API_URL` as an environment
variable if pointing at a live backend (e.g. deployed on Render, matching
the pattern used for the Bati Bank Credit Risk dashboard).

## Pages
- **Overview** — 5 key insights, Access trajectory, gender gap
- **Trends** — indicator selector, date range, event-timeline overlay, CSV download
- **Forecasts** — scenario chart with confidence band, Telebirr/M-Pesa model validation
- **Projections** — scenario toggle vs. NFIS-II target, event×indicator association matrix
