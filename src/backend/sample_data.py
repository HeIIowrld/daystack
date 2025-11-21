"""
Sample data helpers shared between the CLI app and API layer.
"""

from __future__ import annotations

from typing import Dict, List


def get_sample_schedule() -> List[Dict[str, str]]:
    """Return a canned schedule used for demos and tests."""
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
            "name": "아르바이트",
            "start_time": "16:00",
            "end_time": "20:00",
            "location": "판교역",
        },
    ]


def get_sample_todos() -> List[Dict[str, int]]:
    """Return demo todo items."""
    return [
        {"task": "온라인 강의 듣기", "estimated_time": 40},
        {"task": "영어 과제", "estimated_time": 30},
        {"task": "독서", "estimated_time": 45},
    ]
