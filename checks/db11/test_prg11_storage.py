"""PRG-11: progon/storage.py — история прогонов в SQLite."""

import sqlite3
import time
from datetime import datetime, timedelta

import pytest

from progon.model import Outcome, TestResult
from progon.runner import RunResult
from progon.storage import Storage

D = datetime(2026, 10, 1, 12, 0)


def result(passed, failed, status="ok"):
    tests = [TestResult(f"t::ok{i}", Outcome.PASSED) for i in range(passed)]
    tests += [TestResult(f"t::bad{i}", Outcome.FAILED, f"assert {i} == 0") for i in range(failed)]
    return RunResult(status, tuple(tests), 0.25)


@pytest.fixture
def db(tmp_path):
    with Storage(tmp_path / "progon.db") as s:
        yield s


def test_save_and_history(db):
    db.save_run("anna", "w1", D, result(3, 0), 10)
    db.save_run("anna", "w1", D + timedelta(hours=1), result(1, 2), 3.33)
    db.save_run("ivan", "w2", D, RunResult("timeout", (), 10.0), 0)
    assert db.history("anna") == [
        ("w1", D.isoformat(), "ok", 3, 3, 10),
        ("w1", (D + timedelta(hours=1)).isoformat(), "ok", 1, 3, 3.33),
    ]
    assert db.history("ivan") == [("w2", D.isoformat(), "timeout", 0, 0, 0)]
    assert db.history("nobody") == []


def test_failed_tests(db):
    run_id = db.save_run("anna", "w1", D, result(1, 2), 3.33)
    assert db.failed_tests(run_id) == [("t::bad0", "assert 0 == 0"), ("t::bad1", "assert 1 == 0")]


def test_attempts_for_gradebook(db):
    db.save_run("anna", "w1", D + timedelta(hours=2), result(3, 0), 10)
    db.save_run("ivan", "w1", D, result(2, 1), 6.67)
    db.save_run("anna", "w2", D, result(0, 3), 0)
    attempts = db.attempts()
    assert [(a.login, a.task, a.score, a.submitted) for a in attempts] == [
        ("ivan", "w1", 6.67, D), ("anna", "w2", 0, D), ("anna", "w1", 10, D + timedelta(hours=2))]
    assert [a.login for a in db.attempts("w1")] == ["ivan", "anna"]


def test_quotes_are_data(db):
    db.save_run("o'brien", "w1'; DROP TABLE runs; --", D, result(1, 0), 10)
    assert db.history("o'brien")[0][0] == "w1'; DROP TABLE runs; --"


@pytest.mark.parametrize("sql", ["UPDATE runs SET score = 10", "DELETE FROM runs",
                                 "UPDATE results SET outcome = 'passed'", "DELETE FROM results"])
def test_attempts_are_immutable(db, sql):
    db.save_run("anna", "w1", D, result(1, 1), 5)
    with pytest.raises(sqlite3.DatabaseError):
        with db.conn:
            db.conn.execute(sql)
    assert db.history("anna")[0][-1] == 5


def test_schema_version_and_reopen(tmp_path):
    path = tmp_path / "progon.db"
    with Storage(path) as s:
        s.save_run("anna", "w1", D, result(1, 0), 10)
    with Storage(path) as s:
        assert len(s.history("anna")) == 1, "повторное открытие базы потеряло данные"
    conn = sqlite3.connect(path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] >= 1, "версия схемы — в PRAGMA user_version"
    conn.close()


def test_save_run_is_atomic(db, monkeypatch):
    bad = RunResult("ok", (TestResult("t::a", Outcome.PASSED), TestResult(None, Outcome.FAILED)), 0.1)
    with pytest.raises(sqlite3.DatabaseError):
        db.save_run("anna", "w1", D, bad, 5)
    assert db.history("anna") == [], "прогон записан без результатов — нужна одна транзакция"


def test_many_runs_are_fast(tmp_path):
    with Storage(tmp_path / "big.db") as s:
        start = time.perf_counter()
        for i in range(3000):
            s.save_run(f"s{i % 300:03d}", f"w{i % 14}", D + timedelta(minutes=i), result(2, 1), 6.67)
        took = time.perf_counter() - start
        assert len(s.attempts()) == 3000
    assert took < 20, f"3000 прогонов записывались {took:.0f} с"
