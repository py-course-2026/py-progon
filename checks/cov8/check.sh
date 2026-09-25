#!/usr/bin/env bash
# PRG-8: покрытие пакета вашими тестами — не меньше 85 % строк и ветвлений.
set -u
$PY -c "import pytest_cov" >/dev/null 2>&1 || fail "pytest-cov не установлен в проекте — uv add --dev pytest-cov (и закоммитьте pyproject.toml и uv.lock)"
[ -f tests/conftest.py ] || fail "нет tests/conftest.py — общие фикстуры тестов"
grep -q "pytest.fixture" tests/conftest.py || fail "в tests/conftest.py нет ни одной фикстуры (@pytest.fixture)"
quiet "покрытие progon тестами из tests/ — не меньше 85 %" $PY -m pytest -q -p no:cacheprovider tests \
  --cov=progon --cov-branch --cov-report=term-missing --cov-fail-under=85
