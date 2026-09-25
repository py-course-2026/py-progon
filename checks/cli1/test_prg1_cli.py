"""PRG-1: каркас пакета progon и команда progon --version."""

import importlib.metadata
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def progon(*args):
    return subprocess.run(
        [sys.executable, "-m", "progon", *args],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
    )


def test_version_single_source():
    import progon as pkg

    meta = importlib.metadata.version("progon")
    assert getattr(pkg, "__version__", None) == meta, "progon.__version__ должна совпадать с версией из pyproject.toml"
    src = (ROOT / "progon" / "__init__.py").read_text(encoding="utf-8")
    assert meta not in src, "версия записана в __init__.py второй раз — берите её из метаданных пакета"


def test_python_m_progon_version():
    run = progon("--version")
    assert run.returncode == 0, run.stderr[-800:]
    assert run.stdout == f"progon {importlib.metadata.version('progon')}\n"


def test_help():
    run = progon("--help")
    assert run.returncode == 0, run.stderr[-800:]
    assert "--version" in run.stdout


def test_console_script_is_cli_main(capsys):
    eps = importlib.metadata.entry_points(group="console_scripts", name="progon")
    assert eps, "нет команды progon — проверьте [project.scripts] в pyproject.toml и выполните uv sync"
    main = next(iter(eps)).load()
    from progon import cli

    assert main is cli.main
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code in (0, None)
    assert capsys.readouterr().out.startswith("progon ")
