"""
Scheduler module for optimizing task allocation based on available time.
Now orders tasks inside each gap using travel-time-aware routing.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from backend.directions import get_travel_time_from_addresses


def parse_time(time_str: str) -> datetime:
    """Parse HH:MM string to a datetime for today."""
    return datetime.strptime(time_str, "%H:%M")


def calculate_time_gap(end_time_str: str, start_time_str: str) -> int:
    """Calculate the minutes between two time strings."""
    end_time = parse_time(end_time_str)
    start_time = parse_time(start_time_str)
    return int((start_time - end_time).total_seconds() / 60)


def calculate_free_time(schedule_item_1: Dict, schedule_item_2: Dict) -> Dict[str, int]:
    """
    Legacy helper: free time between two events if you travel directly.
    Kept for compatibility/debug prints.
    """
    gap_total = calculate_time_gap(schedule_item_1["end_time"], schedule_item_2["start_time"])
    travel_time = get_travel_time_from_addresses(
        schedule_item_1["location"], schedule_item_2["location"], include_buffer=True
    )
    real_free_time = gap_total - travel_time
    return {
        "total_gap": gap_total,
        "travel_time": travel_time,
        "free_time": max(0, real_free_time),
    }


def _get_travel_minutes_cached(
    start: str,
    end: str,
    cache: Dict[Tuple[str, str, bool], int],
    include_buffer: bool = True,
) -> int:
    """Get travel minutes between two addresses with memoization."""
    key = (start, end, include_buffer)
    if key not in cache:
        cache[key] = get_travel_time_from_addresses(start, end, include_buffer=include_buffer)
    return cache[key]


def _pick_tasks_for_gap(
    current_item: Dict,
    next_item: Dict,
    remaining_tasks: List[Dict],
    travel_cache: Dict[Tuple[str, str, bool], int],
) -> List[Dict]:
    """
    Greedy route-aware packing: in a gap, keep choosing the next task whose
    travel + work still lets you reach the next event, preferring the plan
    that leaves the least slack and lowest travel penalty.
    """
    gap_start_time = parse_time(current_item["end_time"])
    deadline_time = parse_time(next_item["start_time"])
    current_location = current_item["location"]

    allocated: List[Dict] = []

    while remaining_tasks:
        minutes_until_next = int((deadline_time - gap_start_time).total_seconds() / 60)
        if minutes_until_next <= 0:
            break

        best_task = None
        best_score = None
        best_travel_to_task = 0
        best_travel_to_next = 0

        for task in remaining_tasks:
            task_location = task.get("location") or current_location
            travel_to_task = _get_travel_minutes_cached(
                current_location, task_location, travel_cache
            )
            travel_task_to_next = _get_travel_minutes_cached(
                task_location, next_item["location"], travel_cache
            )

            total_if_taken = travel_to_task + task["estimated_time"] + travel_task_to_next
            if total_if_taken > minutes_until_next:
                continue

            slack = minutes_until_next - total_if_taken
            travel_penalty = travel_to_task + travel_task_to_next
            score = (slack, travel_penalty)

            if (best_score is None) or (score < best_score):
                best_score = score
                best_task = task
                best_travel_to_task = travel_to_task
                best_travel_to_next = travel_task_to_next

        if not best_task:
            print(f"   ⚠️  경로/시간 제약으로 추가 배치 불가 (남은 {minutes_until_next}분)")
            break

        start_time = gap_start_time + timedelta(minutes=best_travel_to_task)
        end_time = start_time + timedelta(minutes=best_task["estimated_time"])

        allocated.append(
            {
                "name": f"✅ {best_task['task']}",
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "location": best_task.get("location", current_location),
                "type": "task",
            }
        )

        print(
            f"   ✅ '{best_task['task']}' 배치 "
            f"(이동 {best_travel_to_task}분 + 작업 {best_task['estimated_time']}분 | "
            f"다음 장소 이동 {best_travel_to_next}분)"
        )

        gap_start_time = end_time
        current_location = best_task.get("location", current_location)
        remaining_tasks.remove(best_task)

    return allocated


def allocate_tasks(
    schedule: List[Dict],
    todo_list: List[Dict],
    return_summary: bool = False,
) -> List[Dict] | Tuple[List[Dict], List[Dict]]:
    """
    Allocate tasks to free time slots, choosing a route that minimizes
    wasted travel while respecting arrival times for the next event.
    """
    optimized_schedule: List[Dict] = []
    remaining_tasks = todo_list.copy()
    travel_cache: Dict[Tuple[str, str, bool], int] = {}

    sorted_schedule = sorted(schedule, key=lambda x: x.get("start_time", x.get("end_time")))

    for i in range(len(sorted_schedule)):
        optimized_schedule.append(sorted_schedule[i])

        if i >= len(sorted_schedule) - 1:
            continue

        current_item = sorted_schedule[i]
        next_item = sorted_schedule[i + 1]

        gap_minutes = calculate_time_gap(current_item["end_time"], next_item["start_time"])
        time_info = calculate_free_time(current_item, next_item)

        print(f"\n⏱️/🗺️ 간격 분석: {current_item['name']} ➜ {next_item['name']}")
        print(f"   총 간격: {gap_minutes}분 (직행 시 이동 {time_info['travel_time']}분)")

        allocated = _pick_tasks_for_gap(current_item, next_item, remaining_tasks, travel_cache)
        optimized_schedule.extend(allocated)

    if remaining_tasks:
        print(f"\n⚠️  배치하지 못한 작업:")
        for task in remaining_tasks:
            print(f"   - {task['task']} ({task['estimated_time']}분)")

    if return_summary:
        return optimized_schedule, remaining_tasks
    return optimized_schedule


def print_schedule(schedule: List[Dict]):
    """Pretty print the schedule."""
    print("\n" + "=" * 60)
    print("📅 최적화된 일정")
    print("=" * 60)

    for item in schedule:
        if item.get("type") == "task":
            print(f"{item['start_time']}-{item['end_time']} | {item['name']} @ {item['location']}")
        else:
            start = item.get("start_time", "")
            end = item.get("end_time", "")
            if start and end:
                time_str = f"{start}-{end}"
            elif start:
                time_str = f"{start}"
            elif end:
                time_str = f"~{end}"
            else:
                time_str = "시간 미정"

            print(f"{time_str:13} | 📌 {item['name']} @ {item['location']}")

    print("=" * 60 + "\n")


def test_scheduler():
    """Test function for scheduler."""
    print("=== Scheduler Test ===\n")

    current_schedule = [
        {
            "name": "수업 A",
            "end_time": "13:00",
            "location": "강남역",
        },
        {
            "name": "알바",
            "start_time": "15:00",
            "location": "한양대",
        },
    ]

    todo_list = [
        {"task": "자바 강의 듣기", "estimated_time": 40, "location": "강남역"},
        {"task": "보고서 작성", "estimated_time": 90, "location": "뚝섬"},
        {"task": "팀 미팅", "estimated_time": 45, "location": "성수"},
    ]

    print("📌 기본 일정:")
    for item in current_schedule:
        print(f"   - {item['name']} @ {item['location']}")

    print("\n📝 해야 할 작업")
    for task in todo_list:
        where = f" @ {task['location']}" if task.get("location") else ""
        print(f"   - {task['task']} ({task['estimated_time']}분){where}")

    optimized = allocate_tasks(current_schedule, todo_list)
    print_schedule(optimized)


if __name__ == "__main__":
    from backend.config import Config

    try:
        Config.validate()
        test_scheduler()
    except ValueError as e:
        print(f"Configuration error: {e}")
