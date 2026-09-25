"""Общее для проверок PRG-12: приложение во временной папке."""

import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "checks" / "cmd3" / "course.json"
CASES = ROOT / "checks" / "run10" / "cases"
KEY = "test-key-2026"


def make_client(tmp_path, change=None):
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.fail("нет FastAPI или httpx — uv add fastapi uvicorn && uv add --dev httpx")
    from progon.api import Settings, create_app

    data = json.loads(COURSE.read_text(encoding="utf-8"))
    if change:
        change(data)
    course = tmp_path / "course.json"
    course.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    for task in data["tasks"]:
        shutil.copytree(CASES / "tests", tmp_path / "tests" / task)
    settings = Settings(course, tmp_path / "progon.db", tmp_path / "tests", KEY)
    return TestClient(create_app(settings), headers={"X-API-Key": KEY})


def solution(name):
    return {"calc.py": (CASES / "solutions" / name / "calc.py").read_text(encoding="utf-8")}


@pytest.fixture
def client(tmp_path):
    return make_client(tmp_path)
