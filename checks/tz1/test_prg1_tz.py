"""PRG-1: черновик ТЗ в docs/TZ.md.

Проверяется форма, которую можно проверить автоматически: разделы на месте, требования
пронумерованы, измеримы и прослеживаются до письма заказчика. Содержание читает
тимлид на ревью.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TZ = ROOT / "docs" / "TZ.md"
LETTER = ROOT / "letters" / "01-somova.md"

SECTIONS = {
    "general": r"^##\s*1\.?\s+Общие сведения",
    "purpose": r"^##\s*2\.?\s+Назначение",
    "object": r"^##\s*3\.?\s+Характеристика объекта",
    "system": r"^##\s*4\.?\s+Требования к системе",
    "functions": r"^###\s*4\.1\.?\s+Требования к функциям",
    "quality": r"^###\s*4\.2\.?\s+Требования к надёжности",
    "data": r"^###\s*4\.3\.?\s+Требования к входным",
    "questions": r"^##\s*5\.?\s+Открытые вопросы",
}
REF = re.compile(r"\[(А\d+(?:\s*,\s*А\d+)*)\]")
MUST_COVER = [f"А{n}" for n in range(2, 10)]  # абзацы письма с требованиями


def text():
    if not TZ.is_file():
        pytest.fail("нет файла docs/TZ.md")
    return TZ.read_text(encoding="utf-8")


def sections():
    """Словарь «ключ раздела -> строки раздела» (до следующего заголовка любого уровня)."""
    lines = text().splitlines()
    starts = {}
    for key, pattern in SECTIONS.items():
        found = [i for i, line in enumerate(lines) if re.match(pattern, line.strip())]
        if not found:
            pytest.fail(f"в docs/TZ.md нет раздела, заголовок которого подходит под {pattern!r}")
        starts[key] = found[0]
    heads = sorted(i for i, line in enumerate(lines) if line.startswith("#"))
    out = {}
    for key, i in starts.items():
        end = next((h for h in heads if h > i), len(lines))
        out[key] = [line.strip() for line in lines[i + 1:end] if line.strip()]
    return out


def items(lines, prefix):
    """Пункты вида «- ФТ-01. текст» -> [(номер, строка)]."""
    return [(m[1], line) for line in lines if (m := re.match(rf"[-*]\s*{prefix}-(\d{{2}})\b", line))]


def refs(line):
    return {r.strip() for m in REF.finditer(line) for r in m[1].split(",")}


def letter_paragraphs():
    return set(re.findall(r"\*\*\[(А\d+)\]\*\*", LETTER.read_text(encoding="utf-8")))


def test_no_todo_left():
    assert "TODO" not in text(), "в docs/TZ.md остались TODO — замените их своим текстом"


def test_sections_are_filled():
    s = sections()
    for key in ("general", "purpose", "object", "data"):
        assert s[key], f"раздел {SECTIONS[key]!r} пустой"


def test_functional_requirements():
    fts = items(sections()["functions"], "ФТ")
    assert len(fts) >= 8, f"функциональных требований {len(fts)}, нужно не меньше восьми: «- ФТ-01. …»"
    ids = [n for n, _ in fts]
    assert len(ids) == len(set(ids)), "номера ФТ повторяются"


def test_quality_requirements_are_measurable():
    nfs = items(sections()["quality"], "НФ")
    assert len(nfs) >= 4, f"нефункциональных требований {len(nfs)}, нужно не меньше четырёх: «- НФ-01. …»"
    ids = [n for n, _ in nfs]
    assert len(ids) == len(set(ids)), "номера НФ повторяются"
    for n, line in nfs:
        body = REF.sub("", re.sub(r"^[-*]\s*НФ-\d{2}\.?", "", line))
        assert re.search(r"\d", body), f"НФ-{n} не измеримо — в нём нет ни одного числа: {line!r}"


def test_every_requirement_traces_to_letter():
    s = sections()
    known = letter_paragraphs()
    for n, line in items(s["functions"], "ФТ") + items(s["quality"], "НФ"):
        r = refs(line)
        assert r, f"у требования нет ссылки на письмо вида [А3]: {line!r}"
        assert r <= known, f"ссылка на абзац, которого нет в письме, {sorted(r - known)}: {line!r}"


def test_letter_is_covered():
    s = sections()
    cited = set()
    for _, line in items(s["functions"], "ФТ") + items(s["quality"], "НФ"):
        cited |= refs(line)
    missed = [p for p in MUST_COVER if p not in cited]
    assert not missed, f"абзацы письма с требованиями, на которые не ссылается ни одно требование: {missed}"


def test_data_section_has_formats():
    listed = [line for line in sections()["data"] if re.match(r"[-*]\s", line)]
    assert len(listed) >= 3, "в 4.3 нужны хотя бы три пункта списка: что на входе, что на выходе, в каком формате"


def test_open_questions():
    qs = [line for line in sections()["questions"] if re.match(r"[-*]\s|\d+\.\s", line)]
    real = [q for q in qs if "?" in REF.sub("", q)]
    assert len(real) >= 5, f"открытых вопросов {len(real)}, нужно не меньше пяти — пунктов списка со знаком «?»"
    for q in real:
        assert refs(q), f"вопрос не ссылается на абзац письма: {q!r}"
