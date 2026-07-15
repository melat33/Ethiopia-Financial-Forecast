import { useEffect, useMemo, useState } from "react"
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { api } from "../lib/api"
import Panel from "../components/Panel"
import MetricCard from "../components/MetricCard"
import Loading from "../components/Loading"
import ErrorState from "../components/ErrorState"

const axisStyle = { fontSize: 11, fill: "var(--color-paper-dim)", fontFamily: "var(--font-mono)" }
const TARGET = 70

export default function Projections() {
  const [forecast, setForecast] = useState(null)
  const [historical, setHistorical] = useState(null)
  const [matrix, setMatrix] = useState(null)
  const [scenario, setScenario] = useState("base")
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.forecast(), api.trends("ACC_OWNERSHIP"), api.associationMatrix()])
      .then(([f, h, m]) => { setForecast(f); setHistorical(h.series); setMatrix(m) })
      .catch((e) => setError(e.message))
  }, [])

  const chartData = useMemo(() => {
    if (!forecast || !historical) return []
    const hist = historical.map(d => ({ year: d.year, historical: d.value }))
    const fc = forecast
      .filter(r => r.indicator_code === "ACC_OWNERSHIP" && r.scenario === scenario)
      .map(r => ({ year: r.year, forecast: r.forecast }))
    return [...hist, ...fc]
  }, [forecast, historical, scenario])

  const gap2027 = useMemo(() => {
    if (!forecast) return null
    const row = forecast.find(r => r.indicator_code === "ACC_OWNERSHIP" && r.scenario === scenario && r.year === 2027)
    return row ? +(TARGET - row.forecast).toFixed(1) : null
  }, [forecast, scenario])

  return (
    <div className="flex flex-col gap-6">
      <Panel
        eyebrow="Inclusion Projections"
        title="Progress toward the NFIS-II 70% Access target"
        action={
          <div className="flex gap-1 bg-[var(--color-panel-raised)] rounded-md p-1">
            {["pessimistic", "base", "optimistic"].map(s => (
              <button key={s} onClick={() => setScenario(s)}
                className={`px-3 py-1 rounded text-xs font-mono capitalize transition-colors
                  ${scenario === s ? "bg-[var(--color-gold)] text-[var(--color-ink)]" : "text-[var(--color-paper-dim)]"}`}>
                {s}
              </button>
            ))}
          </div>
        }
      >
        {error ? <ErrorState message={error} /> : !forecast ? <Loading /> : (
          <>
            <ResponsiveContainer width="100%" height={340}>
              <ComposedChart data={chartData}>
                <CartesianGrid stroke="var(--color-hairline)" vertical={false} />
                <XAxis dataKey="year" tick={axisStyle} axisLine={{ stroke: "var(--color-hairline)" }} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={36} domain={[0, 80]} />
                <Tooltip contentStyle={{ background: "var(--color-panel-raised)", border: "1px solid var(--color-hairline)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
                <ReferenceLine y={TARGET} stroke="var(--color-coral)" strokeDasharray="4 4" label={{ value: "NFIS-II Target (70%)", fill: "var(--color-coral)", fontSize: 10, position: "insideTopLeft" }} />
                <Line type="monotone" dataKey="historical" stroke="var(--color-paper)" strokeWidth={2} dot={{ r: 4 }} connectNulls name="Observed" />
                <Line type="monotone" dataKey="forecast" stroke="var(--color-gold)" strokeWidth={2.5} strokeDasharray="5 3" dot={{ r: 4 }} name={`Forecast (${scenario})`} />
              </ComposedChart>
            </ResponsiveContainer>
            <div className="mt-4 max-w-xs">
              <MetricCard label="Projected gap to target, 2027" value={gap2027 > 0 ? gap2027 : "Met"} unit={gap2027 > 0 ? "pp" : ""} accent={gap2027 > 0 ? "coral" : "teal"} />
            </div>
          </>
        )}
      </Panel>

      <Panel eyebrow=" Association Matrix" title="Which events move which indicators">
        {!matrix ? <Loading /> : <AssociationTable matrix={matrix} />}
      </Panel>

      <Panel eyebrow="For the Consortium" title="Answers to the key questions">
        <div className="flex flex-col gap-4 text-sm text-[var(--color-paper)] leading-relaxed">
          <p><strong className="text-[var(--color-gold)]">What drives financial inclusion?</strong> Telebirr and M-Pesa registration growth dominates mobile money expansion, but converts only partially into headline Access growth because most registrants were already banked.</p>
          <p><strong className="text-[var(--color-teal)]">How do events affect outcomes?</strong> See the association matrix above — Telebirr and M-Pesa show the largest empirically-validated effects; Fayda, EthioPay, and interoperability effects remain forward-looking assumptions pending 2025–2027 data.</p>
          <p><strong className="text-[var(--color-coral)]">2025–2027 outlook?</strong> Base-case Access is projected to fall well short of the 70% NFIS-II target without additional intervention.</p>
        </div>
      </Panel>
    </div>
  )
}

function AssociationTable({ matrix }) {
  const max = Math.max(...matrix.values.flat().map(Math.abs), 1)
  return (
    <div className="overflow-x-auto">
      <table className="text-xs font-mono border-collapse">
        <thead>
          <tr>
            <th className="text-left p-2 text-[var(--color-paper-dim)] sticky left-0 bg-[var(--color-panel)]"></th>
            {matrix.indicators.map(ind => (
              <th key={ind} className="p-2 text-[var(--color-paper-dim)] font-normal whitespace-nowrap text-[10px]">{ind}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.events.map((ev, r) => (
            <tr key={ev} className="border-t border-[var(--color-hairline)]">
              <td className="p-2 text-[var(--color-paper)] whitespace-nowrap sticky left-0 bg-[var(--color-panel)] max-w-[180px] truncate">{ev}</td>
              {matrix.values[r].map((v, c) => {
                const intensity = Math.abs(v) / max
                const color = v === 0 ? "transparent" : v > 0 ? `rgba(201,162,39,${0.15 + intensity * 0.55})` : `rgba(228,87,46,${0.15 + intensity * 0.55})`
                return (
                  <td key={c} className="p-2 text-center" style={{ background: color }}>
                    {v !== 0 ? v : "—"}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
