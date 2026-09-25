#!/usr/bin/env bash
# PRG-13: модель риска — лучше базовой на отложенной выборке; свои тесты и ruff.
set -u
pytest_run "модель риска" checks/ml13
[ -f tests/test_predict.py ] || fail "нет tests/test_predict.py — напишите свои тесты модели"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
