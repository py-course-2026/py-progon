#!/usr/bin/env bash
# PRG-11: storage.py — история прогонов в SQLite.
set -u
pytest_run "история в базе" checks/db11
[ -f tests/test_storage.py ] || fail "нет tests/test_storage.py — напишите свои тесты хранилища"
pytest_run "ваши тесты в tests/" tests
quiet "ruff check" $PY -m ruff check progon tests
quiet "ruff format --check" $PY -m ruff format --check --diff progon tests
