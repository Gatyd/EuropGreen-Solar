/**
 * Formate une date ISO en affichant l'heure telle qu'envoyée par le serveur (heure "mur"),
 * sans décalage lié au fuseau du navigateur. Exemple d'entrée: 2025-08-19T14:41:14.740480+02:00
 * Rend: "19 août 2025 14:41" (fr-FR), avec option pour afficher l'offset.
 */
export function formatDate(
  iso?: string | Date,
  options?: { showOffset?: boolean }
): string {
  if (!iso) return '—'
  const { showOffset = false } = options || {}

  try {
    if (typeof iso === 'string') {
      // Capture: YYYY MM DD HH mm [ss] [.sss] [Z|±HH:mm]
      const m = iso.match(
        /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.(\d+))?((?:Z|[+-]\d{2}:?\d{2}))?$/
      )

      if (m) {
        const [, y, mo, d, h, mi, , , offset] = m
        // Construire une date UTC avec l'heure "mur" pour empêcher la conversion de fuseau
        const wallUtc = new Date(
          Date.UTC(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi))
        )
        const datePart = wallUtc.toLocaleDateString('fr-FR', {
          year: 'numeric', month: 'long', day: '2-digit', timeZone: 'UTC'
        })
        const timePart = wallUtc.toLocaleTimeString('fr-FR', {
          hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'UTC'
        })

        if (showOffset && offset) {
          const prettyOffset = offset === 'Z' ? 'UTC' : `UTC${offset.replace(/^(?![+-])/, '+')}`
          return `${datePart} ${timePart} (${prettyOffset})`
        }
        return `${datePart} ${timePart}`
      }
    }

    // Fallback lisible si le format ne correspond pas ou si Date fourni
    const d = typeof iso === 'string' ? new Date(iso) : iso
    if (isNaN(d.getTime())) return String(iso)
    return (
      d.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: '2-digit' }) +
      ' ' +
      d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false })
    )
  } catch {
    return String(iso)
  }
}
