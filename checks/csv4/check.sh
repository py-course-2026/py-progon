#!/usr/bin/env bash
# PRG-4: progon gradebook --csv — ведомость для Excel.
set -u
pytest_run "ведомость для Excel" checks/csv4
