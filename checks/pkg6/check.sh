#!/usr/bin/env bash
# PRG-6: progon check и сборка пакета (uv build); свои тесты и ruff.
set -u
pytest_run "проверка курса и пакет" checks/pkg6
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
