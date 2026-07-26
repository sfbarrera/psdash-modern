"""Endpoints REST del recurso de logs (RF-05)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_log_service
from app.schemas.logs import LogDTO, MatchDTO
from app.services.log_service import LogNotFoundError, LogService

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[LogDTO])
async def list_logs(svc: LogService = Depends(get_log_service)) -> list[LogDTO]:
    """Lista los archivos de log disponibles."""
    return svc.list_logs()


@router.get("/{log_id}/tail", response_model=list[str])
async def tail_log(
    log_id: str,
    n: int = Query(100, ge=1, le=5000, description="Numero de lineas finales"),
    svc: LogService = Depends(get_log_service),
) -> list[str]:
    """Devuelve las ultimas n lineas de un log."""
    try:
        return svc.tail(log_id, n)
    except LogNotFoundError:
        raise HTTPException(status_code=404, detail="log no encontrado") from None


@router.get("/{log_id}/search", response_model=list[MatchDTO])
async def search_log(
    log_id: str,
    q: str = Query(..., min_length=1, description="Patron a buscar"),
    svc: LogService = Depends(get_log_service),
) -> list[MatchDTO]:
    """Busca un patron dentro de un log y devuelve las lineas coincidentes."""
    try:
        return svc.search(log_id, q)
    except LogNotFoundError:
        raise HTTPException(status_code=404, detail="log no encontrado") from None
