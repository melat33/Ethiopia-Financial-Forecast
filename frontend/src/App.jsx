import { useEffect, useState } from "react"
import Sidebar from "./components/Sidebar"
import LedgerStrip from "./components/LedgerStrip"
import Overview from "./pages/Overview"
import Trends from "./pages/Trends"
import Forecasts from "./pages/Forecasts"
import Projections from "./pages/Projections"
import { api } from "./lib/api"

const PAGES = { overview: Overview, trends: Trends, forecasts: Forecasts, projections: Projections }
const TITLES = {
  overview: "Financial inclusion overview",
  trends: "Trends",
  forecasts: "Forecasts",
  projections: "Inclusion projections",
}

export default function App() {
  const [page, setPage] = useState("overview")
  const [overview, setOverview] = useState(null)

  useEffect(() => { api.overview().then(setOverview).catch(() => {}) }, [])

  const Page = PAGES[page]

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <Sidebar page={page} setPage={setPage} />

      <div className="flex-1 min-w-0">
        <LedgerStrip overview={overview} />

        {/* mobile nav */}
        <div className="md:hidden flex gap-1 px-4 py-3 border-b border-[var(--color-hairline)] overflow-x-auto">
          {Object.keys(PAGES).map((id) => (
            <button key={id} onClick={() => setPage(id)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap
                ${page === id ? "bg-[var(--color-panel-raised)] text-[var(--color-gold)]" : "text-[var(--color-paper-dim)]"}`}>
              {id}
            </button>
          ))}
        </div>

        <main className="px-6 py-8 max-w-6xl">
          <div className="mb-6">
            <p className="text-[10px] uppercase tracking-wider text-[var(--color-paper-dim)] mb-1">Selam Analytics — Consortium Dashboard</p>
            <h1 className="font-display text-3xl text-[var(--color-paper)]">{TITLES[page]}</h1>
          </div>
          <Page overview={overview} />
        </main>
      </div>
    </div>
  )
}
