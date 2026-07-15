export default function Loading({ label = "Loading" }) {
  return (
    <div className="flex items-center gap-2 text-[var(--color-paper-dim)] text-sm py-10 justify-center">
      <span className="w-2 h-2 rounded-full bg-[var(--color-gold)] animate-pulse" />
      {label}…
    </div>
  )
}
