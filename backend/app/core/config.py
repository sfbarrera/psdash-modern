"""Configuracion de la aplicacion.

El secreto y los parametros ya no estan incrustados en el codigo (como el
'whatisthissorcery' hardcodeado del run.py legado): se leen de variables de
entorno, con valores por defecto seguros para desarrollo.
"""
from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        # Directorios donde se buscaran archivos .log (RF-05). Se separan con
        # os.pathsep (':' en Linux, ';' en Windows) para que una ruta con letra
        # de unidad como C:\proy\sample-logs no quede partida en dos.
        raw = os.getenv("PSDASH_LOG_DIRS", os.pathsep.join(["/var/log", "/logs"]))
        self.log_dirs: list[str] = [d.strip() for d in raw.split(os.pathsep) if d.strip()]

        # Origenes permitidos para CORS (la SPA de React).
        cors = os.getenv("PSDASH_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        self.cors_origins: list[str] = [o for o in cors.split(",") if o]

        self.app_name = "psdash modernizado"
        self.version = "1.0.0"


settings = Settings()
