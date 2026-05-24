"""
Exact baseline solver for small scheduling instances.
"""
from __future__ import annotations

from itertools import product

from .evaluate import evaluate_schedule


def exact_schedule(instance: dict, top_k: int = 5) -> dict:
    """Search all route-index combinations and return the best schedule."""
    flow_ids = [flow["id"] for flow in instance["flows"]]
    index_ranges = [range(len(instance["paths"][flow_id])) for flow_id in flow_ids]

    evaluated = []
    for combo in product(*index_ranges):
        selection = {flow_id: int(idx) for flow_id, idx in zip(flow_ids, combo)}
        result = evaluate_schedule(instance, selection)
        evaluated.append({"selection": selection, "evaluation": result})

    evaluated.sort(key=lambda row: (not row["evaluation"]["feasible"], row["evaluation"]["objective"]))
    best = evaluated[0]

    return {
        "slot": instance["slot"],
        "method": "exact_enumeration",
        "best_selection": best["selection"],
        "best_evaluation": best["evaluation"],
        "top_candidates": evaluated[:top_k],
    }
