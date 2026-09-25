#!/usr/bin/env bash
# PRG-4: разбор отчёта JUnit XML и команда progon report; свои тесты и ruff.
set -u
pytest_run "отчёт о прогоне" checks/rep4
[ -f tests/test_report.py ] || fail "нет tests/test_report.py — напишите свои тесты разбора отчёта"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
