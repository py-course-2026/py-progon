"""PRG-3: команда progon gradebook и журнал."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = Path(__file__).resolve().parent / "course.json"


def progon(*args, cwd=ROOT):
    return subprocess.run([sys.executable, "-m", "progon", *args], capture_output=True,
                          text=True, encoding="utf-8", cwd=cwd)


def test_gradebook_table():
    r = progon("gradebook", str(COURSE))
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.splitlines() == [
        "ФИО\tГруппа\tweek01\tweek02\tweek03\tИтог",
        "Петрова Анна\tИИ-201\t10\t4.5\t0\t14.5",
        "Иванов Иван\tИИ-201\t5\t8\t10\t23",
        "Орлова Ольга\tИИ-202\t0\t0\t6\t6",
    ]
    assert r.stderr == "", "без -v журнал молчит"


def test_task_order_follows_file(tmp_path):
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    course["tasks"] = dict(reversed(list(course["tasks"].items())))
    path = tmp_path / "course.json"
    path.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")
    r = progon("gradebook", str(path))
    assert r.stdout.splitlines()[0] == "ФИО\tГруппа\tweek03\tweek02\tweek01\tИтог"


def test_verbose_writes_log():
    r = progon("-v", "gradebook", str(COURSE))
    assert r.returncode == 0
    assert "INFO" in r.stderr, "с -v сообщения уровня INFO попадают в журнал (stderr)"
    assert r.stdout.startswith("ФИО\t"), "журнал — в stderr, таблица — в stdout"


def test_unknown_task_is_reported():
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    course["attempts"].append({"login": "anna", "task": "week99", "score": 5, "submitted": "2026-09-10T10:00"})
    path = ROOT / ".prg3-unknown.json"
    try:
        path.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")
        r = progon("gradebook", str(path))
    finally:
        path.unlink(missing_ok=True)
    assert r.returncode == 1
    assert "week99" in r.stderr and "Traceback" not in r.stderr


def test_help_lists_command():
    r = progon("--help")
    assert r.returncode == 0 and "gradebook" in r.stdout


def test_library_does_not_configure_logging():
    code = ("import logging, progon.cli, progon.gradebook; "
            "print(len(logging.getLogger().handlers), logging.getLogger().level)")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)
    assert r.stdout.split() == ["0", "30"], "импорт модулей progon не должен настраивать журнал — только main()"
