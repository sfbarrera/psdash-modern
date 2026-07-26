"""Endpoints REST del recurso de red (RF-04).

Sustituyen las vistas @app.route de web.py que renderizaban plantillas.
Ahora exponen JSON con un contrato tipado; el router no contiene logica,
solo declara la ruta y delega en el servicio inyectado.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_network_service
from app.schemas.network import InterfaceDTO
from app.services.network_service import NetworkService

router = APIRouter(prefix="/api/network", tags=["network"])


@router.get("/interfaces", response_model=list[InterfaceDTO])
async def list_interfaces(
    svc: NetworkService = Depends(get_network_service),
) -> list[InterfaceDTO]:
    """Lista todas las interfaces de red con su throughput instantaneo."""
    return svc.list_interfaces()


@router.get("/interfaces/{name}", response_model=InterfaceDTO)
async def get_interface(
    name: str,
    svc: NetworkService = Depends(get_network_service),
) -> InterfaceDTO:
    """Detalle de una interfaz de red por nombre."""
    iface = svc.get_interface(name)
    if iface is None:
        raise HTTPException(status_code=404, detail=f"interfaz '{name}' no encontrada")
    return iface
