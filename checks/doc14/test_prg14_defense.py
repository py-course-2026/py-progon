"""PRG-14: материалы защиты — отчёт и слайды."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def read(rel):
    p = ROOT / rel
    if not p.is_file():
        pytest.fail(f"нет файла {rel}")
    text = p.read_text(encoding="utf-8")
    assert "TODO" not in text, f"в {rel} остались TODO"
    return text


def test_report_sections():
    text = read("docs/REPORT.md")
    for head in ("Что сделано", "Архитектура", "Что не сделано", "Выводы"):
        m = re.search(rf"^##\s+{head}[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        assert m and len(m[1].strip()) >= 100, f"раздел «{head}» отсутствует или слишком короткий"


def test_slides():
    slides = [s for s in re.split(r"^---\s*$", read("docs/SLIDES.md"), flags=re.M) if s.strip()]
    assert len(slides) >= 6, f"слайдов {len(slides)}, нужно не меньше шести (разделитель — строка ---)"
    for i, s in enumerate(slides, 1):
        assert re.search(r"^#{1,2} ", s, re.M), f"у слайда {i} нет заголовка"
