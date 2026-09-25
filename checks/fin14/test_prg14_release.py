"""PRG-14: выпуск 1.0 — версия, журнал, руководство, протокол приёмки."""

import re
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "checks"))
from tzdoc import items, sections  # noqa: E402

COMMANDS = ["gradebook", "check", "report", "stats", "run", "history", "chart", "model", "serve"]
STATUS = re.compile(r"\b(выполнено|частично|не выполнено)\b")


def read(rel):
    p = ROOT / rel
    if not p.is_file():
        pytest.fail(f"нет файла {rel}")
    return p.read_text(encoding="utf-8")


def test_version_one():
    version = tomllib.loads(read("pyproject.toml"))["project"]["version"]
    assert int(version.split(".")[0]) >= 1, f"версия {version} — выпуск для всех групп: 1.0.0"


def test_changelog_release():
    text = read("CHANGELOG.md")
    heads = re.findall(r"^## \[(\d+)\.\d+\.\d+\] — \d{4}-\d{2}-\d{2}\s*$", text, re.M)
    assert heads and int(heads[0]) >= 1, "верхний раздел журнала — выпуск 1.x.y с датой"
    top = text[text.index("## [") + 1:]
    top = top[: top.find("\n## [")]
    assert len(re.findall(r"^- ", top, re.M)) >= 3, "в выпуске 1.0 — хотя бы три пункта изменений"


def test_user_guide_covers_all_commands():
    text = read("docs/USER_GUIDE.md")
    missing = [c for c in COMMANDS if f"progon {c}" not in text]
    assert not missing, f"в руководстве не описаны команды: {missing}"


def test_acceptance_protocol_covers_every_test():
    tz_tests = {n for n, _ in items(sections({"a": r"^##\s*\d+\.?\s+Порядок контроля и приёмки"})["a"], "ПИ")}
    assert tz_tests, "в ТЗ нет приёмочных испытаний ПИ-NN"
    text = read("docs/ACCEPTANCE.md")
    rows = {m[1]: line for line in text.splitlines() if (m := re.search(r"ПИ-(\d{2})", line))}
    missing = sorted(tz_tests - set(rows))
    assert not missing, f"в протоколе нет испытаний: {['ПИ-' + m for m in missing]}"
    for n in sorted(tz_tests):
        assert STATUS.search(rows[n]), f"у ПИ-{n} нет итога: выполнено, частично или не выполнено"
