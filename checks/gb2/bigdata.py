"""Ведомость размером с колледж: 300 студентов, 14 заданий, по 50 попыток на студента и задание."""

import random
from datetime import datetime, timedelta

START = datetime(2026, 9, 1, 9, 0)


def make(seed=14):
    rnd = random.Random(seed)
    tasks = [f"week{n:02d}" for n in range(1, 15)]
    deadlines = {t: START + timedelta(weeks=i + 1) for i, t in enumerate(tasks)}
    students = [(f"s{i:03d}", f"Студент {i:03d}", f"ИИ-{201 + i // 25}") for i in range(300)]
    attempts = []
    for login, _, _ in students:
        for t in tasks:
            for _ in range(50):
                late = rnd.random() < 0.2
                shift = timedelta(hours=rnd.randint(1, 72))
                when = deadlines[t] + shift if late else deadlines[t] - shift
                attempts.append((login, t, rnd.randint(0, 10), when))
    rnd.shuffle(attempts)
    extensions = {(f"s{i:03d}", "week03"): deadlines["week03"] + timedelta(days=7) for i in range(0, 300, 10)}
    return attempts, students, tasks, deadlines, extensions
