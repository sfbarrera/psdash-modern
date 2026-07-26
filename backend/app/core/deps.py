"""Proveedores de dependencias para FastAPI.

Reemplazan el objeto global current_service del legado (una variable de
contexto de Flask) por dependencias explicitas inyectadas con Depends.
El NetworkService se mantiene como singleton para conservar la lectura
anterior de contadores y poder calcular el throughput entre peticiones.
"""
from __future__ import annotations

from functools import lru_cache

from app.adapters.file_log_adapter import FileLogAdapter
from app.adapters.psutil_adapter import PsutilAdapter
from app.services.log_service import LogService
from app.services.network_service import NetworkService


@lru_cache(maxsize=1)
def get_network_service() -> NetworkService:
    return NetworkService(PsutilAdapter())


def get_log_service() -> LogService:
    return LogService(FileLogAdapter())
