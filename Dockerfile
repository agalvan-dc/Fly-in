# 1. Imagen base ligera
FROM python:3.12-slim

# 2. Configurar variables de entorno (Evita .pyc y configura poetry)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalar Poetry usando pip (no requiere apt)
RUN pip install --no-cache-dir poetry

# 5. Copiar archivos de configuración de dependencias
COPY pyproject.toml poetry.lock* /app/

# 6. Instalar dependencias del proyecto.
# NOTA: Pygame y Numpy tienen wheels precompilados, no hace falta build-essential ni apt.
RUN poetry install --no-interaction --no-ansi --no-root

# 7. Copiar código fuente
COPY . /app

# 8. Comando de ejecución por defecto
CMD ["poetry", "run", "python", "fly-in.py"]
