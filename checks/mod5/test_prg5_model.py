"""PRG-5: progon/model.py — классы предметной области."""

import dataclasses
from datetime import datetime
from enum import StrEnum

import pytest

from progon.model import Attempt, Outcome, Student, Task, TestResult

D = datetime(2026, 10, 1, 23, 59)


def test_outcome_is_str_enum():
    assert issubclass(Outcome, StrEnum)
    assert [o.value for o in Outcome] == ["passed", "failed", "error", "skipped"]
    assert Outcome("error") is Outcome.ERROR
    assert f"{Outcome.FAILED}" == "failed" and Outcome.FAILED == "failed"


def test_test_result():
    r = TestResult("tests.t::test_a", Outcome.FAILED, "assert 1 == 2", 0.5)
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.message = "другое"
    assert not hasattr(r, "__dict__"), "TestResult — dataclass со slots=True"
    assert r == TestResult("tests.t::test_a", Outcome.FAILED, "assert 1 == 2", 0.5)
    assert len({r, TestResult("tests.t::test_a", Outcome.FAILED, "assert 1 == 2", 0.5)}) == 1
    assert not r.ok
    assert TestResult("x", Outcome.PASSED).ok and TestResult("x", Outcome.SKIPPED).ok
    assert TestResult("x", Outcome.PASSED).message is None


def test_test_result_from_dict():
    r = TestResult.from_dict({"test": "t::x", "outcome": "error", "message": "boom", "time": 0.25})
    assert r == TestResult("t::x", Outcome.ERROR, "boom", 0.25)
    assert r.outcome is Outcome.ERROR
    with pytest.raises(ValueError):
        TestResult.from_dict({"test": "t::x", "outcome": "exploded", "message": None, "time": 0})


def test_task_defaults_and_validation():
    t = Task("week01", D)
    assert (t.max_score, t.timeout, t.open_tests) == (10, 10.0, frozenset())
    t2 = Task("week02", D, max_score=20, timeout=600, open_tests=["test_a", "test_b", "test_a"])
    assert t2.open_tests == frozenset({"test_a", "test_b"}) and isinstance(t2.open_tests, frozenset)
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.max_score = 100
    for bad in (dict(max_score=0), dict(timeout=0), dict(timeout=601), dict(timeout=-1)):
        with pytest.raises(ValueError):
            Task("w", D, **bad)
    with pytest.raises(ValueError):
        Task("  ", D)


def test_student_is_frozen():
    s = Student("anna", "Петрова Анна", "ИИ-201")
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.group = "ИИ-202"
    assert s == Student("anna", "Петрова Анна", "ИИ-201")


def test_attempt():
    a = Attempt("anna", "week01", 7, D)
    login, task, score, submitted = a
    assert (login, task, score, submitted) == ("anna", "week01", 7, D)
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.score = 10
    with pytest.raises(ValueError):
        Attempt("anna", "week01", -1, D)


def test_attempts_sort_by_time():
    late = Attempt("anna", "w1", 1, datetime(2026, 10, 3))
    early = Attempt("zoe", "w1", 9, datetime(2026, 10, 1))
    middle = Attempt("boris", "w2", 5, datetime(2026, 10, 2))
    assert sorted([late, early, middle]) == [early, middle, late]
    assert early < late and late > middle
