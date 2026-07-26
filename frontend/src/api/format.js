// Formateo de bytes a unidades legibles. Es el equivalente moderno de
// las funciones de helpers.py del legado, ahora del lado del cliente.

export function humanBytes(n) {
  if (n === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(n) / Math.log(1024));
  return `${(n / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function humanRate(bps) {
  if (!bps || bps <= 0) return "0 B/s";
  return `${humanBytes(bps)}/s`;
}
