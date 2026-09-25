#!/usr/bin/env bash
# PRG-10: таймаут убивает всю группу процессов решения.
set -u
pytest_run "таймаут убивает всё" checks/kill10
