"""PRG-10: progon/runner.py и progon run — тесты решения в отдельном процессе."""

import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"
TESTS = CASES / "tests"
ROOT = HERE.parents[1]


def sol(name):
    return CASES / "solutions" / name


def test_good_solution():
    from progon.runner import run_tests

    r = run_tests(sol("good"), TESTS, timeout=30)
    assert (r.status, r.passed, r.total) == ("ok", 3, 3)
    assert r.duration > 0


def test_bad_solution():
    from progon.model import Outcome
    from progon.runner import run_tests

    r = run_tests(sol("bad"), TESTS, timeout=30)
    assert (r.status, r.passed, r.total) == ("ok", 1, 3)
    failed = {x.test.split("::")[-1]: x for x in r.results if x.outcome is Outcome.FAILED}
    assert set(failed) == {"test_add", "test_div_zero"}
    assert failed["test_add"].message


def test_syntax_error_is_reported_not_raised():
    from progon.runner import run_tests

    r = run_tests(sol("crash"), TESTS, timeout=30)
    assert r.status in ("ok", "error") and r.passed == 0


def test_timeout():
    from progon.runner import run_tests

    start = time.monotonic()
    r = run_tests(sol("loop"), TESTS, timeout=2)
    took = time.monotonic() - start
    assert r.status == "timeout" and r.passed == 0
    assert took < 8, f"прогон с таймаутом 2 с шёл {took:.0f} с"


def test_solution_folder_is_not_touched(tmp_path):
    from progon.runner import run_tests

    work = tmp_path / "anna"
    shutil.copytree(sol("good"), work)
    before = sorted(p.name for p in work.rglob("*"))
    run_tests(work, TESTS, timeout=30)
    assert sorted(p.name for p in work.rglob("*")) == before, "прогон оставил файлы в папке решения"


def test_missing_folder():
    from progon.errors import InputError
    from progon.runner import run_tests

    with pytest.raises(InputError, match="nowhere"):
        run_tests(CASES / "nowhere", TESTS)


def test_run_many_is_parallel_and_ordered():
    from progon.runner import run_many

    start = time.monotonic()
    runs = run_many([sol("slow"), sol("bad"), sol("slow"), sol("slow")], TESTS, timeout=30, workers=4)
    took = time.monotonic() - start
    assert [(r.passed, r.total) for r in runs] == [(3, 3), (1, 3), (3, 3), (3, 3)]
    one = runs[0].duration
    assert took < one * 2.5, f"4 решения по {one:.1f} с шли {took:.1f} с — прогоны идут по очереди?"


def test_run_command(tmp_path):
    root = tmp_path / "solutions"
    for name, src in (("ivan", "bad"), ("anna", "good"), ("zoe", "loop")):
        shutil.copytree(sol(src), root / name)
    r = subprocess.run([sys.executable, "-m", "progon", "run", str(root), str(TESTS), "--timeout", "3",
                        "--workers", "3"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                       timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    lines = [line.split("\t") for line in r.stdout.splitlines()]
    assert lines[0] == ["Решение", "Прошло", "Всего", "Статус", "Время, с"]
    assert [row[:4] for row in lines[1:]] == [["anna", "3", "3", "ok"], ["ivan", "1", "3", "ok"],
                                              ["zoe", "0", "0", "timeout"]]
