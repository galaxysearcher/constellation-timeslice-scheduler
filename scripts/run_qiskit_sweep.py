from __future__ import annotations

import argparse
import json
from pathlib import Path

from constellation_timeslice_scheduler import build_demo_instance
from constellation_timeslice_scheduler.qiskit_optional import run_qiskit_sweep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", type=int, default=7)
    parser.add_argument("--shots", type=int, default=1024)
    args = parser.parse_args()

    instance = build_demo_instance()
    result = run_qiskit_sweep(instance, grid=args.grid, shots=args.shots)

    Path("results").mkdir(exist_ok=True)
    Path("results/qiskit_sweep.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
