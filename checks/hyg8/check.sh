#!/usr/bin/env bash
# PRG-8: гигиена тестов — не пишут в репозиторий, независимы друг от друга, быстрые.
set -u
snapshot() { find . -path ./.venv -prune -o -path ./.git -prune -o -name __pycache__ -prune -o \
  -name .pytest_cache -prune -o -name .coverage -prune -o -name .ruff_cache -prune -o -name .mypy_cache -prune -o \
  -type f -print | sort; }
snapshot >"$TMP/before"
start=$(date +%s)
quiet "все тесты вместе" $PY -m pytest -q -p no:cacheprovider tests
took=$(( $(date +%s) - start ))
snapshot >"$TMP/after"
if ! diff -q "$TMP/before" "$TMP/after" >/dev/null; then
  say "  ✗ тесты оставили файлы в репозитории — пишите во временную папку (фикстура tmp_path):"
  diff "$TMP/before" "$TMP/after" | sed -n 's/^> /    /p' | head -10 >&3
  exit 1
fi
ok "тесты не оставляют файлов в репозитории"
[ "$took" -le 30 ] || fail "тесты идут $took с — больше 30 с; что в них ждёт?"
ok "тесты идут $took с"
for f in tests/test_*.py; do
  quiet "$f проходит сам по себе" $PY -m pytest -q -p no:cacheprovider "$f"
done
