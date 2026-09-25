"""PRG-10: по таймауту умирают все процессы решения, а не только pytest."""

import os
import subprocess
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TESTS = HERE.parent / "run10" / "cases" / "tests"


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    stat = Path(f"/proc/{pid}/stat")
    if stat.exists():  # зомби — уже не живой процесс
        return stat.read_text().split(")")[-1].split()[0] != "Z"
    state = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout
    return bool(state.strip()) and not state.strip().startswith("Z")


@pytest.mark.skipif(os.name != "posix", reason="группы процессов — в Linux и macOS")
def test_children_are_killed(tmp_path, monkeypatch):
    from progon.runner import run_tests

    pidfile = tmp_path / "child.pid"
    monkeypatch.setenv("PROGON_PIDFILE", str(pidfile))
    r = run_tests(HERE / "spawn", TESTS, timeout=3)
    assert r.status == "timeout"
    assert pidfile.exists(), "решение не успело запустить дочерний процесс"
    pid = int(pidfile.read_text())
    for _ in range(20):
        if not alive(pid):
            break
        time.sleep(0.1)
    else:
        os.kill(pid, 9)
        pytest.fail("после таймаута процесс, запущенный решением, остался жив — убивайте всю группу процессов")
