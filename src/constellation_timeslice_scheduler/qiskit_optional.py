"""
Optional Qiskit diagonal-ansatz sweep for the scheduling instance.

The exact enumeration solver is the default baseline. This optional module converts
the exact objective table into a diagonal phase operator for small local experiments.
"""
from __future__ import annotations

import math
from itertools import product
from typing import Dict

import numpy as np

from .evaluate import evaluate_schedule


def _index_to_selection(instance: dict, flat_index: int) -> dict:
    flow_ids = [flow["id"] for flow in instance["flows"]]
    radices = [len(instance["paths"][fid]) for fid in flow_ids]
    digits = []
    n = flat_index
    for base in reversed(radices):
        digits.append(n % base)
        n //= base
    digits = list(reversed(digits))
    return {fid: int(digit) for fid, digit in zip(flow_ids, digits)}


def _objective_vector(instance: dict) -> np.ndarray:
    flow_ids = [flow["id"] for flow in instance["flows"]]
    radices = [len(instance["paths"][fid]) for fid in flow_ids]
    n_states = int(np.prod(radices))
    values = np.zeros(n_states, dtype=float)
    for idx in range(n_states):
        selection = _index_to_selection(instance, idx)
        values[idx] = evaluate_schedule(instance, selection)["objective"]
    return values


def run_qiskit_sweep(instance: dict, grid: int = 7, shots: int = 1024) -> Dict:
    """Run a small local Qiskit diagonal sweep over the schedule objective table."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import Diagonal
        from qiskit_aer.primitives import Sampler
    except Exception as exc:
        raise RuntimeError("Qiskit optional dependencies are not installed") from exc

    objective = _objective_vector(instance)
    n_qubits = math.ceil(math.log2(len(objective)))
    padded = np.full(2 ** n_qubits, objective.max() + 1e3)
    padded[: len(objective)] = objective

    gammas = np.linspace(0.0, 2 * math.pi, grid)
    betas = np.linspace(0.0, math.pi, grid)
    sampler = Sampler()
    best = {"expected_objective": float("inf"), "gamma": None, "beta": None, "counts": None}

    phases_base = padded - padded.min()
    for gamma in gammas:
        phases = np.exp(-1j * gamma * phases_base)
        for beta in betas:
            qc = QuantumCircuit(n_qubits)
            qc.h(range(n_qubits))
            qc.append(Diagonal(phases), range(n_qubits))
            for q in range(n_qubits):
                qc.rx(2 * beta, q)
            qc.measure_all()

            result = sampler.run([qc], shots=shots).result()
            dist = result.quasi_dists[0]
            counts = {format(k, f"0{n_qubits}b"): int(v * shots) for k, v in dist.items()}

            total = max(1, sum(counts.values()))
            expected = 0.0
            for bitstring, count in counts.items():
                idx = int(bitstring, 2)
                expected += (count / total) * float(padded[idx])

            if expected < best["expected_objective"]:
                best = {
                    "expected_objective": float(expected),
                    "gamma": float(gamma),
                    "beta": float(beta),
                    "counts": counts,
                }

    return {
        "method": "qiskit_diagonal_sweep",
        "grid": grid,
        "shots": shots,
        "n_qubits": n_qubits,
        "best": best,
    }
