"""Selected pure routing primitives from Homegrown Cannalytics.

Copyright (c) 2026 Homegrown Cannalytics. All rights reserved.
Selected portfolio excerpt. See LICENSE and docs/PROVENANCE.md.
"""

from __future__ import annotations

import math
from typing import Any

EARTH_RADIUS_METERS = 6_371_008.8


def haversine_meters(first: dict[str, Any], second: dict[str, Any]) -> float:
    lat1 = math.radians(first["latitude"])
    lat2 = math.radians(second["latitude"])
    delta_lat = lat2 - lat1
    delta_lon = math.radians(second["longitude"] - first["longitude"])
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(value))


def _distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    return haversine_meters(first["coordinates"], second["coordinates"])


def _route_cost(
    route: list[dict[str, Any]],
    cost: Any,
) -> float:
    return sum(
        cost(route[index], route[(index + 1) % len(route)])
        for index in range(len(route))
    )


def _nearest_neighbor(
    origin: dict[str, Any],
    candidates: list[dict[str, Any]],
    cost: Any,
) -> list[dict[str, Any]]:
    remaining = sorted(candidates, key=lambda item: item["location_id"])
    route = [origin]
    while remaining:
        current = route[-1]
        next_stop = min(
            remaining,
            key=lambda item: (cost(current, item), item["location_id"]),
        )
        route.append(next_stop)
        remaining.remove(next_stop)
    return route


def _two_opt(route: list[dict[str, Any]], cost: Any) -> list[dict[str, Any]]:
    best = route
    best_distance = _route_cost(best, cost)
    improved = True
    while improved:
        improved = False
        for start in range(1, len(best) - 1):
            for end in range(start + 1, len(best)):
                candidate = best[:start] + list(reversed(best[start : end + 1])) + best[end + 1 :]
                candidate_distance = _route_cost(candidate, cost)
                if candidate_distance + 0.001 < best_distance:
                    best = candidate
                    best_distance = candidate_distance
                    improved = True
                    break
            if improved:
                break
    return best


