export default function ErrorState({ message }) {
  return (
    <div
      className="rounded-lg px-5 py-4 text-sm"
      style={{ border: "1px solid rgba(228,87,46,0.4)", background: "rgba(228,87,46,0.1)", color: "var(--color-coral)" }}
    >
      Couldn't load this data. {message}
    </div>
  )
}
