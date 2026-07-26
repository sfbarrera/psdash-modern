"""Puertos (interfaces) de la arquitectura hexagonal.

Estos protocolos definen QUE necesita la capa de servicios del sistema
operativo, sin acoplarse a COMO se obtiene. Los adaptadores concretos
(psutil, sistema de archivos) los implementan. Gracias a esto, las pruebas
pueden inyectar dobles y la logica de negocio queda independiente del SO
y de las librerias externas.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


class MetricsProvider(Protocol):
    """Puerto para obtener metricas de red del sistema (RF-04)."""

    def read_net_counters(self) -> dict:
        """Contadores de E/S por interfaz."""
        ...

    def read_if_stats(self) -> dict:
        """Estado (up/down) por interfaz."""
        ...

    def read_addresses(self, name: str) -> tuple[str | None, str | None]:
        """Devuelve (ipv4, mac) de la interfaz indicada."""
        ...


class LogReaderPort(Protocol):
    """Puerto para leer archivos de log (RF-05)."""

    def list_files(self) -> list[Path]:
        ...

    def tail(self, path: Path, n: int) -> list[str]:
        ...

    def search(self, path: Path, pattern: str) -> Iterator[tuple[int, str]]:
        ...
