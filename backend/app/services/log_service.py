"""Logica de negocio del recurso de logs (RF-05)."""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from app.adapters.ports import LogReaderPort
from app.schemas.logs import LogDTO, MatchDTO


class LogNotFoundError(Exception):
    """Se lanza cuando el log solicitado no existe o no esta permitido."""


class LogService:
    def __init__(self, reader: LogReaderPort) -> None:
        self._reader = reader

    def list_logs(self) -> list[LogDTO]:
        logs: list[LogDTO] = []
        for path in self._reader.list_files():
            stat = path.stat()
            logs.append(
                LogDTO(
                    id=self._make_id(path),
                    path=str(path),
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                )
            )
        return logs

    def tail(self, log_id: str, n: int = 100) -> list[str]:
        path = self._resolve(log_id)
        return [line.rstrip("\n") for line in self._reader.tail(path, n)]

    def search(self, log_id: str, pattern: str) -> list[MatchDTO]:
        path = self._resolve(log_id)
        return [
            MatchDTO(line_no=no, content=content)
            for no, content in self._reader.search(path, pattern)
        ]

    # -- helpers --
    def _resolve(self, log_id: str) -> Path:
        for path in self._reader.list_files():
            if self._make_id(path) == log_id:
                return path
        raise LogNotFoundError(log_id)

    @staticmethod
    def _make_id(path: Path) -> str:
        return hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]
