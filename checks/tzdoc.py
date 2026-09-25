"""Разбор docs/TZ.md для проверок тикетов о ТЗ: разделы, пункты требований, ссылки на письма.

Письма заказчика — letters/NN-*.md, абзацы в них помечены **[А1]**, **[Б3]**…: буква — номер
письма (А — первое, Б — второе…), число — номер абзаца.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TZ = ROOT / "docs" / "TZ.md"
LETTERS = ROOT / "letters"

REF = re.compile(r"\[([А-Я]\d+(?:\s*,\s*[А-Я]\d+)*)\]")


def text():
    if not TZ.is_file():
        pytest.fail("нет файла docs/TZ.md")
    return TZ.read_text(encoding="utf-8")


def sections(spec):
    """{ключ: регулярка заголовка} -> {ключ: непустые строки раздела до следующего заголовка}."""
    lines = text().splitlines()
    heads = [i for i, line in enumerate(lines) if line.startswith("#")]
    out = {}
    for key, pattern in spec.items():
        found = [i for i, line in enumerate(lines) if re.match(pattern, line.strip())]
        if not found:
            pytest.fail(f"в docs/TZ.md нет раздела, заголовок которого подходит под {pattern!r}")
        start = found[0]
        end = next((h for h in heads if h > start), len(lines))
        out[key] = [line.strip() for line in lines[start + 1:end] if line.strip()]
    return out


def items(lines, prefix):
    """Пункты вида «- ФТ-01. текст» -> [(номер, строка)]."""
    return [(m[1], line) for line in lines if (m := re.match(rf"[-*]\s*{prefix}-(\d{{2}})\b", line))]


def listed(lines):
    """Пункты маркированного или нумерованного списка."""
    return [line for line in lines if re.match(r"[-*]\s|\d+\.\s", line)]


def refs(line):
    """Ссылки на абзацы писем в строке: {"А3", "Б4"}."""
    return {r.strip() for m in REF.finditer(line) for r in m[1].split(",")}


def letter_paragraphs():
    """Все абзацы всех писем: {"А1", …, "Б8"}."""
    found = set()
    for path in sorted(LETTERS.glob("*.md")):
        found |= set(re.findall(r"\*\*\[([А-Я]\d+)\]\*\*", path.read_text(encoding="utf-8")))
    return found
