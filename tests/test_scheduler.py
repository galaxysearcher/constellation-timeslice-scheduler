import json
import subprocess
import sys
from pathlib import Path

from constellation_timeslice_scheduler import build_demo_instance, exact_schedule


def test_demo_instance_structure():
    inst = build_demo_instance()
    assert len(inst["nodes"]) == 12
    assert inst["ground_node"] == 100
    assert len(inst["flows"]) == 4
    for flow in inst["flows"]:
        assert len(inst["paths"][flow["id"]]) == 5


def test_exact_schedule_is_feasible():
    inst = build_demo_instance()
    solution = exact_schedule(inst)
    assert solution["method"] == "exact_enumeration"
    assert solution["best_evaluation"]["feasible"] is True
    assert solution["best_evaluation"]["total_latency"] > 0


def test_run_exact_script():
    result = subprocess.run(
        [sys.executable, "scripts/run_exact.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert "exact_enumeration" in result.stdout
    assert Path("results/exact_solution.json").exists()
    payload = json.loads(Path("results/exact_solution.json").read_text(encoding="utf-8"))
    assert payload["best_evaluation"]["feasible"] is True
