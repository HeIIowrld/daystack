"""
Sample data helpers shared between the CLI app and API layer.
Includes locations so routing logic can demonstrate travel-aware packing.
"""

from __future__ import annotations

from typing import Dict, List

from daystack import get_crawler_tasks, get_schedule

from backend.location_utils import ensure_coordinates

FALLBACK_TASKS = [
    {"task": "온라인 강의 듣기", "estimated_time": 40},
    {"task": "영어 과제", "estimated_time": 30},
    {"task": "독서", "estimated_time": 45},
]


def get_sample_schedule() -> List[Dict[str, str]]:
    """Return a canned schedule used for demos and tests."""
<<<<<<< HEAD
    return ensure_coordinates(get_schedule())


def get_sample_todos() -> List[Dict]:
    """Return demo todo items sourced from the shared DAYSTACK logic."""
    tasks = get_crawler_tasks()
    return tasks if tasks else FALLBACK_TASKS.copy()
=======
    return [
        {
            "name": "오전 수업",
            "start_time": "09:00",
            "end_time": "12:00",
            "location": "강남역",
        },
        {
            "name": "점심 약속",
            "start_time": "12:30",
            "end_time": "13:30",
            "location": "강남역",
        },
        {
            "name": "알바",
            "start_time": "16:00",
            "end_time": "20:00",
            "location": "한양대",
        },
    ]


def get_sample_todos() -> List[Dict[str, int]]:
    """Return demo todo items."""
    return [
        {"task": "자바 강의 듣기", "estimated_time": 40, "location": "강남역"},
        {"task": "영어 과제", "estimated_time": 30, "location": "성수"},
        {"task": "독서", "estimated_time": 45, "location": "뚝섬"},
    ]
>>>>>>> 5a1bfb6 (scheduling algorithm)
