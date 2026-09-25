"""PRG-13: progon chart — график по заданиям для учебной части."""

import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "checks" / "cmd3" / "course.json"


def test_plot_tasks(tmp_path):
    from progon.analytics import plot_tasks
    from progon.model import Course

    fig = plot_tasks(Course.from_json(COURSE), tmp_path / "tasks.png")
    assert (tmp_path / "tasks.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    ax = fig.axes[0]
    assert ax.get_title() == "Средний лучший балл по заданиям"
    assert [t.get_text() for t in ax.get_xticklabels()] == ["week01", "week02", "week03"]
    assert [round(p.get_height(), 2) for p in ax.patches] == [7.5, 6.25, 8.0]


def test_chart_command(tmp_path):
    out = tmp_path / "chart.png"
    r = subprocess.run([sys.executable, "-m", "progon", "chart", str(COURSE), "--out", str(out)],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    assert out.stat().st_size > 5000 and r.stdout == ""
