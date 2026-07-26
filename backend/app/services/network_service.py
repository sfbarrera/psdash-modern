"""Logica de negocio del recurso de red (RF-04).

Hereda de node.py/net.py del legado la responsabilidad de recolectar las
metricas de red y calcular el throughput, pero desacoplada del framework web
y del sistema operativo: recibe un MetricsProvider por inyeccion de
dependencias y no sabe si detras hay psutil, un mock de prueba u otra fuente.
"""
from __future__ import annotations

import time

from app.adapters.ports import MetricsProvider
from app.schemas.network import InterfaceDTO


class NetworkService:
    def __init__(self, provider: MetricsProvider) -> None:
        self._provider = provider
        self._prev: dict[str, tuple[float, int, int]] = {}

    def list_interfaces(self) -> list[InterfaceDTO]:
        counters = self._provider.read_net_counters()
        stats = self._provider.read_if_stats()
        now = time.monotonic()
        result: list[InterfaceDTO] = []

        for name, c in counters.items():  # items(), no iteritems() (Py2)
            ipv4, mac = self._provider.read_addresses(name)
            tx_ps, rx_ps = self._throughput(name, now, c.bytes_sent, c.bytes_recv)
            is_up = stats[name].isup if name in stats else False
            result.append(
                InterfaceDTO(
                    name=name,
                    ip=ipv4,
                    mac=mac,
                    is_up=is_up,
                    bytes_sent=c.bytes_sent,
                    bytes_recv=c.bytes_recv,
                    tx_per_sec=tx_ps,
                    rx_per_sec=rx_ps,
                )
            )
        return sorted(result, key=lambda i: i.name)

    def get_interface(self, name: str) -> InterfaceDTO | None:
        for iface in self.list_interfaces():
            if iface.name == name:
                return iface
        return None

    def _throughput(
        self, name: str, now: float, sent: int, recv: int
    ) -> tuple[float, float]:
        """Calcula bytes/segundo comparando contra la lectura anterior."""
        tx_ps = rx_ps = 0.0
        if name in self._prev:
            prev_t, prev_sent, prev_recv = self._prev[name]
            dt = now - prev_t
            if dt > 0:
                tx_ps = max(0.0, (sent - prev_sent) / dt)
                rx_ps = max(0.0, (recv - prev_recv) / dt)
        self._prev[name] = (now, sent, recv)
        return round(tx_ps, 2), round(rx_ps, 2)
