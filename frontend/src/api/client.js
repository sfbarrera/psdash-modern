// Cliente HTTP minimo para la API del backend.
// Centraliza el manejo de errores para que los componentes solo se ocupen
// de presentar datos.

async function request(path) {
  const res = await fetch(path, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch (_) {
      /* respuesta sin cuerpo JSON */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  interfaces: () => request("/api/network/interfaces"),
  logs: () => request("/api/logs"),
  tail: (id, n = 100) => request(`/api/logs/${id}/tail?n=${n}`),
  search: (id, q) => request(`/api/logs/${id}/search?q=${encodeURIComponent(q)}`),
};
