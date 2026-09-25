#!/usr/bin/env bash
# PRG-6: CHANGELOG.md и docs/USER_GUIDE.md к выпуску 0.1.0.
set -u
pytest_run "журнал изменений и руководство" checks/rel6
