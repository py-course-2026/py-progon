"""PRG-5: класс Course — композиция заданий, студентов и попыток."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from progon.errors import UnknownTaskError
from progon.model import Attempt, Course, Student, Task

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "checks" / "cmd3" / "course.json"
D = datetime(2026, 10, 1, 23, 59)


def small():
    return Course([Task("w1", D), Task("w2", D, max_score=20)],
                  [Student("anna", "Петрова Анна", "ИИ-201"), Student("ivan", "Иванов Иван", "ИИ-202")])


def test_from_json_gradebook():
    c = Course.from_json(COURSE)
    assert c.gradebook() == [
        ["Петрова Анна", "ИИ-201", 10, 4.5, 0, 14.5],
        ["Иванов Иван", "ИИ-201", 5, 8, 10, 23],
        ["Орлова Ольга", "ИИ-202", 0, 0, 6, 6],
    ]
    assert len(c) == 7
    assert list(c.tasks) == ["week01", "week02", "week03"]
    assert c.best("anna", "week02") == 4.5 and c.best("olga", "week01") == 0


def test_add_attempt_and_best():
    c = small()
    c.add_attempt(Attempt("anna", "w2", 18, D))
    c.add_attempt(Attempt("anna", "w2", 20, D.replace(day=2)))
    assert c.best("anna", "w2") == 18
    c.extend("anna", "w2", D.replace(day=5))
    assert c.best("anna", "w2") == 20


def test_add_attempt_validation():
    c = small()
    with pytest.raises(UnknownTaskError):
        c.add_attempt(Attempt("anna", "w9", 5, D))
    with pytest.raises(ValueError, match="w1"):
        c.add_attempt(Attempt("anna", "w1", 11, D))
    with pytest.raises(ValueError):
        c.add_attempt(Attempt("ghost", "w1", 5, D))
    with pytest.raises(UnknownTaskError):
        c.extend("anna", "w9", D)
    assert len(c) == 0


def test_read_only_views():
    c = small()
    with pytest.raises(TypeError):
        c.tasks["w3"] = Task("w3", D)
    assert isinstance(c.students, tuple)
    assert c.tasks["w2"].max_score == 20


def test_task_objects_in_json(tmp_path):
    data = json.loads(COURSE.read_text(encoding="utf-8"))
    data["tasks"]["week03"] = {"deadline": "2026-09-21T23:59", "max_score": 20, "timeout": 60,
                               "open_tests": ["tests.test_a::test_ok"]}
    data["attempts"].append({"login": "olga", "task": "week03", "score": 17, "submitted": "2026-09-20T10:00"})
    p = tmp_path / "course.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    c = Course.from_json(p)
    assert c.tasks["week03"].max_score == 20 and c.tasks["week03"].timeout == 60
    assert c.tasks["week03"].open_tests == frozenset({"tests.test_a::test_ok"})
    assert c.best("olga", "week03") == 17


@pytest.mark.parametrize(("change", "part"), [
    (lambda d: d["attempts"].append({"login": "anna", "task": "week01", "score": 12,
                                     "submitted": "2026-09-01T10:00"}), "12"),
    (lambda d: d["attempts"].append({"login": "ghost", "task": "week01", "score": 5,
                                     "submitted": "2026-09-01T10:00"}), "ghost"),
    (lambda d: d["tasks"].update(week04={"deadline": "2026-09-28T23:59", "timeout": 3600}), "week04"),
])
def test_bad_data_is_a_user_error(tmp_path, change, part):
    data = json.loads(COURSE.read_text(encoding="utf-8"))
    change(data)
    p = tmp_path / "course.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "progon", "gradebook", str(p)], capture_output=True,
                       text=True, encoding="utf-8", cwd=ROOT)
    assert r.returncode == 1 and "Traceback" not in r.stderr, r.stderr[-600:]
    assert r.stderr.startswith("progon: ошибка: ") and part in r.stderr, r.stderr
