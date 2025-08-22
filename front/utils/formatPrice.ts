/**
 * Formate un nombre en prix avec espaces et virgules appropriées
 * @param price - Le prix à formater (number ou string)
 * @returns Le prix formaté avec espaces comme séparateurs de milliers
 * 
 * Exemples:
 * - 2000.00 -> "2 000"
 * - 1000000 -> "1 000 000"
 * - 3600.99 -> "3 600,99"
 * - 9.9 -> "9,90"
 * - 9 -> "9"
 */
export function formatPrice(price: number | string, zero: boolean = false): string {
  // Convertir en nombre si c'est une chaîne
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  
  // Vérifier si c'est un nombre valide
  if (isNaN(numPrice)) {
    return '0'
  }
  
  // Séparer la partie entière et décimale
  const parts = numPrice.toFixed(2).split('.')
  const integerPart = parts[0]
  const decimalPart = parts[1]
  
  // Formater la partie entière avec des espaces
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  
  // Si les décimales sont .00, ne pas les afficher
  if (decimalPart === '00' && !zero) {
    return formattedInteger
  }
  
  // Remplacer le point par une virgule pour les décimales
  return `${formattedInteger},${decimalPart}`
}
