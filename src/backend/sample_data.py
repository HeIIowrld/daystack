"""
Sample data helpers shared between the CLI app and API layer.
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
    return ensure_coordinates(get_schedule())


def get_sample_todos() -> List[Dict]:
    """Return demo todo items sourced from the shared DAYSTACK logic."""
    tasks = get_crawler_tasks()
    return tasks if tasks else FALLBACK_TASKS.copy()
