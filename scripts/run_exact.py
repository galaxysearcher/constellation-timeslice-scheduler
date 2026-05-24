from __future__ import annotations

import json
from pathlib import Path

from constellation_timeslice_scheduler import build_demo_instance, exact_schedule


def main() -> int:
    instance = build_demo_instance()
    Path("examples").mkdir(exist_ok=True)
    Path("examples/timeslice0_instance.json").write_text(json.dumps(instance, indent=2), encoding="utf-8")

    solution = exact_schedule(instance)
    Path("results").mkdir(exist_ok=True)
    Path("results/exact_solution.json").write_text(json.dumps(solution, indent=2), encoding="utf-8")

    print(json.dumps({
        "method": solution["method"],
        "objective": solution["best_evaluation"]["objective"],
        "total_latency": solution["best_evaluation"]["total_latency"],
        "feasible": solution["best_evaluation"]["feasible"],
        "min_energy_margin": solution["best_evaluation"]["min_energy_margin"],
        "best_selection": solution["best_selection"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
