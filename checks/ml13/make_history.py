"""История прошлого семестра для модели риска — синтетическая, с настоящей зависимостью.

Строка — студент и задание: признаки первых суток после выдачи задания и итог.
    first_score    — балл первой попытки (0..10)
    attempts_day1  — сколько попыток в первые сутки
    hours_before   — за сколько часов до срока сдана первая попытка (меньше 0 — после срока)
    prev_best      — лучший балл за предыдущее задание
    at_risk        — 1, если итоговый лучший балл оказался меньше 6

    uv run python checks/ml13/make_history.py checks/ml13
"""

import csv
import math
import random
import sys
from pathlib import Path

FIELDS = ["first_score", "attempts_day1", "hours_before", "prev_best", "at_risk"]


def rows(n, seed):
    rnd = random.Random(seed)
    for _ in range(n):
        prev_best = min(10, max(0, round(rnd.gauss(6.5, 2.5), 1)))
        first_score = min(10, max(0, round(prev_best * 0.6 + rnd.uniform(-2, 5), 1)))
        attempts = min(8, max(0, int(rnd.expovariate(0.6))))
        hours = round(rnd.uniform(-48, 168), 1)
        logit = 4.2 - 0.45 * first_score - 0.35 * prev_best - 0.012 * hours + 0.15 * attempts
        risk = 1 / (1 + math.exp(-logit))
        yield [first_score, attempts, hours, prev_best, int(rnd.random() < risk)]


def write(path, n, seed):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows(n, seed))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    write(out / "train.csv", 800, 2025)
    write(out / "test.csv", 400, 2026)
