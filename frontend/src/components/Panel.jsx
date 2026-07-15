export default function Panel({ title, eyebrow, action, children, className = "" }) {
  return (
    <section className={`bg-[var(--color-panel)] border border-[var(--color-hairline)] rounded-lg ${className}`}>
      {(title || eyebrow) && (
        <header className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-[var(--color-hairline)]">
          <div>
            {eyebrow && <p className="text-[10px] uppercase tracking-wider text-[var(--color-paper-dim)] mb-0.5">{eyebrow}</p>}
            {title && <h3 className="font-display text-lg text-[var(--color-paper)]">{title}</h3>}
          </div>
          {action}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  )
}
