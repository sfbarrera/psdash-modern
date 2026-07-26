"""Adaptador que lee archivos de log del sistema de archivos (RF-05).

Corrige los defectos del LogReader legado (Python 2): declara la codificacion
de forma explicita, usa gestores de contexto que garantizan el cierre del
descriptor y realiza la lectura de forma incremental para no cargar en memoria
archivos de log muy grandes.
"""
from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from pathlib import Path

from app.core.config import settings


class FileLogAdapter:
    """Implementacion concreta de LogReaderPort sobre el sistema de archivos."""

    def __init__(self, base_dirs: list[Path] | None = None) -> None:
        self._base_dirs = base_dirs or [Path(d) for d in settings.log_dirs]

    def list_files(self) -> list[Path]:
        files: list[Path] = []
        for base in self._base_dirs:
            if not base.exists():
                continue
            for path in base.glob("*.log"):
                if path.is_file():
                    files.append(path)
        return sorted(files)

    def tail(self, path: Path, n: int) -> list[str]:
        # deque con maxlen mantiene solo las ultimas n lineas en memoria,
        # sin importar el tamano total del archivo.
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return list(deque(fh, maxlen=n))

    def search(self, path: Path, pattern: str) -> Iterator[tuple[int, str]]:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line_no, line in enumerate(fh, start=1):
                if pattern in line:
                    yield line_no, line.rstrip("\n")
