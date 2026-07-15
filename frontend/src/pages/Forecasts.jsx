import { useEffect, useMemo, useState } from "react"
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from "recharts"
import { api } from "../lib/api"
import Panel from "../components/Panel"
import MetricCard from "../components/MetricCard"
import Loading from "../components/Loading"
import ErrorState from "../components/ErrorState"

const axisStyle = { fontSize: 11, fill: "var(--color-paper-dim)", fontFamily: "var(--font-mono)" }
const INDICATORS = [
  { code: "ACC_OWNERSHIP", label: "Access — Account Ownership" },
  { code: "USG_DIGITAL_PAYMENT", label: "Usage — Digital Payment Adoption" },
]

export default function Forecasts() {
  const [forecast, setForecast] = useState(null)
  const [validation, setValidation] = useState(null)
  const [historical, setHistorical] = useState(null)
  const [indicator, setIndicator] = useState("ACC_OWNERSHIP")
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.forecast(), api.validation()])
      .then(([f, v]) => { setForecast(f); setValidation(v) })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    setHistorical(null)
    api.trends(indicator).then(d => setHistorical(d.series)).catch(() => setHistorical([]))
  }, [indicator])

  const chartData = useMemo(() => {
    if (!forecast) return []
    const rows = forecast.filter(r => r.indicator_code === indicator)
    const byYear = {}
    rows.forEach(r => {
      byYear[r.year] = byYear[r.year] || { year: r.year }
      byYear[r.year][r.scenario] = r.forecast
      if (r.scenario === "base") { byYear[r.year].ci_low = r.ci_low; byYear[r.year].ci_high = r.ci_high; byYear[r.year].band = [r.ci_low, r.ci_high] }
    })
    const forecastRows = Object.values(byYear).sort((a, b) => a.year - b.year)
    const histRows = (historical || []).map(d => ({ year: d.year, historical: d.value }))
    return [...histRows, ...forecastRows]
  }, [forecast, historical, indicator])

  const isFallback = forecast?.find(r => r.indicator_code === indicator)?.trend_is_single_point_fallback

  return (
    <div className="flex flex-col gap-6">
      <Panel
        eyebrow="Forecasts, 2025–2027"
        title="Access & Usage forecast with confidence bands"
        action={
          <select value={indicator} onChange={(e) => setIndicator(e.target.value)}
            className="bg-[var(--color-panel-raised)] border border-[var(--color-hairline)] rounded-md text-sm px-3 py-1.5 text-[var(--color-paper)] font-mono">
            {INDICATORS.map(i => <option key={i.code} value={i.code}>{i.label}</option>)}
          </select>
        }
      >
        {isFallback && (
          <p
            className="text-xs mb-3 rounded-md px-3 py-2"
            style={{ color: "var(--color-coral)", background: "rgba(228,87,46,0.1)", border: "1px solid rgba(228,87,46,0.3)" }}
          >
            This indicator has only one historical observation — the baseline is a flat-line fallback, not a fitted trend. Confidence intervals are widened accordingly.
          </p>
        )}
        {error ? <ErrorState message={error} /> : !forecast ? <Loading /> : (
          <ResponsiveContainer width="100%" height={380}>
            <ComposedChart data={chartData}>
              <CartesianGrid stroke="var(--color-hairline)" vertical={false} />
              <XAxis dataKey="year" tick={axisStyle} axisLine={{ stroke: "var(--color-hairline)" }} tickLine={false} />
              <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={36} />
              <Tooltip contentStyle={{ background: "var(--color-panel-raised)", border: "1px solid var(--color-hairline)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "var(--color-paper-dim)" }} />
              <ReferenceLine x={chartData.find(d => d.pessimistic)?.year} stroke="var(--color-hairline)" strokeDasharray="2 2" />
              <Area dataKey="band" stroke="none" fill="var(--color-gold)" fillOpacity={0.1} name="Base 90% band" />
              <Line type="monotone" dataKey="historical" stroke="var(--color-paper)" strokeWidth={2} dot={{ r: 4 }} connectNulls name="Observed" />
              <Line type="monotone" dataKey="pessimistic" stroke="var(--color-coral)" strokeWidth={1.5} strokeDasharray="4 3" dot={false} name="Pessimistic" />
              <Line type="monotone" dataKey="base" stroke="var(--color-gold)" strokeWidth={2.5} dot={{ r: 3 }} name="Base" />
              <Line type="monotone" dataKey="optimistic" stroke="var(--color-teal)" strokeWidth={1.5} strokeDasharray="4 3" dot={false} name="Optimistic" />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </Panel>

      {validation && (
        <Panel eyebrow="Model Validation" title="Telebirr + M-Pesa modeled effect vs. observed data">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <MetricCard label="Observed 2021" value={validation.observed_2021} unit="%" accent="teal" />
            <MetricCard label="Observed 2024" value={validation.observed_2024} unit="%" accent="teal" />
            <MetricCard label="Observed Δ" value={`+${validation.observed_delta_pp}`} unit="pp" accent="teal" />
            <MetricCard label="Modeled 2024" value={validation.modeled_2024_estimate} unit="%" accent="gold" />
            <MetricCard label="Model gap" value={validation.modeled_vs_observed_gap_pp} unit="pp" accent={Math.abs(validation.modeled_vs_observed_gap_pp) < 1 ? "teal" : "coral"} />
          </div>
        </Panel>
      )}
    </div>
  )
}
