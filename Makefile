.PHONY: install install-dev test lint run api evaluate clean

install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check src tests

run:
	python -m lead_qualifier.cli --sample

api:
	uvicorn lead_qualifier.api:app --reload

evaluate:
	python scripts/run_evaluation.py

clean:
	rm -rf .pytest_cache .ruff_cache logs **/__pycache__
