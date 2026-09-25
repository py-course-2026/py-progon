#!/usr/bin/env bash
# PRG-5: класс Course и команда gradebook поверх него; свои тесты и ruff.
set -u
pytest_run "курс" checks/crs5
[ -f tests/test_model.py ] || fail "нет tests/test_model.py — напишите свои тесты модели"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
