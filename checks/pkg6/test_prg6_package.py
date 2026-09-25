"""PRG-6: команда progon check и пакет, который можно поставить на сервер колледжа."""

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "checks" / "cmd3" / "course.json"


def progon(*args):
    return subprocess.run([sys.executable, "-m", "progon", *args], capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT)


def test_check_command():
    r = progon("check", str(COURSE))
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.splitlines() == [
        "Заданий: 3, студентов: 3, попыток: 7, продлений: 1",
        "Попыток после срока: 2",
        "Курс в порядке.",
    ]


def test_check_reports_bad_data(tmp_path):
    data = json.loads(COURSE.read_text(encoding="utf-8"))
    data["attempts"][0]["score"] = 99
    p = tmp_path / "course.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    r = progon("check", str(p))
    assert r.returncode == 1 and r.stderr.startswith("progon: ошибка: ") and "Traceback" not in r.stderr
    assert r.stdout == ""


@pytest.fixture(scope="module")
def wheel(tmp_path_factory):
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("нет uv — сборку пакета проверит GitHub Actions")
    out = tmp_path_factory.mktemp("dist")
    r = subprocess.run([uv, "build", "--wheel", "--out-dir", str(out)], capture_output=True,
                       text=True, cwd=ROOT)
    assert r.returncode == 0, "uv build не собрал пакет:\n" + r.stderr[-1500:]
    wheels = list(out.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def test_wheel_contents(wheel):
    from progon import __version__

    assert wheel.name == f"progon-{__version__}-py3-none-any.whl"
    names = zipfile.ZipFile(wheel).namelist()
    for module in ("__init__", "__main__", "cli", "course", "errors", "export", "gradebook", "model", "report"):
        assert f"progon/{module}.py" in names, f"в пакете нет progon/{module}.py"
    extra = [n for n in names if n.split("/")[0] in ("tests", "checks", "docs", "letters", "tickets")]
    assert not extra, f"в пакет попало лишнее: {extra[:5]}"


def test_wheel_metadata(wheel):
    z = zipfile.ZipFile(wheel)
    info = next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))
    eps = next(n for n in z.namelist() if n.endswith(".dist-info/entry_points.txt"))
    assert "Version: 0.1.0" in z.read(info).decode()
    assert "progon = progon.cli:main" in z.read(eps).decode()
