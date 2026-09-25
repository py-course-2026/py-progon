#!/usr/bin/env bash
# PRG-10: runner.py и progon run; свои тесты и ruff.
set -u
pytest_run "прогон решений" checks/run10
[ -f tests/test_runner.py ] || fail "нет tests/test_runner.py — напишите свои тесты прогона"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
