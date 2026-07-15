import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts"
import { api } from "../lib/api"
import Panel from "../components/Panel"
import Loading from "../components/Loading"
import ErrorState from "../components/ErrorState"

const chartGrid = { stroke: "var(--color-hairline)" }
const axisStyle = { fontSize: 11, fill: "var(--color-paper-dim)", fontFamily: "var(--font-mono)" }

export default function Overview({ overview }) {
  const [access, setAccess] = useState(null)
  const [gender, setGender] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.trends("ACC_OWNERSHIP"), api.genderGap()])
      .then(([acc, g]) => { setAccess(acc.series); setGender(g) })
      .catch((e) => setError(e.message))
  }, [])

  if (!overview) return <Loading label="Loading overview" />

  return (
    <div className="flex flex-col gap-6">
      <Panel eyebrow="Five Key Insights" title="What's driving financial inclusion in Ethiopia">
        <ol className="flex flex-col gap-4">
          {overview.insights.map((text, i) => (
            <li key={i} className="flex gap-4">
              <span className="font-mono text-[var(--color-gold)] text-sm pt-0.5 shrink-0">{String(i + 1).padStart(2, "0")}</span>
              <p className="text-sm text-[var(--color-paper)] leading-relaxed">{text}</p>
            </li>
          ))}
        </ol>
      </Panel>

      <div className="grid md:grid-cols-2 gap-6">
        <Panel eyebrow="Access Pillar" title="Account Ownership, 2011–2024">
          {error ? <ErrorState message={error} /> : !access ? <Loading /> : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={access.map(d => ({ year: d.year, value: d.value }))}>
                <CartesianGrid {...chartGrid} vertical={false} />
                <XAxis dataKey="year" tick={axisStyle} axisLine={{ stroke: "var(--color-hairline)" }} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={32} />
                <Tooltip contentStyle={{ background: "var(--color-panel-raised)", border: "1px solid var(--color-hairline)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
                <Line type="monotone" dataKey="value" stroke="var(--color-gold)" strokeWidth={2.5} dot={{ r: 4, fill: "var(--color-gold)" }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Panel>

        <Panel eyebrow="Gender Pillar" title="Account Ownership by Gender">
          {error ? <ErrorState message={error} /> : !gender ? <Loading /> : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={groupGender(gender)}>
                <CartesianGrid {...chartGrid} vertical={false} />
                <XAxis dataKey="year" tick={axisStyle} axisLine={{ stroke: "var(--color-hairline)" }} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={32} />
                <Tooltip contentStyle={{ background: "var(--color-panel-raised)", border: "1px solid var(--color-hairline)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "var(--color-paper-dim)" }} />
                <Bar dataKey="male" fill="var(--color-teal)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="female" fill="var(--color-gold)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Panel>
      </div>
    </div>
  )
}

function groupGender(rows) {
  const byYear = {}
  rows.forEach(r => {
    const year = new Date(r.date).getFullYear()
    byYear[year] = byYear[year] || { year }
    byYear[year][r.gender] = r.value
  })
  return Object.values(byYear).sort((a, b) => a.year - b.year)
}
