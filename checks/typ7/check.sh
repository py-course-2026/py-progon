#!/usr/bin/env bash
# PRG-7: типы — mypy --strict на весь пакет, маркер py.typed.
set -u
$PY -m mypy --version >/dev/null 2>&1 || fail "mypy не установлен в проекте — uv add --dev mypy (и закоммитьте pyproject.toml и uv.lock)"
[ -f progon/py.typed ] || fail "нет progon/py.typed — маркер «пакет с аннотациями типов» (PEP 561)"
quiet "mypy --strict progon" $PY -m mypy --strict --no-incremental progon
