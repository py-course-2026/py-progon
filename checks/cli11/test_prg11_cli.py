"""PRG-11: progon run --db и progon history."""

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "checks" / "run10" / "cases"


def progon(*args):
    return subprocess.run([sys.executable, "-m", "progon", *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=ROOT, timeout=120)


def test_run_saves_and_history_shows(tmp_path):
    sols = tmp_path / "solutions"
    shutil.copytree(CASES / "solutions" / "good", sols / "anna")
    shutil.copytree(CASES / "solutions" / "bad", sols / "ivan")
    db = tmp_path / "progon.db"
    for _ in range(2):
        r = progon("run", str(sols), str(CASES / "tests"), "--db", str(db), "--task", "week10",
                   "--max-score", "9")
        assert r.returncode == 0, r.stderr[-800:]
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 4
    conn.close()
    r = progon("history", "ivan", "--db", str(db))
    assert r.returncode == 0, r.stderr[-800:]
    lines = [line.split("\t") for line in r.stdout.splitlines()]
    assert lines[0] == ["Задание", "Время", "Статус", "Прошло", "Всего", "Балл"]
    assert len(lines) == 3
    assert [(x[0], x[2], x[3], x[4], x[5]) for x in lines[1:]] == [("week10", "ok", "1", "3", "3")] * 2


def test_db_needs_task(tmp_path):
    r = progon("run", str(CASES / "solutions"), str(CASES / "tests"), "--db", str(tmp_path / "p.db"),
               "--timeout", "2")
    assert r.returncode == 1 and r.stderr.startswith("progon: ошибка: ") and "--task" in r.stderr
