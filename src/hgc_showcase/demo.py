"""Run a generic, synthetic-node demonstration with no external services."""
from __future__ import annotations
import json
from .routing_core import _nearest_neighbor, _route_cost, _two_opt

def nodes() -> list[dict]:
    # Fabricated unitless points. These are not retailer or real-world coordinates.
    points = [(85, 88), (89, 76), (65, 45), (16, 15), (44, 57), (80, 90), (90, 83), (45, 84)]
    return [{"location_id": chr(65 + i), "x": x, "y": y} for i, (x, y) in enumerate(points)]

def distance(a: dict, b: dict) -> float:
    return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5

def run() -> dict:
    points = nodes()
    nearest = _nearest_neighbor(points[0], points[1:], distance)
    improved = _two_opt(nearest, distance)
    return {
        "input": "fabricated unitless nodes; no real locations",
        "algorithm": "nearest-neighbor then 2-opt; heuristic, not an optimality proof",
        "nearest_order": [p["location_id"] for p in nearest],
        "improved_order": [p["location_id"] for p in improved],
        "nearest_cost": round(_route_cost(nearest, distance), 3),
        "improved_cost": round(_route_cost(improved, distance), 3),
        "returns_to": "A",
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

