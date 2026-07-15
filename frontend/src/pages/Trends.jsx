import { useEffect, useMemo, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { api } from "../lib/api"
import Panel from "../components/Panel"
import Loading from "../components/Loading"
import ErrorState from "../components/ErrorState"

const axisStyle = { fontSize: 11, fill: "var(--color-paper-dim)", fontFamily: "var(--font-mono)" }

export default function Trends() {
  const [indicators, setIndicators] = useState([])
  const [selected, setSelected] = useState("ACC_OWNERSHIP")
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [range, setRange] = useState([2011, 2027])

  useEffect(() => { api.indicators().then(setIndicators).catch((e) => setError(e.message)) }, [])
  useEffect(() => {
    setData(null)
    api.trends(selected).then(setData).catch((e) => setError(e.message))
  }, [selected])

  const filtered = useMemo(() => {
    if (!data) return []
    return data.series.filter(d => d.year >= range[0] && d.year <= range[1])
  }, [data, range])

  const eventsInRange = useMemo(() => {
    if (!data) return []
    return data.events.filter(e => {
      const y = new Date(e.date).getFullYear()
      return y >= range[0] && y <= range[1]
    })
  }, [data, range])

  function downloadCsv() {
    if (!data) return
    const rows = ["date,value,confidence,source", ...data.series.map(d => `${d.date},${d.value},${d.confidence},"${d.source}"`)]
    const blob = new Blob([rows.join("\n")], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url; a.download = `${selected}_series.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col gap-6">
      <Panel
        eyebrow="Interactive Trends"
        title="Indicator explorer with event timeline overlay"
        action={
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="bg-[var(--color-panel-raised)] border border-[var(--color-hairline)] rounded-md text-sm px-3 py-1.5 text-[var(--color-paper)] font-mono"
          >
            {indicators.map(code => <option key={code} value={code}>{code}</option>)}
          </select>
        }
      >
        <div className="flex items-center gap-3 mb-4">
          <span className="text-[11px] text-[var(--color-paper-dim)] font-mono">{range[0]}</span>
          <input
            type="range" min={2011} max={2027} value={range[0]}
            onChange={(e) => setRange([Math.min(+e.target.value, range[1]), range[1]])}
            className="accent-[var(--color-gold)] flex-1"
          />
          <input
            type="range" min={2011} max={2027} value={range[1]}
            onChange={(e) => setRange([range[0], Math.max(+e.target.value, range[0])])}
            className="accent-[var(--color-gold)] flex-1"
          />
          <span className="text-[11px] text-[var(--color-paper-dim)] font-mono">{range[1]}</span>
        </div>

        {error ? <ErrorState message={error} /> : !data ? <Loading /> : (
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={filtered.map(d => ({ year: d.year, value: d.value }))}>
              <CartesianGrid stroke="var(--color-hairline)" vertical={false} />
              <XAxis dataKey="year" tick={axisStyle} axisLine={{ stroke: "var(--color-hairline)" }} tickLine={false} />
              <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={36} />
              <Tooltip contentStyle={{ background: "var(--color-panel-raised)", border: "1px solid var(--color-hairline)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
              {eventsInRange.map(e => (
                <ReferenceLine
                  key={e.name + e.date}
                  x={new Date(e.date).getFullYear()}
                  stroke="var(--color-teal)"
                  strokeDasharray="3 3"
                  label={{ value: e.name, angle: -90, position: "insideTopRight", fontSize: 9, fill: "var(--color-paper-dim)" }}
                />
              ))}
              <Line type="monotone" dataKey="value" stroke="var(--color-gold)" strokeWidth={2.5} dot={{ r: 4, fill: "var(--color-gold)" }} />
            </LineChart>
          </ResponsiveContainer>
        )}

        <div className="flex justify-end mt-3">
          <button onClick={downloadCsv} className="text-xs font-mono text-[var(--color-teal)] hover:text-[var(--color-gold)] transition-colors">
            ↓ download series (CSV)
          </button>
        </div>
      </Panel>

      {data && (
        <Panel eyebrow="Underlying data" title="Observations">
          <div className="overflow-x-auto">
            <table className="w-full text-sm font-mono">
              <thead>
                <tr className="text-left text-[var(--color-paper-dim)] text-[10px] uppercase tracking-wider border-b border-[var(--color-hairline)]">
                  <th className="py-2 pr-4">Date</th><th className="py-2 pr-4">Value</th>
                  <th className="py-2 pr-4">Confidence</th><th className="py-2">Source</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((d, i) => (
                  <tr key={i} className="border-b border-[var(--color-hairline)]/50">
                    <td className="py-2 pr-4 text-[var(--color-paper)]">{d.date}</td>
                    <td className="py-2 pr-4 text-[var(--color-gold)]">{d.value}</td>
                    <td className="py-2 pr-4 text-[var(--color-paper-dim)]">{d.confidence}</td>
                    <td className="py-2 text-[var(--color-paper-dim)] font-sans">{d.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  )
}
