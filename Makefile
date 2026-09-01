IMAGE_NAME = fly-in-image
CONTAINER_NAME = fly-in-dev
MAP_DIR = mapas/
MAP ?=

# 1. Detect OS to set the correct GUI Docker arguments
OS := $(shell uname -s)

ifeq ($(OS),Linux)
	GUI_ARGS = -e DISPLAY=$$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e XDG_RUNTIME_DIR=/tmp -e LIBGL_ALWAYS_SOFTWARE=1 --security-opt label=disable

else ifeq ($(OS),Darwin)
	# macOS
	GUI_ARGS = -e DISPLAY=host.docker.internal:0
else
	# Windows (Git Bash / MinGW)
	GUI_ARGS = -e DISPLAY=host.docker.internal:0.0
endif

build:
	docker build -t $(IMAGE_NAME) .

run:
	@echo "Detected OS: $(OS)."
	docker run --rm -it \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e PYGAME_HIDE_SUPPORT_PROMPT=1 \
		$(GUI_ARGS) \
		-v "$$(pwd):/app:z" \
		--name $(CONTAINER_NAME) $(IMAGE_NAME) poetry run python fly-in.py $(MAP)

shell:
	docker run --rm -it -v "$$(pwd):/app:z" --name $(CONTAINER_NAME) $(IMAGE_NAME) /bin/bash

debug:
	docker run --rm -it \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e PYGAME_HIDE_SUPPORT_PROMPT=1 \
		$(GUI_ARGS) \
		-v "$$(pwd):/app:z" \
		$(IMAGE_NAME) poetry run python -m pdb fly-in.py $(MAP)

lint:
	docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd):/app:z" $(IMAGE_NAME) bash -c "flake8 . && mypy ."

lint-strict:
	docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd):/app:z" $(IMAGE_NAME) bash -c "flake8 . && mypy . --strict"

clean:
	@echo "Cleaning cache files (resolving Docker root permissions)..."
	@docker run --rm -v "$$(pwd):/app:z" -w /app python:3.12-slim bash -c "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"
	@echo "Cleaning local files and JSON configurations..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.json" -delete 2>/dev/null || true
	@rm -rf .mypy_cache poetry.lock 2>/dev/null || true
	@echo "Cleaning Docker environment..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@docker rmi -f $(IMAGE_NAME) 2>/dev/null || true
	@docker image prune -f

.PHONY: build run shell debug lint lint-strict clean
