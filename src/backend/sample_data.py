"""
Sample data helpers shared between the CLI app and API layer.
Includes locations so routing logic can demonstrate travel-aware packing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path to import daystack
# IMPORTANT: Must be at the beginning so root config.py is found before src/backend/config.py
project_root = Path(__file__).parent.parent.parent
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)
elif sys.path.index(project_root_str) > 0:
    # Move to front if already in path but not first
    sys.path.remove(project_root_str)
    sys.path.insert(0, project_root_str)

# Ensure .env file is loaded from project root
# This is important because daystack imports config which needs the .env file
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")
else:
    # Try loading from current directory as fallback
    load_dotenv()
    print(f"⚠️  .env not found at {env_path}, trying current directory")

# Temporarily remove backend from path to ensure root config is imported
backend_path = str(Path(__file__).parent)
backend_was_in_path = backend_path in sys.path
if backend_was_in_path:
    sys.path.remove(backend_path)

try:
    # Import daystack - it will import root config.py because project_root is first in path
    from daystack import get_crawler_tasks, get_schedule
    print(f"✅ Successfully imported daystack functions: get_crawler_tasks={callable(get_crawler_tasks)}, get_schedule={callable(get_schedule)}")
except Exception as e:
    # If import fails, set to None and use fallback data
    import traceback
    print(f"⚠️  Failed to import daystack: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    get_crawler_tasks = None
    get_schedule = None
finally:
    # Restore backend path if it was there
    if backend_was_in_path and backend_path not in sys.path:
        sys.path.append(backend_path)

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
            print("📅 Attempting to fetch schedule from daystack...")
            raw_schedule = get_schedule()
            print(f"✅ Got schedule from daystack: {len(raw_schedule) if raw_schedule else 0} items")
        except Exception as e:
            print(f"⚠️  Error fetching schedule from daystack: {e}")
            raw_schedule = None

    if not raw_schedule:
        print("📅 Using fallback schedule")
        raw_schedule = FALLBACK_SCHEDULE

    return ensure_coordinates(raw_schedule)


def get_sample_todos() -> List[Dict]:
    """Return demo todo items sourced from the shared DAYSTACK logic."""
    if callable(get_crawler_tasks):
        try:
            print("🕸️  Attempting to fetch tasks from crawler...")
            tasks = get_crawler_tasks()
            print(f"📥 Crawler returned {len(tasks) if tasks else 0} tasks")
            # Only return tasks if we got actual data (non-empty list)
            if tasks and len(tasks) > 0:
                print(f"✅ Using {len(tasks)} tasks from crawler")
                return tasks
            else:
                print("⚠️  Crawler returned empty list, using fallback data")
        except Exception as e:
            # Log the error for debugging, but continue to fallback
            import traceback
            print(f"❌ Error fetching crawler tasks: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            tasks = None
    else:
        print("⚠️  get_crawler_tasks is not callable, using fallback data")
    return FALLBACK_TASKS.copy()
