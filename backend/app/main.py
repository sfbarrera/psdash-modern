"""Punto de entrada de la aplicacion modernizada (ASGI / FastAPI).

Reemplaza el arranque con gevent + monkey-patching de run.py del legado por
un servidor ASGI (Uvicorn) y organiza la aplicacion en routers.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import logs, network

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API REST de monitoreo de sistema (migracion de psdash a Python 3 + FastAPI).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(network.router)
app.include_router(logs.router)


@app.get("/api/health", tags=["health"])
async def health() -> dict:
    """Endpoint de salud para orquestadores y balanceadores."""
    return {"status": "ok", "app": settings.app_name, "version": settings.version}
