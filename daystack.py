"""
DAYSTACK - To-do list Tetris
Optimizing your daily tasks with travel time consideration
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from crawler import LMSCrawler
from scheduler import allocate_tasks, print_schedule
from config import YONSEI_USERNAME, YONSEI_PASSWORD

DEFAULT_TASK_DURATION = 60


def get_schedule() -> List[Dict]:
    """Return today's sample schedule."""
    return [
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


def manual_input_tasks() -> List[Dict]:
    """Collect tasks from the CLI user."""
    print("\n📝 Enter tasks (empty line to finish):\n")
    tasks: List[Dict] = []
    
    while True:
        name = input("Task name: ").strip()
        if not name:
            break

        try:
            duration = int(input("Duration (minutes): ").strip())
            tasks.append({"task": name, "estimated_time": duration})
            print("✓ Added\n")
        except ValueError:
            print("✗ Invalid duration\n")
            continue

        tasks.append({"task": name, "estimated_time": duration})
        print("✓ Added\n")

    return tasks


def convert_lms_tasks(lms_tasks: List[Dict]) -> List[Dict]:
    """
    Convert LMS crawler output to Scheduler format.
    Scheduler expects: 'task' and 'estimated_time'
    """
    formatted_tasks = []
    print(f"\n📥 Converting {len(lms_tasks)} LMS tasks...")
    
    for t in lms_tasks:
        # Combine Course and Task Name for clarity
        full_name = f"[{t['course']}] {t['task']}"
        
        # Heuristic: Default to 60 mins for assignments, can be adjusted
        default_duration = 60 
        
        formatted_tasks.append({
            "task": full_name,
            "estimated_time": default_duration,
            "course": t.get('course', ''),
        })
    return formatted_tasks


def get_crawler_tasks(username: str | None = None, password: str | None = None) -> List[Dict]:
    """Fetch and convert tasks from the LMS crawler."""
    username = username or YONSEI_USERNAME
    password = password or YONSEI_PASSWORD

    if not username or not password:
        print("⚠️  Missing LMS credentials. Set YONSEI_USERNAME and YONSEI_PASSWORD.")
        return []

    crawler = LMSCrawler(username, password)
    if not crawler.login():
        print("❌ Login failed. Please check your credentials.")
        return []

    raw_tasks = crawler.fetch_tasks()
    if not raw_tasks:
        print("⚠️  Login successful, but no incomplete tasks found.")
        return []

    return convert_lms_tasks(raw_tasks)


def get_daystack_data(source: str = "crawler") -> Tuple[List[Dict], List[Dict]]:
    """Shared helper for CLI/API to retrieve schedule and tasks."""
    schedule = get_schedule()

    if source == "crawler":
        tasks = get_crawler_tasks()
    elif source == "manual":
        tasks = manual_input_tasks()
    else:
        raise ValueError("Unknown task source: expected 'crawler' or 'manual'")

    return schedule, tasks


def main():
    print("\n" + "=" * 60)
    print("  DAYSTACK - To-do List Tetris")
    print("=" * 60)

    print("\nHow to get tasks?")
    print("  1. Fetch from LMS (requires credentials)")
    print("  2. Manual input")

    choice = input("\nChoice (1/2): ").strip()
    source = "crawler" if choice == "1" else "manual"

    schedule, tasks = get_daystack_data(source)

    if not tasks:
        print("⚠️  No tasks to schedule")
        return
    
    # Get schedule
    schedule = get_schedule()
    
    print("\n📅 Today's Schedule:")
    for event in schedule:
        start = event.get("start_time", "")
        end = event.get("end_time", "")
        print(f"  {start}-{end}: {event['name']} @ {event['location']}")
    
    print("\n📚 Tasks:")
    for task in tasks:
        course = f" ({task['course']})" if task.get("course") else ""
        print(f"  - {task['task']}{course} / {task['estimated_time']}분")
    
    # Optimize
    print("\n🔄 Optimizing...")
    optimized = allocate_tasks(schedule, tasks)
    print_schedule(optimized)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
