"""PRG-6: релиз 0.1 — журнал изменений и руководство пользователя."""

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def read(rel):
    p = ROOT / rel
    if not p.is_file():
        pytest.fail(f"нет файла {rel}")
    return p.read_text(encoding="utf-8")


def project_version():
    return tomllib.loads(read("pyproject.toml"))["project"]["version"]


def test_changelog_has_release():
    text = read("CHANGELOG.md")
    heads = re.findall(r"^## \[(\d+\.\d+\.\d+)\] — (\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    assert heads, "в CHANGELOG.md нужен раздел вида «## [0.1.0] — 2026-10-12»"
    assert heads[0][0] == project_version(), "верхний выпуск в журнале должен совпадать с версией в pyproject.toml"
    assert "0.1.0" in [v for v, _ in heads]


def test_changelog_lists_changes():
    text = read("CHANGELOG.md")
    start = text.index("## [0.1.0]") if "## [0.1.0]" in text else pytest.fail("нет раздела [0.1.0]")
    rest = text[start + 1:]
    section = rest[: rest.find("\n## [")] if "\n## [" in rest else rest
    items = re.findall(r"^- .+", section, re.M)
    assert len(items) >= 3, "в выпуске 0.1.0 перечислите хотя бы три изменения пунктами списка"
    for cmd in ("gradebook", "report", "check"):
        assert cmd in section, f"в журнале выпуска не упомянута команда {cmd}"


def test_user_guide():
    text = read("docs/USER_GUIDE.md")
    assert "TODO" not in text
    for head in ("Назначение", "Установка", "Команды", "Сообщения об ошибках"):
        assert re.search(rf"^##\s+.*{head}", text, re.M), f"в руководстве нет раздела «{head}»"
    for cmd in ("progon gradebook", "progon report", "progon check", "--csv"):
        assert cmd in text, f"в руководстве не описано: {cmd}"
    assert text.count("```") >= 6, "покажите команды примерами — хотя бы три блока кода"
