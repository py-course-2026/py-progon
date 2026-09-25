"""PRG-12: HTTP API «Прогона» — доступ, задания, история, ведомость, проверка входа."""

import pytest
from conftest import KEY, solution


def test_health_is_public(client):
    from fastapi.testclient import TestClient

    from progon import __version__

    r = TestClient(client.app).get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "version": __version__}


@pytest.mark.parametrize("path", ["/tasks", "/gradebook", "/students/anna/history"])
def test_key_required(client, path):
    from fastapi.testclient import TestClient

    anon = TestClient(client.app)
    assert anon.get(path).status_code == 401
    assert anon.get(path, headers={"X-API-Key": KEY + "x"}).status_code == 401


def test_tasks(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert [t["name"] for t in r.json()] == ["week01", "week02", "week03"]
    assert r.json()[0] == {"name": "week01", "deadline": "2026-09-07T23:59:00", "max_score": 10}


def test_history_and_gradebook_start_empty(client):
    assert client.get("/students/anna/history").json() == []
    g = client.get("/gradebook").json()
    assert g["tasks"] == ["week01", "week02", "week03"]
    assert g["rows"][0] == {"name": "Петрова Анна", "group": "ИИ-201", "scores": [0, 0, 0], "total": 0}


@pytest.mark.parametrize("body", [
    {"login": "anna", "task": "week01", "files": {"../calc.py": "x = 1"}},
    {"login": "anna", "task": "week01", "files": {"sub/calc.py": "x = 1"}},
    {"login": "anna", "task": "week01", "files": {"calc.txt": "x = 1"}},
    {"login": "anna", "task": "week01", "files": {}},
    {"login": "anna", "task": "week01", "files": {"calc.py": "#" * 1_000_001}},
    {"login": "anna", "files": {"calc.py": "x = 1"}},
])
def test_bad_submissions_are_422(client, body):
    assert client.post("/submissions", json=body).status_code == 422


def test_unknown_task_and_student_are_404(client):
    assert client.post("/submissions", json={"login": "anna", "task": "week99",
                                             "files": solution("good")}).status_code == 404
    assert client.post("/submissions", json={"login": "ghost", "task": "week01",
                                             "files": solution("good")}).status_code == 404
