"""PRG-3: исключения «Прогона» — иерархия и сообщения пользователю вместо трассировки."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GOOD = {
    "tasks": {"w1": "2026-10-01T23:59"},
    "students": [{"login": "anna", "name": "Петрова Анна", "group": "ИИ-201"}],
    "attempts": [{"login": "anna", "task": "w1", "score": 9, "submitted": "2026-10-01T10:00"}],
}


def test_hierarchy():
    from progon import errors

    assert issubclass(errors.ProgonError, Exception)
    assert issubclass(errors.InputError, errors.ProgonError)
    assert issubclass(errors.UnknownTaskError, errors.ProgonError)
    assert issubclass(errors.UnknownTaskError, ValueError), "старый код ловил ValueError — пусть работает"


def test_gradebook_raises_unknown_task_error():
    from progon.errors import UnknownTaskError
    from progon.gradebook import best_scores

    with pytest.raises(UnknownTaskError, match="w9"):
        best_scores([("anna", "w9", 5, datetime(2026, 10, 1))], {"w1": datetime(2026, 10, 1)})


def progon_on(tmp_path, content):
    path = tmp_path / "course.json"
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return subprocess.run([sys.executable, "-m", "progon", "gradebook", str(path)],
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


def assert_user_error(r, *parts):
    assert r.returncode == 1, f"код завершения {r.returncode}, нужен 1\n{r.stderr[-600:]}"
    assert "Traceback" not in r.stderr, "пользователь видит трассировку вместо сообщения:\n" + r.stderr[-600:]
    assert r.stderr.startswith("progon: ошибка: "), f"сообщение начинается с «progon: ошибка: »: {r.stderr!r}"
    for part in parts:
        assert part in r.stderr, f"в сообщении нет {part!r}: {r.stderr!r}"


def test_missing_file():
    r = subprocess.run([sys.executable, "-m", "progon", "gradebook", "nope.json"],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    assert_user_error(r, "nope.json")


def test_broken_json_names_the_line(tmp_path):
    text = json.dumps(GOOD, ensure_ascii=False, indent=2).replace('"score": 9', '"score": 9,,')
    line = next(n for n, s in enumerate(text.splitlines(), 1) if ",," in s)
    assert_user_error(progon_on(tmp_path, text), "course.json", f"строка {line}")


def test_not_utf8(tmp_path):
    raw = json.dumps(GOOD, ensure_ascii=False).encode("cp1251")
    assert_user_error(progon_on(tmp_path, raw), "course.json", "UTF-8")


def test_missing_field(tmp_path):
    bad = json.loads(json.dumps(GOOD))
    del bad["attempts"][0]["score"]
    assert_user_error(progon_on(tmp_path, json.dumps(bad)), "score")


def test_bad_date(tmp_path):
    bad = json.loads(json.dumps(GOOD))
    bad["attempts"][0]["submitted"] = "01.10.2026 10:00"
    assert_user_error(progon_on(tmp_path, json.dumps(bad, ensure_ascii=False)), "01.10.2026 10:00")
