"""Pruebas unitarias de la logica de negocio.

Se apoyan en la arquitectura de puertos y adaptadores: en lugar de leer del
sistema operativo real, inyectan dobles que devuelven datos controlados. Esto
demuestra la ventaja de mantenibilidad del diseno: la logica se prueba de
forma aislada, deterministica y sin depender del entorno.
"""
from __future__ import annotations

from pathlib import Path

from app.schemas.network import InterfaceDTO
from app.services.log_service import LogNotFoundError, LogService
from app.services.network_service import NetworkService


# ---------- Dobles ----------
class _Counter:
    def __init__(self, sent: int, recv: int) -> None:
        self.bytes_sent = sent
        self.bytes_recv = recv


class _Stat:
    def __init__(self, isup: bool) -> None:
        self.isup = isup


class FakeMetricsProvider:
    def read_net_counters(self) -> dict:
        return {"eth0": _Counter(1000, 2000), "lo": _Counter(0, 0)}

    def read_if_stats(self) -> dict:
        return {"eth0": _Stat(True), "lo": _Stat(True)}

    def read_addresses(self, name: str):
        return ("172.18.0.2", "02:42:ac:12:00:02") if name == "eth0" else (None, None)


class FakeLogReader:
    def __init__(self, tmp: Path) -> None:
        self._file = tmp / "app.log"
        self._file.write_text(
            "linea de info\nerror: fallo de conexion\notra linea\nerror: timeout\n",
            encoding="utf-8",
        )

    def list_files(self):
        return [self._file]

    def tail(self, path, n):
        return path.read_text(encoding="utf-8").splitlines(keepends=True)[-n:]

    def search(self, path, pattern):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern in line:
                yield i, line


# ---------- RF-04 ----------
def test_list_interfaces_devuelve_dto_tipado():
    svc = NetworkService(FakeMetricsProvider())
    ifaces = svc.list_interfaces()
    assert all(isinstance(i, InterfaceDTO) for i in ifaces)
    eth0 = next(i for i in ifaces if i.name == "eth0")
    assert eth0.ip == "172.18.0.2"
    assert eth0.is_up is True
    assert eth0.bytes_sent == 1000


def test_interfaz_sin_ipv4_no_lanza_excepcion():
    """El defecto latente del legado (acceso por indice) queda corregido."""
    svc = NetworkService(FakeMetricsProvider())
    lo = svc.get_interface("lo")
    assert lo is not None
    assert lo.ip is None  # no explota, devuelve None


def test_throughput_se_calcula_entre_lecturas():
    svc = NetworkService(FakeMetricsProvider())
    svc.list_interfaces()          # primera lectura, sin previo
    ifaces = svc.list_interfaces() # segunda lectura, con delta
    eth0 = next(i for i in ifaces if i.name == "eth0")
    assert eth0.tx_per_sec >= 0.0


# ---------- RF-05 ----------
def test_search_encuentra_coincidencias(tmp_path):
    svc = LogService(FakeLogReader(tmp_path))
    log_id = svc.list_logs()[0].id
    matches = svc.search(log_id, "error")
    assert len(matches) == 2
    assert matches[0].line_no == 2


def test_tail_devuelve_ultimas_lineas(tmp_path):
    svc = LogService(FakeLogReader(tmp_path))
    log_id = svc.list_logs()[0].id
    last = svc.tail(log_id, 2)
    assert len(last) == 2
    assert "timeout" in last[-1]


def test_log_inexistente_lanza_error(tmp_path):
    import pytest

    svc = LogService(FakeLogReader(tmp_path))
    with pytest.raises(LogNotFoundError):
        svc.search("idinexistente", "x")
