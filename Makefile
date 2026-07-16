PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python

.PHONY: bootstrap install test smoke check

bootstrap:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e '.[dev,tui]'
	$(VENV_PYTHON) -m pytest -v
	$(VENV_PYTHON) -m codex_runner.runner guardian --help >/dev/null
	$(VENV_PYTHON) -m codex_runner.runner loop --help >/dev/null

install:
	$(PYTHON) -m pip install -e '.[dev,tui]'

test:
	$(PYTHON) -m pytest -v

smoke:
	$(PYTHON) -c "import yaml; import codex_runner.runner; import codex_runner.guardian.plan_pack_validator"
	$(PYTHON) -m codex_runner.runner guardian --help >/dev/null
	$(PYTHON) -m codex_runner.runner loop --help >/dev/null

check: smoke test
