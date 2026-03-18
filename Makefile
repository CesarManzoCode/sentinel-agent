PYTHON ?= python3

.PHONY: install run format lint typecheck test docs clean package

install:
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m sentinel chat

format:
	ruff format src tests

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	pytest -q

docs:
	mkdocs build

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist site

package:
	$(PYTHON) -m build
