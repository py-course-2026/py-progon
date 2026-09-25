"""PRG-4: progon gradebook --csv — ведомость, которую Excel открывает двойным щелчком."""

import csv
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "checks" / "cmd3" / "course.json"


def export(tmp_path):
    out = tmp_path / "ведомость.csv"
    r = subprocess.run([sys.executable, "-m", "progon", "gradebook", str(COURSE), "--csv", str(out)],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    return r, out


def test_csv_for_excel(tmp_path):
    r, out = export(tmp_path)
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout == "", "с --csv таблица идёт в файл, а не на экран"
    raw = out.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf"), "без BOM Excel прочитает UTF-8 как кракозябры"
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=";"))
    assert rows == [
        ["ФИО", "Группа", "week01", "week02", "week03", "Итог"],
        ["Петрова Анна", "ИИ-201", "10", "4,5", "0", "14,5"],
        ["Иванов Иван", "ИИ-201", "5", "8", "10", "23"],
        ["Орлова Ольга", "ИИ-202", "0", "0", "6", "6"],
    ], "разделитель «;», дробная часть — через запятую, как ждёт русский Excel"


def test_no_temporary_files_left(tmp_path):
    r, out = export(tmp_path)
    assert r.returncode == 0
    assert [p.name for p in tmp_path.iterdir()] == [out.name], "рядом с ведомостью остались лишние файлы"


def test_quotes_and_separators_are_escaped(tmp_path):
    import json

    course = json.loads(COURSE.read_text(encoding="utf-8"))
    course["students"][0]["name"] = 'Петрова "Аня"; Анна'
    src = tmp_path / "course.json"
    src.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "out.csv"
    r = subprocess.run([sys.executable, "-m", "progon", "gradebook", str(src), "--csv", str(out)],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    assert r.returncode == 0, r.stderr[-800:]
    rows = list(csv.reader(io.StringIO(out.read_text(encoding="utf-8-sig"), newline=""), delimiter=";"))
    assert rows[1][0] == 'Петрова "Аня"; Анна', "ФИО с «;» и кавычками — одна ячейка; пишите через модуль csv"
