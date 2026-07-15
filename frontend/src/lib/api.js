// API client: tries the live FastAPI backend first (VITE_API_URL, default
// localhost:8000), and falls back to the static JSON snapshots bundled in
// /public/data/ if the backend isn't running. Keeps the dashboard usable as
// a static demo (e.g. on Vercel with no backend deployed) while still
// working live in local dev.

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function tryLive(path) {
  const res = await fetch(`${API_BASE}${path}`, { signal: AbortSignal.timeout(2500) })
  if (!res.ok) throw new Error(`${path} -> ${res.status}`)
  return res.json()
}

async function fallback(staticPath) {
  const res = await fetch(staticPath)
  if (!res.ok) throw new Error(`No fallback for ${staticPath}`)
  return res.json()
}

async function get(livePath, staticPath) {
  try {
    return await tryLive(livePath)
  } catch {
    return fallback(staticPath)
  }
}

export const api = {
  overview: () => get("/api/overview", "/data/overview.json"),
  indicators: () => get("/api/indicators", "/data/indicators.json"),
  trends: (code) => get(`/api/trends/${code}`, `/data/trends/${code}.json`),
  genderGap: () => get("/api/gender-gap", "/data/gender-gap.json"),
  forecast: () => get("/api/forecast", "/data/forecast.json"),
  associationMatrix: () => get("/api/association-matrix", "/data/association-matrix.json"),
  validation: () => get("/api/validation", "/data/validation.json"),
}
