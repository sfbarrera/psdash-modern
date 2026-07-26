# psdash modernizado

Modernización de la aplicación **psdash** (panel web de monitoreo de sistemas Linux)
de **Python 2.7 + Flask** a **Python 3.12 + FastAPI + React**, contenerizada con Docker.

Esta entrega implementa dos requisitos del proyecto:

- **RF-04 — Red:** listar interfaces de red con su dirección y throughput en vivo.
- **RF-05 — Logs:** listar archivos de log, ver sus últimas líneas y buscar patrones.

---

## Arquitectura

```
                 navegador
                    │  HTTP
              ┌─────▼─────┐
              │   Nginx   │  sirve la SPA de React + reverse proxy /api
              └─────┬─────┘
                    │  red interna docker
              ┌─────▼─────┐
              │  FastAPI  │  routers → services → adapters (puertos)
              └─────┬─────┘
                    │  psutil / sistema de archivos (solo lectura)
              ┌─────▼─────┐
              │   Linux   │  /proc, /var/log del host
              └───────────┘
```

El backend sigue una **arquitectura de puertos y adaptadores**: los *routers* exponen
REST, los *services* contienen la lógica de negocio y los *adapters* aíslan el acceso
al sistema operativo. Esto desacopla la lógica del framework web y del SO, que era el
principal problema de mantenibilidad del `web.py` legado.

---

## Opción 1: ejecutar con Docker (recomendada)

Requisito: Docker y Docker Compose.

```bash
docker compose up --build
```

Luego abrir **http://localhost:8080**.

- El frontend queda en el puerto 8080.
- El backend no expone puerto al host: solo es accesible por el frontend a través
  de la red interna de Docker (Nginx como único punto de entrada).
- Se monta `/var/log` del host en modo **solo lectura** como fuente de logs (RF-05).

Para detener: `Ctrl+C` y luego `docker compose down`.

---

## Opción 2: ejecutar en local (para desarrollo)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements-dev.txt

# Directorios donde buscar archivos .log (separados por ':')
export PSDASH_LOG_DIRS=/var/log

uvicorn app.main:app --reload --port 8000
```

- API en http://localhost:8000
- Documentación OpenAPI interactiva en http://localhost:8000/docs

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

- SPA en http://localhost:5173 (Vite hace proxy de `/api` al backend en el 8000).

---

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servicio |
| GET | `/api/network/interfaces` | Lista de interfaces con throughput (RF-04) |
| GET | `/api/network/interfaces/{name}` | Detalle de una interfaz |
| GET | `/api/logs` | Lista de archivos de log (RF-05) |
| GET | `/api/logs/{id}/tail?n=100` | Últimas n líneas de un log |
| GET | `/api/logs/{id}/search?q=patron` | Búsqueda de un patrón en un log |

---

## Pruebas y calidad

```bash
cd backend
pytest --cov=app --cov-report=term    # pruebas + cobertura (~95%)
ruff check app tests                  # análisis estático / lint
```

El pipeline de CI (`.github/workflows/ci.yml`) ejecuta en cada push:

- Pruebas con cobertura y lint del backend.
- Build del frontend.
- Escaneo de vulnerabilidades con **Trivy** (severidad CRITICAL/HIGH).
- Análisis de calidad y seguridad con **SonarQube** (config en `sonar-project.properties`).

---

## Estructura del repositorio

```
psdash-modern/
├── backend/              API FastAPI (Python 3.12)
│   ├── app/
│   │   ├── routers/      endpoints REST (network, logs)
│   │   ├── services/     lógica de negocio
│   │   ├── adapters/     acceso al SO (psutil, ficheros) tras puertos
│   │   ├── schemas/      contratos Pydantic (DTO)
│   │   └── core/         configuración e inyección de dependencias
│   ├── tests/            pruebas unitarias y de integración
│   └── Dockerfile
├── frontend/             SPA React + Vite
│   ├── src/
│   │   ├── components/   NetworkPanel (RF-04), LogsPanel (RF-05)
│   │   └── api/          cliente HTTP
│   ├── nginx.conf        reverse proxy
│   └── Dockerfile
├── docker-compose.yml
├── sonar-project.properties
└── .github/workflows/ci.yml
```
