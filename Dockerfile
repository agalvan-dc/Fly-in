# 1. Lightweight base image with Python 3.12 pre-installed
FROM python:3.12-slim

# 2. Install C build tools and system dependencies for Pygame and NumPy[cite: 4]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsdl2-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Poetry globally inside the container[cite: 4]
RUN pip install poetry

# 4. Set working directory inside container[cite: 4]
WORKDIR /app

# 5. Copy dependency configuration files[cite: 4]
COPY pyproject.toml poetry.lock* /app/

# 6. Install Python dependencies without creating an internal virtual environment[cite: 4]
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# 7. Copy remaining project source code[cite: 4]
COPY . /app

# 8. Default execution command[cite: 4]
CMD ["poetry", "run", "python", "fly-in.py", "data/"]
