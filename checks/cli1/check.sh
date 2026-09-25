#!/usr/bin/env bash
# PRG-1: каркас пакета progon, команда --version, свои тесты и чистота по ruff.
set -u
pytest_run "каркас и progon --version" checks/cli1
[ -n "$(find tests -name 'test_*.py' 2>/dev/null)" ] || fail "в tests/ нет ни одного файла test_*.py — напишите свои тесты"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
