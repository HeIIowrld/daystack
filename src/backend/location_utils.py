"""
Helpers for handling geographic coordinates.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .geocoding import get_location_coords

KNOWN_COORDINATES: Dict[str, Dict[str, float]] = {
    "강남역": {"lat": 37.497952, "lng": 127.027926},
    "서울특별시 강남구": {"lat": 37.517236, "lng": 127.047325},
    "분당구 불정로 6": {"lat": 37.394953, "lng": 127.11167},
    "판교역": {"lat": 37.394768, "lng": 127.111217},
}

_coord_cache: Dict[str, Dict[str, float]] = {k: v.copy() for k, v in KNOWN_COORDINATES.items()}


def _coord_dict(raw: str | None) -> Optional[Dict[str, float]]:
    if not raw:
        return None
    try:
        lng_str, lat_str = raw.split(",", 1)
        return {"lat": float(lat_str), "lng": float(lng_str)}
    except (ValueError, AttributeError):
        return None


def ensure_coordinates(entries: List[Dict]) -> List[Dict]:
    """Return a new list where each item has coordinates if a location is known."""
    enriched: List[Dict] = []

    for entry in entries:
        data = dict(entry)
        if data.get("coordinates"):
            enriched.append(data)
            continue

        location = data.get("location")
        if not location:
            enriched.append(data)
            continue

        normalized_location = location.strip()
        coords = _coord_cache.get(normalized_location)
        if not coords:
            coords = KNOWN_COORDINATES.get(normalized_location)
        if not coords:
            coords = _coord_dict(get_location_coords(normalized_location))
            if coords:
                _coord_cache[normalized_location] = coords

        if coords:
            data["coordinates"] = coords

        enriched.append(data)

    return enriched
