#!/usr/bin/env bash
# PRG-12: HTTP API «Прогона».
set -u
pytest_run "HTTP API" checks/api12
[ -f tests/test_api.py ] || fail "нет tests/test_api.py — напишите свои тесты API"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
