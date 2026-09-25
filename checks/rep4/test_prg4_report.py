"""PRG-4: progon/report.py и команда progon report — разбор отчёта pytest --junitxml."""

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def progon(*args):
    return subprocess.run([sys.executable, "-m", "progon", *args], capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT)


def test_parse_real_pytest_report():
    from progon.report import parse_junit

    results = parse_junit(HERE / "report.xml")
    assert [(r["test"], r["outcome"]) for r in results] == [
        ("tests.test_basic::test_add", "passed"),
        ("tests.test_basic::test_add_many[1-1-2]", "passed"),
        ("tests.test_basic::test_add_many[0-0-0]", "passed"),
        ("tests.test_basic::test_add_many[-1-1-1]", "failed"),
        ("tests.test_basic::test_greet", "failed"),
        ("tests.test_basic::test_with_config", "error"),
        ("tests.test_basic::test_later", "skipped"),
        ("tests.test_basic::test_round", "skipped"),
    ]
    by = {r["test"]: r for r in results}
    assert by["tests.test_basic::test_add"]["message"] is None
    assert by["tests.test_basic::test_add_many[-1-1-1]"]["message"] == "assert 0 == 1"
    assert by["tests.test_basic::test_greet"]["message"] == \
        "AssertionError: приветствие должно заканчиваться восклицательным знаком"
    assert by["tests.test_basic::test_with_config"]["message"] == \
        'failed on setup with "FileNotFoundError: нет файла config.toml"'
    assert all(isinstance(r["time"], float) for r in results)


def test_message_falls_back_to_text(tmp_path):
    from progon.report import parse_junit

    p = tmp_path / "r.xml"
    p.write_text('<testsuite><testcase classname="t" name="x"><failure>\n\n  первая строка\nвторая'
                 '</failure></testcase></testsuite>', encoding="utf-8")
    assert parse_junit(p)[0]["message"] == "первая строка"


def test_summarize():
    from progon.report import parse_junit, summarize

    assert summarize(parse_junit(HERE / "report.xml")) == \
        {"total": 8, "passed": 3, "failed": 2, "error": 1, "skipped": 2}
    assert summarize([]) == {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}


def test_report_command():
    r = progon("report", str(HERE / "report.xml"))
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.splitlines() == [
        "Тестов: 8, прошло: 3, упало: 2, ошибок: 1, пропущено: 2",
        "FAILED tests.test_basic::test_add_many[-1-1-1] — assert 0 == 1",
        "FAILED tests.test_basic::test_greet — AssertionError: приветствие должно заканчиваться "
        "восклицательным знаком",
        'ERROR tests.test_basic::test_with_config — failed on setup with "FileNotFoundError: '
        'нет файла config.toml"',
    ]


def test_report_all_passed():
    r = progon("report", str(HERE / "clean.xml"))
    assert r.stdout.splitlines() == ["Тестов: 3, прошло: 3, упало: 0, ошибок: 0, пропущено: 0"]


@pytest.mark.parametrize(("content", "part"), [
    (None, "nope.xml"),
    ("<testsuite><testcase name='x'>\n</testsuite>", "строка 2"),
])
def test_report_input_errors(tmp_path, content, part):
    if content is None:
        path = "nope.xml"
    else:
        path = tmp_path / "broken.xml"
        path.write_text(content, encoding="utf-8")
    r = progon("report", str(path))
    assert r.returncode == 1 and "Traceback" not in r.stderr
    assert r.stderr.startswith("progon: ошибка: ") and part in r.stderr, r.stderr


def test_big_report_is_fast(tmp_path):
    cases = "".join(f'<testcase classname="t" name="test_{i}" time="0.001"/>' for i in range(50_000))
    p = tmp_path / "big.xml"
    p.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>", encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "progon", "report", str(p)], capture_output=True,
                       text=True, encoding="utf-8", cwd=ROOT, timeout=20)
    assert r.stdout.startswith("Тестов: 50000, прошло: 50000")
