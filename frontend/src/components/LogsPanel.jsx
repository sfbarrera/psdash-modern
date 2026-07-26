import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { humanBytes } from "../api/format.js";

export default function LogsPanel() {
  const [logs, setLogs] = useState(null);
  const [active, setActive] = useState(null);
  const [lines, setLines] = useState([]);
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("tail"); // "tail" | "search"
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .logs()
      .then((d) => {
        setLogs(d);
        if (d.length) selectLog(d[0]);
      })
      .catch((e) => setError(e.message));
  }, []);

  function selectLog(log) {
    setActive(log);
    setMode("tail");
    setQuery("");
    api
      .tail(log.id, 200)
      .then((ls) => setLines(ls.map((txt, idx) => ({ ln: idx + 1, txt }))))
      .catch((e) => setError(e.message));
  }

  function runSearch() {
    if (!active || !query) return;
    api
      .search(active.id, query)
      .then((matches) => {
        setMode("search");
        setLines(matches.map((m) => ({ ln: m.line_no, txt: m.content })));
      })
      .catch((e) => setError(e.message));
  }

  function clearSearch() {
    if (active) selectLog(active);
  }

  function highlight(text) {
    if (mode !== "search" || !query) return text;
    const parts = text.split(query);
    return parts.map((p, i) =>
      i < parts.length - 1 ? (
        <span key={i}>
          {p}
          <mark>{query}</mark>
        </span>
      ) : (
        <span key={i}>{p}</span>
      )
    );
  }

  if (error) return <div className="msg err">Error al leer logs: {error}</div>;
  if (!logs) return <div className="msg">Buscando archivos de log…</div>;
  if (!logs.length)
    return (
      <div className="panel">
        <div className="msg">
          No hay archivos .log en los directorios monitoreados. Monta un directorio
          con logs para verlos aquí.
        </div>
      </div>
    );

  return (
    <div className="log-layout">
      <div className="panel log-list">
        <div className="panel-head">
          <span>ARCHIVOS</span>
          <span className="count">{logs.length}</span>
        </div>
        {logs.map((log) => {
          const name = log.path.split("/").pop();
          return (
            <div
              key={log.id}
              className={`log-item ${active && active.id === log.id ? "active" : ""}`}
              onClick={() => selectLog(log)}
            >
              <div className="name">{name}</div>
              <div className="size">{humanBytes(log.size)}</div>
            </div>
          );
        })}
      </div>

      <div className="panel log-view">
        <div className="search-bar">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runSearch()}
            placeholder={`Buscar patrón en ${active ? active.path.split("/").pop() : "…"}`}
          />
          <button onClick={runSearch}>Buscar</button>
          {mode === "search" && (
            <button className="ghost" onClick={clearSearch}>
              Ver todo
            </button>
          )}
        </div>
        <div className="panel-head">
          <span>{mode === "search" ? `COINCIDENCIAS DE "${query}"` : "ÚLTIMAS LÍNEAS"}</span>
          <span className="count">{lines.length}</span>
        </div>
        <div className="log-lines">
          {lines.length === 0 ? (
            <div className="msg">Sin resultados.</div>
          ) : (
            lines.map((l, i) => (
              <div className="log-line" key={i}>
                <span className="ln">{l.ln}</span>
                <span className="txt">{highlight(l.txt)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
