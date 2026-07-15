export default function MetricCard({ label, value, unit, sublabel, accent = "gold" }) {
  const color = accent === "gold" ? "var(--color-gold)" : accent === "teal" ? "var(--color-teal)" : "var(--color-coral)"
  return (
    <div className="bg-[var(--color-panel)] border border-[var(--color-hairline)] rounded-lg px-5 py-4">
      <p className="text-[11px] uppercase tracking-wider text-[var(--color-paper-dim)] mb-2">{label}</p>
      <p className="font-mono text-3xl tabular-nums" style={{ color }}>
        {value}<span className="text-sm ml-1 text-[var(--color-paper-dim)]">{unit}</span>
      </p>
      {sublabel && <p className="text-xs text-[var(--color-paper-dim)] mt-1">{sublabel}</p>}
    </div>
  )
}
