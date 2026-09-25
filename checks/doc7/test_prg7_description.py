"""PRG-7: описание программы по ГОСТ 19.402-78."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SECTIONS = ["Общие сведения", "Функциональное назначение", "Описание логической структуры",
            "Используемые технические средства", "Вызов и загрузка", "Входные данные", "Выходные данные"]


def text():
    p = ROOT / "docs" / "DESCRIPTION.md"
    if not p.is_file():
        pytest.fail("нет файла docs/DESCRIPTION.md")
    return p.read_text(encoding="utf-8")


def section(body, title):
    m = re.search(rf"^##\s*(?:\d+\.?\s+)?{title}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m[1] if m else None


def test_sections_in_order():
    body = text()
    assert "TODO" not in body
    positions = []
    for title in SECTIONS:
        m = re.search(rf"^##\s*(?:\d+\.?\s+)?{title}\s*$", body, re.M)
        assert m, f"нет раздела «{title}» (заголовок уровня ##)"
        assert section(body, title).strip(), f"раздел «{title}» пустой"
        positions.append(m.start())
    assert positions == sorted(positions), "разделы — в порядке ГОСТ 19.402-78"


def test_structure_lists_every_module():
    structure = section(text(), "Описание логической структуры")
    modules = sorted(p.stem for p in (ROOT / "progon").glob("*.py"))
    missing = [m for m in modules if m not in structure]
    assert not missing, f"в описании логической структуры не упомянуты модули: {missing}"


def test_has_flowchart():
    structure = section(text(), "Описание логической структуры")
    assert re.search(r"```mermaid\s+flowchart", structure), "нужна схема алгоритма — блок ```mermaid с flowchart"


def test_data_formats():
    body = text()
    inp, out = section(body, "Входные данные"), section(body, "Выходные данные")
    assert "JSON" in inp and "XML" in inp, "во входных данных — файл курса JSON и отчёт JUnit XML"
    assert "CSV" in out, "в выходных данных — ведомость CSV"
