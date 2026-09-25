#!/usr/bin/env bash
# PRG-3: progon gradebook — ведомость из файла курса, журнал; свои тесты и ruff.
set -u
pytest_run "команда gradebook" checks/cmd3
grep -qs gradebook tests/test_cli.py || fail "в tests/test_cli.py нет теста команды gradebook"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
