# Methodology

## Objective

Model a short constellation scheduling slice as a constrained route-selection problem.

Each traffic flow must choose one candidate path from a source spacecraft to a ground node. A schedule is evaluated by latency, link capacity, downlink capacity, terminal concurrency, and energy margin.

## Graph model

The demo instance uses a two-ring constellation with 12 spacecraft and one ground node. Each flow has five candidate paths. The graph is deterministic so the exact solver and tests produce repeatable outputs.

## Feasibility checks

The evaluator tracks:

- link usage against per-link capacity
- downlink-node usage against downlink capacity
- spacecraft terminal usage against a concurrency limit
- minimum energy margin after communication activity
- weighted total latency

## Exact baseline

The exact solver enumerates all candidate-path combinations. For four flows with five candidate paths each, this is a 625-schedule search. That makes the result easy to inspect and provides a baseline for optional heuristic or QAOA-style methods.

## Optional Qiskit sweep

The optional Qiskit path maps the objective table onto a diagonal phase operator and performs a small gamma / beta sweep on a local simulator. The exact enumeration result remains the reference solution for this compact instance.
