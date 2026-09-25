"""PRG-9: progon stats и скорость на данных размера колледжа."""

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COURSE = ROOT / "checks" / "cmd3" / "course.json"
LIMIT = 10  # секунд на всю команду, включая запуск Python и разбор JSON


def progon(*args, timeout=60):
    return subprocess.run([sys.executable, "-m", "progon", *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=ROOT, timeout=timeout)


@pytest.fixture(scope="module")
def big(tmp_path_factory):
    path = tmp_path_factory.mktemp("big") / "big.json"
    subprocess.run([sys.executable, str(HERE / "bigcourse.py"), str(path)], check=True)
    return path


def test_stats_command():
    r = progon("stats", str(COURSE))
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.splitlines() == [
        "Задание\tПопыток\tСтудентов\tСредний балл\tПосле срока",
        "week01\t3\t2\t7.5\t33%",
        "week02\t2\t2\t6.25\t50%",
        "week03\t2\t2\t8\t0%",
    ]


def test_stats_empty_task(tmp_path):
    import json

    data = json.loads(COURSE.read_text(encoding="utf-8"))
    data["tasks"]["week04"] = "2026-09-28T23:59"
    p = tmp_path / "c.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert progon("stats", str(p)).stdout.splitlines()[-1] == "week04\t0\t0\t0\t0%"


@pytest.mark.parametrize("command", ["gradebook", "stats", "check"])
def test_college_size(big, command):
    try:
        r = progon(command, str(big), timeout=LIMIT)
    except subprocess.TimeoutExpired:
        pytest.fail(f"progon {command} на 210 000 попыток не уложился в {LIMIT} с — профилируйте: "
                    f"uv run python -m cProfile -s tottime -m progon {command} big.json")
    assert r.returncode == 0, r.stderr[-800:]
    assert len(r.stdout.splitlines()) >= 3
