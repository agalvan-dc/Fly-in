IMAGE_NAME = fly-in-image
CONTAINER_NAME = fly-in-dev
MAP_DIR = maps/

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd):/app:z" --name $(CONTAINER_NAME) $(IMAGE_NAME) poetry run python fly-in.py $(MAP_DIR)

shell:
	docker run --rm -it -v "$$(pwd):/app:z" --name $(CONTAINER_NAME) $(IMAGE_NAME) /bin/bash

debug:
	docker run --rm -it -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd):/app:z" $(IMAGE_NAME) poetry run python -m pdb fly-in.py $(MAP_DIR)

lint:
	docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd):/app:z" $(IMAGE_NAME) bash -c "flake8 . && python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs -S"

clean:
	@echo "Limpiando archivos locales y configuraciones JSON..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.json" -delete 2>/dev/null || true
	@rm -rf .mypy_cache poetry.lock 2>/dev/null || true
	@echo "Limpiando Docker..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@docker rmi -f $(IMAGE_NAME) 2>/dev/null || true
	@docker image prune -f

.PHONY: build run shell debug lint clean
