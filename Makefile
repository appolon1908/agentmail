.PHONY: install test lint typecheck run

install:
	python -m pip install -e '.[dev]'

test:
	pytest -q

lint:
	ruff check .

typecheck:
	mypy src

run:
	uvicorn codestra_agentmail.main:app --reload --port 8097
