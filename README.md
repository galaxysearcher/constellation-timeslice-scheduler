# Constellation Time-Slice Scheduler

Toy scheduler for constellation downlink and inter-satellite resource allocation.

The repository models one short scheduling slice. Each traffic flow chooses one candidate path from a source spacecraft to a ground node while respecting link capacity, downlink capacity, terminal concurrency, and coarse energy-margin constraints.

```text
traffic flows → candidate paths → feasible schedule → latency and resource diagnostics
```

## What this project does

- Builds a small two-ring constellation graph.
- Enumerates candidate routes from source spacecraft to downlink nodes.
- Selects one route per traffic flow using an exact baseline solver.
- Evaluates link capacity, downlink capacity, terminal concurrency, energy margin, and latency.
- Provides an optional QAOA-style diagonal sweep for local simulator experiments.
- Writes structured JSON outputs for repeatable inspection.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python scripts/run_exact.py
```

The run writes:

```text
results/exact_solution.json
```

## Run tests

```bash
python -m pytest
```

## Optional Qiskit run

```bash
pip install -e ".[qiskit]"
python scripts/run_qiskit_sweep.py --grid 7 --shots 1024
```

## Repository structure

```text
src/constellation_timeslice_scheduler/
  instance.py       # toy constellation instance generator
  solve.py          # exact schedule search
  evaluate.py       # feasibility and latency diagnostics
  qiskit_optional.py # optional diagonal-ansatz sweep

scripts/
  run_exact.py
  run_qiskit_sweep.py

docs/
  methodology.md
  validation_plan.md

examples/
  timeslice0_instance.json
```

## Output fields

The result JSON includes:

- selected path for each flow
- total latency
- objective value
- capacity feasibility
- terminal feasibility
- downlink feasibility
- minimum energy margin
- edge and terminal usage diagnostics

## Research workflow

This project turns a short-horizon constellation routing problem into an explicit resource-allocation workflow. The core pattern is: define the graph, generate candidate paths, score feasibility, select a schedule, and record diagnostics.
