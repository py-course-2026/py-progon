#!/usr/bin/env bash
# PRG-7: docs/DESCRIPTION.md по ГОСТ 19.402-78 и docstring у всех публичных модулей, классов, функций.
set -u
pytest_run "описание программы" checks/doc7
quiet "docstring у публичных объектов (ruff D1)" $PY -m ruff check --select D1 --ignore D105,D107 progon
