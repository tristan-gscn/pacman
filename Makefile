install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	find src -type d -name "__pycache__" -exec rm -r {} +
	find src -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .venv
	rm -rf .pytest_cache

lint:
	uv run python -m flake8 src
	uv run python -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run python -m flake8 src
	uv run python -m mypy src --strict

test:
	uv run python -m pytest src/testing/ -v

.PHONY: install run debug clean lint lint-strict test
