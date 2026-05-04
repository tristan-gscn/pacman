help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run the application"
	@echo "  make clean       - Clean temporary files"
	@echo "  make debug       - Open the project in debug mode"
	@echo "  make lint        - Run linters and type checkers"
	@echo "  make package     - Create a package that can be exported on other systems"
	@echo "  make lint-strict - Run linters and type checkers in strict mode"

install:
	uv sync

run:
	uv run python pac-man.py config.json

debug:
	uv run python -m pdb -m src

lint:
	uv run python -m flake8 src
	uv run python -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run python -m flake8 src
	uv run python -m mypy src --strict

package:
	rm -rf build dist
	uv run pyinstaller pacman.spec --noconfirm

clean:
	find src -type d -name "__pycache__" -exec rm -r {} +
	find -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf build dist
	rm -f pacman.spec.bak

.PHONY: install run debug clean lint lint-strict test package help
