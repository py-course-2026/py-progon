#!/usr/bin/env bash
# PRG-2: progon/gradebook.py — ведомость; свои тесты и ruff.
set -u
pytest_run "ведомость" checks/gb2
[ -f tests/test_gradebook.py ] || fail "нет tests/test_gradebook.py — напишите свои тесты ведомости"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
