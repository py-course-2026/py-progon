"""PRG-13: progon/predict.py — модель риска и её проверка на отложенной выборке."""

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRAIN, TEST = HERE / "train.csv", HERE / "test.csv"


@pytest.fixture(scope="module")
def model():
    try:
        from progon import predict
    except ImportError as e:
        pytest.fail(f"не импортируется progon.predict ({e}) — uv add pandas scikit-learn matplotlib")
    return predict.train(TRAIN)


def test_better_than_baseline(model):
    from progon import predict

    scores = predict.evaluate(model, TEST)
    assert scores["baseline"] == pytest.approx(0.69, abs=0.01), "базовая модель — «как большинство» на отложенной выборке"
    assert scores["accuracy"] >= 0.75, f"доля верных {scores['accuracy']} — модель почти не лучше угадывания"
    assert scores["accuracy"] >= scores["baseline"] + 0.05


def test_risk_is_probability_and_sensible(model):
    from progon import predict

    strong = {"first_score": 9.5, "attempts_day1": 1, "hours_before": 120, "prev_best": 9.0}
    weak = {"first_score": 1.0, "attempts_day1": 4, "hours_before": -10, "prev_best": 2.0}
    r_strong, r_weak = predict.risk(model, strong), predict.risk(model, weak)
    assert 0 <= r_strong <= 1 and 0 <= r_weak <= 1
    assert r_strong < 0.3 < 0.7 < r_weak, (r_strong, r_weak)


def test_save_and_load(model, tmp_path):
    from progon import predict

    predict.save(model, tmp_path / "model.pkl")
    again = predict.load(tmp_path / "model.pkl")
    x = {"first_score": 5, "attempts_day1": 2, "hours_before": 24, "prev_best": 6}
    assert predict.risk(again, x) == predict.risk(model, x)


def test_bad_history(tmp_path):
    from progon import predict
    from progon.errors import InputError

    p = tmp_path / "h.csv"
    p.write_text("first_score,at_risk\n5,0\n", encoding="utf-8")
    with pytest.raises(InputError):
        predict.train(p)
    with pytest.raises(InputError):
        predict.train(tmp_path / "nope.csv")


def test_model_command(tmp_path):
    r = subprocess.run([sys.executable, "-m", "progon", "model", str(TRAIN), "--test", str(TEST),
                        "--out", str(tmp_path / "m.pkl")], capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.startswith("Доля верных: 0.") and "у базовой модели: 0.69" in r.stdout
    assert (tmp_path / "m.pkl").stat().st_size > 0


def test_risk_endpoint(model, tmp_path):
    import json
    import shutil

    from fastapi.testclient import TestClient

    from progon import predict
    from progon.api import Settings, create_app

    course = tmp_path / "course.json"
    shutil.copy(ROOT / "checks" / "cmd3" / "course.json", course)
    predict.save(model, tmp_path / "m.pkl")
    body = {"first_score": 1.0, "attempts_day1": 4, "hours_before": -10, "prev_best": 2.0}
    with_model = TestClient(create_app(Settings(course, tmp_path / "p.db", tmp_path, "k", tmp_path / "m.pkl")),
                            headers={"X-API-Key": "k"})
    r = with_model.post("/risk", json=body)
    assert r.status_code == 200 and r.json()["risk"] > 0.7
    assert with_model.post("/risk", json={**body, "first_score": 11}).status_code == 422
    without = TestClient(create_app(Settings(course, tmp_path / "p.db", tmp_path, "k")), headers={"X-API-Key": "k"})
    assert without.post("/risk", json=body).status_code == 503
    assert json.loads(json.dumps(body))
