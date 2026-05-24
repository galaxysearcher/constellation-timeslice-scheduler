"""
Demo constellation instance generator.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path


def _ring_positions(radius: float, n: int, phase: float = 0.0):
    return [
        (radius * math.cos(2 * math.pi * i / n + phase),
         radius * math.sin(2 * math.pi * i / n + phase))
        for i in range(n)
    ]


def _distance(positions: dict, u: int, v: int) -> float:
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    return math.hypot(x2 - x1, y2 - y1)


def _enumerate_paths(src: int, downlink_nodes: list[int], adjacency: dict, max_hops: int = 5, top_k: int = 5):
    candidates = []
    stack = [(src, [src], 0.0)]

    while stack:
        node, path, latency = stack.pop()
        if len(path) > max_hops:
            continue

        if node in downlink_nodes:
            candidates.append({
                "path": path + [100],
                "latency": latency + 8.0,
                "downlink_node": node,
                "edges": [tuple(sorted((path[i], path[i + 1]))) for i in range(len(path) - 1)],
            })

        for nbr, edge_latency in adjacency[node]:
            if nbr in path:
                continue
            stack.append((nbr, path + [nbr], latency + edge_latency))

    candidates.sort(key=lambda row: row["latency"])
    return candidates[:top_k]


def build_demo_instance() -> dict:
    """
    Build a small deterministic constellation scheduling instance.

    Node 100 represents the ground node. Spacecraft nodes are integers 0 through 11.
    """
    n_ring = 6
    ring_a = list(range(0, n_ring))
    ring_b = list(range(n_ring, 2 * n_ring))
    all_spacecraft = ring_a + ring_b

    positions = {i: xy for i, xy in zip(ring_a, _ring_positions(1.0, n_ring))}
    positions.update({i: xy for i, xy in zip(ring_b, _ring_positions(1.6, n_ring, phase=math.pi / n_ring))})
    positions[100] = (0.0, 0.0)

    edge_capacity = 2
    edges = {}
    adjacency = defaultdict(list)

    def add_edge(u: int, v: int):
        latency = 5.0 * _distance(positions, u, v)
        key = f"{min(u, v)}-{max(u, v)}"
        edges[key] = {"u": min(u, v), "v": max(u, v), "capacity": edge_capacity, "latency": latency}
        adjacency[u].append((v, latency))
        adjacency[v].append((u, latency))

    for ring in (ring_a, ring_b):
        for i in range(n_ring):
            add_edge(ring[i], ring[(i + 1) % n_ring])

    for i in range(n_ring):
        add_edge(ring_a[i], ring_b[i])

    downlink_nodes = [1, 3, 7, 10]
    flows = [
        {"id": "flow_a", "source": 0, "weight": 1.0},
        {"id": "flow_b", "source": 5, "weight": 1.0},
        {"id": "flow_c", "source": 6, "weight": 1.2},
        {"id": "flow_d", "source": 11, "weight": 0.8},
    ]

    paths = {}
    for flow in flows:
        paths[flow["id"]] = _enumerate_paths(flow["source"], downlink_nodes, adjacency, max_hops=5, top_k=5)

    energy_soc = {str(node): 70.0 + 2.5 * (node % 7) for node in all_spacecraft}
    solar_charge = {str(node): 2.5 if node % 4 in (0, 1) else 0.2 for node in all_spacecraft}

    instance = {
        "slot": 0,
        "nodes": all_spacecraft,
        "ground_node": 100,
        "flows": flows,
        "paths": paths,
        "edges": edges,
        "downlink_nodes": downlink_nodes,
        "downlink_capacity": 2,
        "terminal_limit": 4,
        "energy": {
            "soc": energy_soc,
            "solar_charge": solar_charge,
            "minimum_margin": 20.0,
            "per_hop_cost": 3.0,
            "downlink_cost": 4.0,
        },
        "objective_weights": {
            "latency": 1.0,
            "capacity_penalty": 1000.0,
            "downlink_penalty": 1000.0,
            "terminal_penalty": 1000.0,
            "energy_penalty": 1000.0,
        },
    }
    return instance


def write_demo_instance(path: str | Path) -> None:
    payload = build_demo_instance()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
