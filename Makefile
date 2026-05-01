install:
	uv sync

run:
	uv run python -m src

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
	find src -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf build dist
	rm -f pacman.spec.bak

.PHONY: install run debug clean lint lint-strict test package
