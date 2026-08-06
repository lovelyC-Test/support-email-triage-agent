# Every routine command in one place, so none of them live only in your shell
# history. Run `make` or `make help` to see what is available.
#
# Two kinds of target, and the distinction matters:
#   fix    changes your files to make them correct
#   lint   only reports, and changes nothing
# `make check` uses the reporting kind, so a pass genuinely means it was clean
# rather than meaning something quietly rewrote it.

.DEFAULT_GOAL := help
PY := .venv/bin

.PHONY: help venv install fix lint typecheck test cov check run version clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-11s\033[0m %s\n", $$1, $$2}'

venv:  ## Create the virtual environment
	python3 -m venv .venv

install: venv  ## Install the package, dev tools and git hooks
	$(PY)/python -m pip install --upgrade pip
	$(PY)/python -m pip install -e ".[dev]"
	$(PY)/pre-commit install

fix:  ## Autofix lint errors and reformat. MODIFIES FILES
	$(PY)/ruff check . --fix
	$(PY)/ruff format .

lint:  ## Report lint and formatting problems, changing nothing
	$(PY)/ruff check .
	$(PY)/ruff format --check .

typecheck:  ## Strict type check
	$(PY)/mypy

test:  ## Run the tests. These must pass with no network connection
	$(PY)/pytest

cov:  ## Run the tests with a coverage report
	$(PY)/pytest --cov

check: lint typecheck test  ## Verify everything, changing nothing. Run before committing

run:  ## Process the sample emails through the graph
	$(PY)/python -m support_desk.main process-folder data/raw/emails

version:  ## Phase 1 acceptance test: the package imports and reports its version
	$(PY)/python -m support_desk.main --version

clean:  ## Remove caches and build artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage dist build
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
