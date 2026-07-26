# Imagen del backend: API FastAPI servida por Uvicorn.
# Reemplaza el arranque con gevent del legado por un servidor ASGI moderno.
FROM python:3.12-slim

# Buenas practicas: no generar .pyc y salida sin buffer para ver logs en vivo.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero para aprovechar la cache de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Ejecutar como usuario sin privilegios (tactica de seguridad: menor privilegio).
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Healthcheck para que el orquestador sepa si el servicio esta vivo.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
