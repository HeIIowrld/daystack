"""
DAYSTACK - To-do list Tetris
Optimizing your daily tasks with travel time consideration
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from crawler import LMSCrawler
from scheduler import allocate_tasks, print_schedule
from config import YONSEI_USERNAME, YONSEI_PASSWORD

DEFAULT_TASK_DURATION = 60

FALLBACK_SCHEDULE = [
    {
        "name": "오전 수업",
        "start_time": "09:00",
        "end_time": "12:00",
        "location": "연세로 50",
    },
    {
        "name": "점심",
        "start_time": "12:30",
        "end_time": "13:30",
        "location": "서울특별시 마포구 양화로 160",
    },
    {
        "name": "아르바이트",
        "start_time": "16:00",
        "end_time": "20:00",
        "location": "경기도 성남시 분당구 판교역로 160",
    },
]


def get_schedule(use_lms: bool = True) -> List[Dict]:
    """Return today's schedule using real LMS due dates when possible."""
    if use_lms:
        raw_tasks = fetch_raw_lms_tasks()
        schedule = build_schedule_from_lms(raw_tasks)
        if schedule:
            return schedule
    return FALLBACK_SCHEDULE.copy()


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

    return tasks

def parse_course_id(course_name):
    """
    Parse course ID from course name (format: AAA0000.00-00)
    Returns 3-letter college code (e.g., 'CSE' from 'CSE1234.01-01')
    """
    import re
    # Pattern: 3 letters, 4 digits, dot, 2 digits, dash, 2 digits
    pattern = r'^([A-Z]{3})\d{4}\.\d{2}-\d{2}'
    match = re.match(pattern, course_name)
    if match:
        return match.group(1)
    return None


def get_college_location(college_code):
    """
    Map college code to building location.
    If not found, return default location.
    """
    # College code to building location mapping
    '''
    college_locations = {
        
        "KOR": "연세대학교 위당관",
        "CHI": "연세대학교 위당관",
        "CHN": "연세대학교 위당관",
        "ENG": "연세대학교 위당관",
        "GER": "연세대학교 위당관",
        "FRA": "연세대학교 위당관",
        "RUS": "연세대학교 위당관",
        "HIS": "연세대학교 위당관",
        "PHI": "연세대학교 위당관",
        "LLI": "연세대학교 위당관",
        "PSY": "연세대학교 위당관",
        "CBE": "연세대학교 공학관",
        "EEE": "연세대학교 공학관",
        "ARC": "연세대학교 공학관",
        "CEE": "연세대학교 공학관",
        "MEE": "연세대학교 공학관",
        "MSE": "연세대학교 공학관",
        "CSI": "연세대학교 공학관",
        "IID": "연세대학교 공학관",
        "GLT": "연세대학교 공학관",  # Chemical Engineering
        "MAT": "연세대학교 과학관",
        "PHY": "연세대학교 과학관",
        "CHE": "연세대학교 과학관",
        "ESS": "연세대학교 과학관",
        "AST": "연세대학교 과학관",
        "ATM": "연세대학교 과학관",
        "ECO": "연세대학교 대우관",
        "STA": "연세대학교 대우관",
        "BIZ": "연세대학교 경영관",
        "POL": "연세대학교 정치외교학",
        "PUB": "연세대학교 외솔관",
        "SOC": "연세대학교 외솔관",
        "ANT": "연세대학교 외솔관",
        "COM": "연세대학교 외솔관",
        "SWK": "연세대학교 외솔관",
        "LAW": "연세대학교 법학관",
        "MED": "연세대학교 의과대학",
        "DEN": "연세대학교 치과대학",
        "NUR": "연세대학교 간호대학",
        "PHAR": "연세대학교 약학대학",
        "MUS": "연세대학교 음악대학",
        "ART": "연세대학교 미술대학",
        "THE": "연세대학교 신과대학",
        "CNT": "연세대학교 삼성관",
        "FNS": "연세대학교 삼성관",
        "HID": "연세대학교 삼성관",
        "CFM": "연세대학교 삼성관",
        "HEC": "연세대학교 삼성관"
    }
    '''
    
    if college_code and college_code in college_locations:
        return college_locations[college_code]
    
    # Default location if not found
    return "연세로 50"


def resolve_course_location(course_name: str) -> str:
    code = parse_course_id(course_name)
    return get_college_location(code)


def _normalize_course_header(raw_header: str) -> Tuple[str, str | None, str | None]:
    """Extract title, course code, instructor from raw bracketed text."""
    header = raw_header.strip()
    if header.startswith("[") and header.endswith("]"):
        header = header[1:-1]

    instructor = None
    if "/" in header:
        header, instructor = [part.strip() for part in header.split("/", 1)]

    code_match = re.search(r"([A-Z]{3}\d{4}\.\d{2}-\d{2})", header)
    course_code = code_match.group(1) if code_match else None

    # remove repeated codes and semester markers
    if course_code:
        header = header.replace(course_code, "").strip()
    header = header.replace("(2학기)", "").strip()

    return header, course_code, instructor


def format_course_label(raw_course: str) -> str:
    """Format course label in a clean format: [Course Code] Course Title"""
    title, course_code, _ = _normalize_course_header(raw_course)
    parts = []
    if course_code:
        parts.append(f"[{course_code}]")
    if title and title.strip():
        parts.append(title.strip())
    return " ".join(parts).strip() if parts else "과목"


def format_task_label(raw_course: str, task_title: str) -> str:
    """
    Format task label - returns just the task name for simplicity.
    Course info, due date, and estimated time are stored separately.
    """
    # Just return the task title, cleaned up
    task_name = task_title.strip() if task_title else "과제"
    return task_name


def estimate_task_time(task_title: str) -> int:
    """
    Estimate time required for a task based on keywords in the title.
    
    Args:
        task_title (str): Title of the task
        
    Returns:
        int: Estimated time in minutes
    """
    title_lower = task_title.lower()
    
    # Keyword-based heuristics
    if "프로젝트" in title_lower or "project" in title_lower:
        return 180  # 3 hours
    elif "레포트" in title_lower or "report" in title_lower or "보고서" in title_lower:
        return 90   # 1.5 hours
    elif "과제" in title_lower or "assignment" in title_lower or "homework" in title_lower:
        return 60   # 1 hour
    elif "퀴즈" in title_lower or "quiz" in title_lower:
        return 30   # 30 minutes
    elif "시험" in title_lower or "exam" in title_lower or "test" in title_lower:
        return 120  # 2 hours
    elif "발표" in title_lower or "presentation" in title_lower:
        return 90   # 1.5 hours
    elif "읽기" in title_lower or "reading" in title_lower:
        return 45   # 45 minutes
    else:
        return 60   # Default: 1 hour


def convert_lms_tasks(lms_tasks):
    """
    Convert LMS crawler output to Scheduler format.
    Scheduler expects: 'task', 'estimated_time', and 'location'
    """
    formatted_tasks = []
    print(f"\n📥 Converting {len(lms_tasks)} LMS tasks...")
    
    for t in lms_tasks:
        course_name = t.get('course', '')
        location = resolve_course_location(course_name)
        
        # Just use the task name (no course info in task name)
        task_name = format_task_label(course_name, t['task'])
        course_label = format_course_label(course_name)
        
        # Smart time estimation based on task title keywords
        estimated_time = estimate_task_time(t['task'])
        
        # Extract due date if available
        due_date = t.get('due_date', '')
        
        # Extract due date if available (crawler uses 'due_date')
        due_date = t.get('due_date', '')
        # Clean up "No deadline" to None
        deadline = due_date if due_date and due_date != "No deadline" else None
        
        formatted_tasks.append({
            "task": task_name,  # Just the task name (e.g., "11/3 presentation ppt")
            "estimated_time": estimated_time,  # Expected time in minutes
            "course": course_name,  # Full course name for reference
            "course_display": course_label,  # Formatted course name for display
            "location": location,
            "deadline": deadline,  # Due date stored separately
        })
        
        college_code = parse_course_id(course_name)
        if college_code:
            print(f"  ✓ {course_name} → {college_code} → {location} ({estimated_time}분)")
        else:
            print(f"  ⚠ {course_name} → (no course ID found) → {location} ({estimated_time}분)")
    
    return formatted_tasks


def fetch_raw_lms_tasks(username: str | None = None, password: str | None = None) -> List[Dict]:
    username = username or YONSEI_USERNAME
    password = password or YONSEI_PASSWORD

    if not username or not password:
        print("⚠️  Missing LMS credentials. Set YONSEI_USERNAME and YONSEI_PASSWORD.")
        return []

    crawler = LMSCrawler(username, password)
    if not crawler.login():
        print("❌ Login failed. Please check your credentials.")
        return []

    return crawler.fetch_tasks() or []


def get_crawler_tasks(username: str | None = None, password: str | None = None) -> List[Dict]:
    """Fetch and convert tasks from the LMS crawler."""
    raw_tasks = fetch_raw_lms_tasks(username, password)
    if not raw_tasks:
        print("⚠️  Login successful, but no incomplete tasks found.")
        return []
    return convert_lms_tasks(raw_tasks)


def build_schedule_from_lms(raw_tasks: List[Dict]) -> List[Dict]:
    events = []
    for task in raw_tasks:
        due_str = task.get("due_date")
        if not due_str:
            continue
        try:
            due_dt = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        start_dt = due_dt - timedelta(minutes=DEFAULT_TASK_DURATION)
        title = format_task_label(task.get('course', '과제'), task.get('task', ""))
        location = resolve_course_location(task.get("course", ""))

        events.append(
            {
                "name": title,
                "start_time": start_dt.strftime("%H:%M"),
                "end_time": due_dt.strftime("%H:%M"),
                "location": location,
            }
        )

    return sorted(events, key=lambda e: e["start_time"])


def get_daystack_data(source: str = "crawler") -> Tuple[List[Dict], List[Dict]]:
    """Shared helper for CLI/API to retrieve schedule and tasks."""
    use_lms_schedule = source == "crawler"
    schedule = get_schedule(use_lms=use_lms_schedule)

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
