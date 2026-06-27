ci:
	ruff format
	ruff check --fix

migration:
	PYTHONPATH=$(PYTHONPATH) uv run alembic revision --autogenerate 

upgrade:
	PYTHONPATH=$(PYTHONPATH) uv run  alembic upgrade head


run_home:
	python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

up_home_d:
	docker-compose up --build -d

up_home:
	docker-compose up --build

down:
	docker-compose down -v

venv:
	uv python install 3.13
	uv sync --python 3.13
	@echo "✅ Environment is ready."

