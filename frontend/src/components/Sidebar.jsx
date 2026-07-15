const NAV = [
  { id: "overview", label: "Overview" },
  { id: "trends", label: "Trends" },
  { id: "forecasts", label: "Forecasts" },
  { id: "projections", label: "Projections" },
]

export default function Sidebar({ page, setPage }) {
  return (
    <aside className="hidden md:flex md:flex-col md:w-56 shrink-0 border-r border-[var(--color-hairline)] px-5 py-6">
      <div className="flex items-center gap-2 mb-10">
        <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true">
          <rect width="32" height="32" rx="6" fill="var(--color-panel-raised)" />
          <path d="M8 10h16M8 16h10M8 22h16" stroke="var(--color-gold)" strokeWidth="2" strokeLinecap="round" />
        </svg>
        <div className="leading-tight">
          <p className="font-display text-[15px] text-[var(--color-paper)]">Selam Analytics</p>
          <p className="text-[10px] tracking-wide uppercase text-[var(--color-paper-dim)]">Ethiopia FI Forecast</p>
        </div>
      </div>

      <nav className="flex flex-col gap-1" aria-label="Primary">
        {NAV.map((item) => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            aria-current={page === item.id ? "page" : undefined}
            className={`text-left px-3 py-2 rounded-md text-sm font-medium transition-colors
              ${page === item.id
                ? "bg-[var(--color-panel-raised)] text-[var(--color-gold)]"
                : "text-[var(--color-paper-dim)] hover:text-[var(--color-paper)] hover:bg-[var(--color-panel)]"}`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="mt-auto pt-8 border-t border-[var(--color-hairline)] text-[11px] text-[var(--color-paper-dim)] leading-relaxed">
        <p>Global Findex-aligned tracking of Access &amp; Usage for Ethiopia's digital financial transformation.</p>
      </div>
    </aside>
  )
}
