"""Файл курса размером с колледж: 300 студентов, 14 заданий, по 50 попыток.

    uv run python checks/perf9/bigcourse.py big.json
"""

import json
import random
import sys
from datetime import datetime, timedelta

START = datetime(2026, 9, 1, 9, 0)


def make(seed=14):
    rnd = random.Random(seed)
    tasks = {f"week{n:02d}": (START + timedelta(weeks=n)).isoformat() for n in range(1, 15)}
    students = [{"login": f"s{i:03d}", "name": f"Студент {i:03d}", "group": f"ИИ-{201 + i // 25}"}
                for i in range(300)]
    attempts = []
    for s in students:
        for n, task in enumerate(tasks, 1):
            deadline = START + timedelta(weeks=n)
            for _ in range(50):
                shift = timedelta(minutes=rnd.randint(1, 4000))
                when = deadline + shift if rnd.random() < 0.2 else deadline - shift
                attempts.append({"login": s["login"], "task": task, "score": rnd.randint(0, 10),
                                 "submitted": when.isoformat()})
    rnd.shuffle(attempts)
    extensions = [{"login": f"s{i:03d}", "task": "week03", "until": (START + timedelta(weeks=4)).isoformat()}
                  for i in range(0, 300, 10)]
    return {"tasks": tasks, "students": students, "attempts": attempts, "extensions": extensions}


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(make(), f, ensure_ascii=False)
