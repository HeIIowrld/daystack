"""
Sample data helpers shared between the CLI app and API layer.
Includes locations so routing logic can demonstrate travel-aware packing.
"""

from __future__ import annotations

from typing import Dict, List

try:
    from daystack import get_crawler_tasks, get_schedule
except Exception:
    get_crawler_tasks = None
    get_schedule = None

from .location_utils import ensure_coordinates

FALLBACK_SCHEDULE: List[Dict[str, str]] = [
    {
        "name": "오전 수업",
        "start_time": "09:00",
        "end_time": "12:00",
        "location": "강남역",
    },
    {
        "name": "점심",
        "start_time": "12:30",
        "end_time": "13:30",
        "location": "강남역",
    },
    {
        "name": "아르바이트",
        "start_time": "16:00",
        "end_time": "20:00",
        "location": "판교역",
    },
]

FALLBACK_TASKS: List[Dict] = [
    {"task": "온라인 강의 듣기", "estimated_time": 40, "location": "강남역"},
    {"task": "영어 과제", "estimated_time": 30, "location": "성수"},
    {"task": "독서", "estimated_time": 45, "location": "뚝섬"},
]


def get_sample_schedule() -> List[Dict[str, str]]:
    """Return a canned schedule used for demos and tests."""
    raw_schedule = None
    if callable(get_schedule):
        try:
            raw_schedule = get_schedule()
        except Exception:
            raw_schedule = None

    if not raw_schedule:
        raw_schedule = FALLBACK_SCHEDULE

    return ensure_coordinates(raw_schedule)


def get_sample_todos() -> List[Dict]:
    """Return demo todo items sourced from the shared DAYSTACK logic."""
    if callable(get_crawler_tasks):
        try:
            tasks = get_crawler_tasks()
        except Exception:
            tasks = None
        if tasks:
            return tasks
    return FALLBACK_TASKS.copy()
