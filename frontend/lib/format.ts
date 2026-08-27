export function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

/** Formats a RISA z-score deviation as "+2.48σ" / "-7.70σ" (sign always shown, unit changed z -> σ). */
export function formatSigma(zScore: number): string {
  const sign = zScore >= 0 ? "+" : "";
  return `${sign}${zScore.toFixed(2)}σ`;
}

/** Formats a 0-1 fraction as a whole percentage, e.g. 0.98 -> "98%". */
export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}
