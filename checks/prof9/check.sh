#!/usr/bin/env bash
# PRG-9: docs/PERFORMANCE.md — замеры, профили до и после, выводы.
set -u
pytest_run "отчёт о производительности" checks/prof9
