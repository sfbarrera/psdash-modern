"""Contratos de datos (DTO) del recurso de logs (RF-05)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LogDTO(BaseModel):
    """Metadatos de un archivo de log disponible para consulta."""

    id: str = Field(..., description="Identificador del log (hash de su ruta)")
    path: str = Field(..., description="Ruta absoluta del archivo de log")
    size: int = Field(..., description="Tamano del archivo en bytes")
    modified_at: datetime = Field(..., description="Fecha de ultima modificacion")


class MatchDTO(BaseModel):
    """Una linea del log que coincide con el patron buscado."""

    line_no: int = Field(..., description="Numero de linea dentro del archivo")
    content: str = Field(..., description="Contenido de la linea coincidente")


class TailDTO(BaseModel):
    """Ultimas lineas de un archivo de log."""

    id: str
    lines: list[str] = Field(default_factory=list)
