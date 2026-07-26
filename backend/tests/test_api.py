"""Pruebas de integracion de la API sobre los endpoints reales.

Usan el TestClient de FastAPI, que ejercita la aplicacion completa
(routers, inyeccion de dependencias, validacion Pydantic y manejo de errores)
sin levantar un servidor. Complementan las pruebas unitarias de servicios.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("PSDASH_LOG_DIRS", tempfile.gettempdir())

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_interfaces_devuelve_lista():
    r = client.get("/api/network/interfaces")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Al menos la interfaz loopback debe existir en cualquier entorno.
    assert any(i["name"] == "lo" for i in data)
    # El contrato Pydantic garantiza estas claves.
    if data:
        assert {"name", "is_up", "bytes_sent", "tx_per_sec"} <= data[0].keys()


def test_interfaz_inexistente_da_404():
    r = client.get("/api/network/interfaces/no-existe-xyz")
    assert r.status_code == 404


def test_logs_endpoint_responde():
    r = client.get("/api/logs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_sin_query_da_422():
    """Validacion automatica de Pydantic: falta el parametro obligatorio q."""
    r = client.get("/api/logs/cualquiera/search")
    assert r.status_code == 422


def test_search_en_log_real(tmp_path):
    # Crea un log temporal en un directorio aislado y apunta el adaptador ahi.
    logdir = tmp_path / "aislado"
    logdir.mkdir()
    (logdir / "demo.log").write_text(
        "INFO ok\nERROR fallo\nINFO fin\n", encoding="utf-8"
    )
    from app.adapters.file_log_adapter import FileLogAdapter
    from app.core import deps
    from app.services.log_service import LogService

    app.dependency_overrides[deps.get_log_service] = lambda: LogService(
        FileLogAdapter([Path(logdir)])
    )
    try:
        logs = client.get("/api/logs").json()
        assert len(logs) == 1
        log_id = logs[0]["id"]
        matches = client.get(f"/api/logs/{log_id}/search?q=ERROR").json()
        assert len(matches) == 1
        assert matches[0]["line_no"] == 2
    finally:
        app.dependency_overrides.clear()
