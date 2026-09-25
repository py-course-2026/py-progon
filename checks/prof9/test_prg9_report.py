"""PRG-9: docs/PERFORMANCE.md — замеры и профиль."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def text():
    p = ROOT / "docs" / "PERFORMANCE.md"
    if not p.is_file():
        pytest.fail("нет файла docs/PERFORMANCE.md")
    return p.read_text(encoding="utf-8")


def section(body, title):
    m = re.search(rf"^##\s+{title}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    if not m or not m[1].strip():
        pytest.fail(f"нет раздела «## {title}» или он пустой")
    return m[1]


def test_measurements():
    s = section(text(), "Замеры")
    times = re.findall(r"\d+(?:[.,]\d+)?\s*с\b", s)
    assert len(times) >= 4, "в замерах — время до и после хотя бы для двух команд, в секундах: «0,35 с»"


def test_profile():
    s = section(text(), "Профиль")
    assert re.search(r"ncalls\s+tottime\s+percall\s+cumtime\s+percall", s), \
        "вставьте вывод cProfile — со строкой заголовка ncalls tottime percall cumtime percall"
    assert s.count("```") >= 4, "два профиля — до и после — в блоках кода"


def test_conclusions():
    s = section(text(), "Что ускорили")
    assert len(re.findall(r"^- ", s, re.M)) >= 2, "перечислите, что и почему ускорили, — хотя бы два пункта"
    assert "TODO" not in text()
