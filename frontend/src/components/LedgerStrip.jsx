// The page's signature element: a persistent ticker of key metrics, styled
// like a financial-terminal strip. The gold bar is not decorative — its
// width literally encodes progress from the base 2025 forecast to the
// NFIS-II 70% Access target.

function Stat({ label, value, unit = "", accent = "gold" }) {
  const color = accent === "gold" ? "var(--color-gold)" : accent === "teal" ? "var(--color-teal)" : "var(--color-coral)"
  return (
    <div className="flex flex-col gap-0.5 px-5 py-3 border-r border-[var(--color-hairline)] last:border-r-0 min-w-[140px]">
      <span className="text-[10px] uppercase tracking-wider text-[var(--color-paper-dim)]">{label}</span>
      <span className="font-mono text-xl tabular-nums" style={{ color }}>
        {value}
        <span className="text-xs ml-0.5 text-[var(--color-paper-dim)]">{unit}</span>
      </span>
    </div>
  )
}

export default function LedgerStrip({ overview }) {
  if (!overview) return (
    <div className="h-[74px] border-b border-[var(--color-hairline)] animate-pulse bg-[var(--color-panel)]" />
  )

  const { access, mobile_money, crossover_ratio, target_2025, base_forecast_2025, gap_pp } = overview
  const progressPct = target_2025 ? Math.min(100, (base_forecast_2025 / target_2025) * 100) : 0

  return (
    <div className="border-b border-[var(--color-hairline)] bg-[var(--color-panel)]">
      <div className="flex flex-wrap">
        <Stat label={`Access, ${access.year}`} value={access.current.toFixed(0)} unit="%" accent="gold" />
        <Stat label="Mobile Money Accounts" value={mobile_money.current.toFixed(1)} unit="%" accent="teal" />
        <Stat label="P2P / ATM Ratio" value={crossover_ratio ? crossover_ratio.toFixed(2) : "—"} unit="x" accent="teal" />
        <Stat label="Gap to NFIS-II Target" value={gap_pp ? gap_pp.toFixed(1) : "—"} unit="pp" accent="coral" />
      </div>
      <div className="h-1 w-full bg-[var(--color-hairline)]">
        <div
          className="h-1 bg-[var(--color-gold)] transition-all duration-700"
          style={{ width: `${progressPct}%` }}
          role="progressbar"
          aria-valuenow={Math.round(progressPct)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Progress toward NFIS-II 70% Access target"
        />
      </div>
    </div>
  )
}
