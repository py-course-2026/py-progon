"""PRG-12: POST /submissions — прогон, запись в базу, ответ студенту."""

from conftest import make_client, solution


def test_good_solution(client):
    r = client.post("/submissions", json={"login": "anna", "task": "week01", "files": solution("good")})
    assert r.status_code == 201, r.text
    body = r.json()
    assert (body["status"], body["passed"], body["total"], body["score"], body["failed"]) == ("ok", 3, 3, 10, [])
    assert isinstance(body["id"], int)
    history = client.get("/students/anna/history").json()
    assert [(h["task"], h["passed"], h["score"]) for h in history] == [("week01", 3, 10)]


def test_bad_solution_shows_failed_tests(client):
    r = client.post("/submissions", json={"login": "ivan", "task": "week02", "files": solution("bad")})
    body = r.json()
    assert (body["passed"], body["total"], body["score"]) == (1, 3, 3.33)
    assert sorted(f["test"].split("::")[-1] for f in body["failed"]) == ["test_add", "test_div_zero"]
    assert all(f["message"] for f in body["failed"])


def test_gradebook_uses_submissions(client):
    client.post("/submissions", json={"login": "olga", "task": "week03", "files": solution("good")})
    rows = {r["name"]: r for r in client.get("/gradebook").json()["rows"]}
    assert rows["Орлова Ольга"]["scores"][2] > 0


def test_timeout_of_task(tmp_path):
    def short(data):
        data["tasks"]["week01"] = {"deadline": "2030-01-01T00:00", "timeout": 2}

    c = make_client(tmp_path, short)
    body = c.post("/submissions", json={"login": "anna", "task": "week01", "files": solution("loop")}).json()
    assert (body["status"], body["score"]) == ("timeout", 0)
