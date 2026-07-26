"""Contratos de datos (DTO) del recurso de red (RF-04).

En el legado, net.py devolvia diccionarios sin tipar que se pasaban
directamente a la plantilla Jinja2. Aqui cada respuesta tiene un contrato
explicito y validado por Pydantic, que ademas genera la documentacion
OpenAPI automaticamente.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class InterfaceDTO(BaseModel):
    """Representa una interfaz de red y su throughput instantaneo."""

    name: str = Field(..., description="Nombre de la interfaz, p. ej. eth0")
    ip: str | None = Field(None, description="Direccion IPv4, si la interfaz tiene una")
    mac: str | None = Field(None, description="Direccion fisica (MAC)")
    is_up: bool = Field(..., description="Indica si la interfaz esta activa")
    bytes_sent: int = Field(..., description="Bytes enviados acumulados")
    bytes_recv: int = Field(..., description="Bytes recibidos acumulados")
    tx_per_sec: float = Field(0.0, description="Throughput de subida en bytes/segundo")
    rx_per_sec: float = Field(0.0, description="Throughput de bajada en bytes/segundo")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "eth0",
                "ip": "172.18.0.2",
                "mac": "02:42:ac:12:00:02",
                "is_up": True,
                "bytes_sent": 145820,
                "bytes_recv": 982340,
                "tx_per_sec": 1024.0,
                "rx_per_sec": 8192.0,
            }
        }
    }
