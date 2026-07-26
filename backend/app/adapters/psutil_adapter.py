"""Adaptador que obtiene metricas de red usando psutil (RF-04).

Sustituye el uso de netifaces del legado (dependencia abandonada) por
psutil, que esta activamente mantenida. Es el unico punto del backend que
conoce psutil: si en el futuro se cambiara de libreria, solo este archivo
se veria afectado.
"""
from __future__ import annotations

import socket

import psutil


class PsutilAdapter:
    """Implementacion concreta de MetricsProvider basada en psutil."""

    def read_net_counters(self) -> dict:
        return psutil.net_io_counters(pernic=True)

    def read_if_stats(self) -> dict:
        return psutil.net_if_stats()

    def read_addresses(self, name: str) -> tuple[str | None, str | None]:
        ipv4: str | None = None
        mac: str | None = None
        for addr in psutil.net_if_addrs().get(name, []):
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == psutil.AF_LINK:
                mac = addr.address
        # A diferencia del legado, no se accede por indice: si la interfaz
        # no tiene IPv4 simplemente se devuelve None, sin lanzar excepcion.
        return ipv4, mac
