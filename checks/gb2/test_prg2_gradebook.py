"""PRG-2: progon/gradebook.py — лучший балл, опоздания, продления и ведомость."""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from progon import gradebook as gb

ROOT = Path(__file__).resolve().parents[2]
D = datetime(2026, 10, 1, 23, 59)
DEADLINES = {"w1": D, "w2": D + timedelta(days=7)}
H = timedelta(hours=1)


def test_effective_score_on_time_and_late():
    assert gb.effective_score(8, D - H, D) == 8
    assert gb.effective_score(8, D, D) == 8, "ровно в срок — ещё не опоздание"
    assert gb.effective_score(8, D + H, D) == 4
    assert gb.effective_score(9, D + H, D, late_factor=0.8) == pytest.approx(7.2)


def test_best_scores_takes_best_effective():
    attempts = [
        ("ivan", "w1", 6, D - 2 * H),
        ("ivan", "w1", 10, D + H),        # 10 × 0,5 = 5 — хуже, чем 6 вовремя
        ("ivan", "w2", 3, D),
        ("anna", "w1", 10, D - H),
        ("anna", "w1", 7, D - 3 * H),
    ]
    assert gb.best_scores(attempts, DEADLINES) == {("ivan", "w1"): 6, ("ivan", "w2"): 3, ("anna", "w1"): 10}


def test_extension_is_personal():
    attempts = [("ivan", "w1", 10, D + H), ("anna", "w1", 10, D + H)]
    ext = {("ivan", "w1"): D + 48 * H}
    assert gb.best_scores(attempts, DEADLINES, ext) == {("ivan", "w1"): 10, ("anna", "w1"): 5}


def test_unknown_task_is_an_error():
    with pytest.raises(ValueError, match="w9"):
        gb.best_scores([("ivan", "w9", 5, D)], DEADLINES)


def test_gradebook_rows():
    attempts = [
        ("ivan", "w2", 7, D),
        ("anna", "w1", 10, D - H),
        ("anna", "w2", 9, D + 8 * 24 * H),   # после срока w2: 4,5
        ("ghost", "w1", 10, D),              # не в списке студентов — в ведомость не попадает
    ]
    students = [("anna", "Петрова Анна", "ИИ-201"), ("ivan", "Иванов Иван", "ИИ-202"), ("olga", "Орлова Ольга", "ИИ-201")]
    rows = gb.gradebook(attempts, students, ["w1", "w2"], DEADLINES)
    assert rows == [
        ["Петрова Анна", "ИИ-201", 10, 4.5, 14.5],
        ["Иванов Иван", "ИИ-202", 0, 7, 7],
        ["Орлова Ольга", "ИИ-201", 0, 0, 0],
    ]


def test_gradebook_does_not_change_inputs():
    attempts = [("anna", "w1", 10, D)]
    students = [("anna", "Петрова Анна", "ИИ-201")]
    deadlines = dict(DEADLINES)
    ext = {("anna", "w2"): D}
    gb.gradebook(attempts, students, ["w1", "w2"], deadlines, ext)
    assert attempts == [("anna", "w1", 10, D)] and deadlines == DEADLINES and ext == {("anna", "w2"): D}


def test_gradebook_for_whole_college_is_fast():
    code = (
        "import sys; sys.path.insert(0, 'checks/gb2'); from bigdata import make; "
        "from progon.gradebook import gradebook; "
        "a, s, t, d, e = make(); rows = gradebook(a, s, t, d, e); "
        "print(len(rows), round(sum(r[-1] for r in rows), 2))"
    )
    try:
        run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             encoding="utf-8", cwd=ROOT, timeout=20)
    except subprocess.TimeoutExpired:
        pytest.fail("ведомость на 300 студентов × 14 заданий × 50 попыток не собралась за 20 с — "
                    "для каждой клетки ведомости перебираются все попытки?")
    assert run.returncode == 0, run.stderr[-800:]
    rows, total = run.stdout.split()
    assert rows == "300"
    assert float(total) == pytest.approx(41905)
