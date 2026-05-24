"""
Schedule evaluation and feasibility diagnostics.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Tuple


def _edge_key(edge: Tuple[int, int]) -> str:
    return f"{min(edge)}-{max(edge)}"


def evaluate_schedule(instance: dict, selection: Dict[str, int]) -> dict:
    """Evaluate a selected candidate-path index for every flow."""
    edge_usage = Counter()
    downlink_usage = Counter()
    terminal_usage = Counter()
    total_latency = 0.0
    selected = {}
    energy_draw = defaultdict(float)

    flow_by_id = {flow["id"]: flow for flow in instance["flows"]}

    for flow_id, path_idx in selection.items():
        flow = flow_by_id[flow_id]
        cand = instance["paths"][flow_id][path_idx]
        weight = float(flow["weight"])
        total_latency += weight * float(cand["latency"])

        for edge in cand["edges"]:
            key = _edge_key(tuple(edge))
            edge_usage[key] += 1

        downlink_usage[int(cand["downlink_node"])] += 1

        route_nodes = [node for node in cand["path"] if node != instance["ground_node"]]
        for node in route_nodes:
            terminal_usage[int(node)] += 1

        for i in range(len(route_nodes) - 1):
            energy_draw[str(route_nodes[i])] += instance["energy"]["per_hop_cost"]
        energy_draw[str(cand["downlink_node"])] += instance["energy"]["downlink_cost"]

        selected[flow_id] = {
            "path_index": path_idx,
            "path": cand["path"],
            "latency": cand["latency"],
            "downlink_node": cand["downlink_node"],
        }

    edge_violations = []
    for key, count in edge_usage.items():
        cap = instance["edges"][key]["capacity"]
        if count > cap:
            edge_violations.append({"edge": key, "usage": count, "capacity": cap})

    downlink_violations = [
        {"downlink_node": node, "usage": count, "capacity": instance["downlink_capacity"]}
        for node, count in downlink_usage.items()
        if count > instance["downlink_capacity"]
    ]

    terminal_violations = [
        {"node": node, "usage": count, "limit": instance["terminal_limit"]}
        for node, count in terminal_usage.items()
        if count > instance["terminal_limit"]
    ]

    energy_margins = {}
    for node in instance["nodes"]:
        key = str(node)
        margin = (
            float(instance["energy"]["soc"][key])
            + float(instance["energy"]["solar_charge"][key])
            - float(energy_draw.get(key, 0.0))
            - float(instance["energy"]["minimum_margin"])
        )
        energy_margins[key] = margin

    min_energy_margin = min(energy_margins.values())
    energy_ok = min_energy_margin >= 0.0

    weights = instance["objective_weights"]
    objective = total_latency
    objective += weights["capacity_penalty"] * len(edge_violations)
    objective += weights["downlink_penalty"] * len(downlink_violations)
    objective += weights["terminal_penalty"] * len(terminal_violations)
    objective += weights["energy_penalty"] * (0.0 if energy_ok else abs(min_energy_margin))

    return {
        "selected": selected,
        "total_latency": total_latency,
        "objective": objective,
        "feasible": not edge_violations and not downlink_violations and not terminal_violations and energy_ok,
        "edge_usage": dict(edge_usage),
        "downlink_usage": {str(k): v for k, v in downlink_usage.items()},
        "terminal_usage": {str(k): v for k, v in terminal_usage.items()},
        "edge_violations": edge_violations,
        "downlink_violations": downlink_violations,
        "terminal_violations": terminal_violations,
        "min_energy_margin": min_energy_margin,
    }
