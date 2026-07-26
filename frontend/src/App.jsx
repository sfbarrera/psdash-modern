import { useEffect, useState } from "react";
import { api } from "./api/client.js";
import NetworkPanel from "./components/NetworkPanel.jsx";
import LogsPanel from "./components/LogsPanel.jsx";

export default function App() {
  const [tab, setTab] = useState("network");
  const [online, setOnline] = useState(null);

  useEffect(() => {
    const ping = () =>
      api
        .health()
        .then(() => setOnline(true))
        .catch(() => setOnline(false));
    ping();
    const t = setInterval(ping, 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="app">
      <header className="masthead">
        <div className="brand">
          <h1>
            psdash<span className="dot">_</span>
          </h1>
          <span className="sub">python 3 · fastapi · react</span>
        </div>
        <div className="status">
          <span className={`led ${online ? "" : "off"}`} />
          {online === null ? "conectando" : online ? "API en línea" : "API sin conexión"}
        </div>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${tab === "network" ? "active" : ""}`}
          onClick={() => setTab("network")}
        >
          <span className="rf">RF-04</span>Red
        </button>
        <button
          className={`tab ${tab === "logs" ? "active" : ""}`}
          onClick={() => setTab("logs")}
        >
          <span className="rf">RF-05</span>Logs
        </button>
      </nav>

      {tab === "network" ? <NetworkPanel /> : <LogsPanel />}

      <footer>
        <span>psdash modernizado · monitor de sistema para Linux</span>
        <span>migración Python 2 → Python 3</span>
      </footer>
    </div>
  );
}
