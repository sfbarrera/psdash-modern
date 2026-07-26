import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { humanBytes, humanRate } from "../api/format.js";

// Escala logaritmica suave para el medidor: satura visualmente cerca de 10 MB/s.
function gaugePct(bps) {
  if (!bps || bps <= 0) return 0;
  const pct = (Math.log10(bps) / Math.log10(10_000_000)) * 100;
  return Math.max(2, Math.min(100, pct));
}

export default function NetworkPanel() {
  const [ifaces, setIfaces] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    const load = () =>
      api
        .interfaces()
        .then((d) => alive && (setIfaces(d), setError(null)))
        .catch((e) => alive && setError(e.message));
    load();
    // Refresco periodico: es lo que hace visible el throughput (RF-04).
    const t = setInterval(load, 2000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  if (error) return <div className="msg err">No se pudieron leer las interfaces: {error}</div>;
  if (!ifaces) return <div className="msg">Leyendo interfaces de red…</div>;

  return (
    <div className="panel">
      <div className="panel-head">
        <span>INTERFACES DE RED · throughput en vivo</span>
        <span className="count">{ifaces.length} activas</span>
      </div>
      {ifaces.map((i) => (
        <div className="iface" key={i.name}>
          <div className="iface-top">
            <span className="iface-name">{i.name}</span>
            <span className={`badge ${i.is_up ? "up" : "down"}`}>{i.is_up ? "up" : "down"}</span>
            <span className="iface-meta">
              {i.ip || "sin IPv4"} {i.mac ? `· ${i.mac}` : ""}
            </span>
          </div>
          <div className="gauges">
            <div>
              <div className="gauge-label">
                <span>TX subida</span>
                <span className="val">{humanRate(i.tx_per_sec)}</span>
              </div>
              <div className="gauge-track">
                <div className="gauge-fill" style={{ width: `${gaugePct(i.tx_per_sec)}%` }} />
              </div>
            </div>
            <div>
              <div className="gauge-label">
                <span>RX bajada</span>
                <span className="val">{humanRate(i.rx_per_sec)}</span>
              </div>
              <div className="gauge-track">
                <div className="gauge-fill rx" style={{ width: `${gaugePct(i.rx_per_sec)}%` }} />
              </div>
            </div>
          </div>
          <div className="totals">
            <span>total enviado: {humanBytes(i.bytes_sent)}</span>
            <span>total recibido: {humanBytes(i.bytes_recv)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
