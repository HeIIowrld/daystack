"""
Scheduler module for optimizing task allocation based on available time
Calculates free time between schedule items considering travel time
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from backend.directions import get_travel_time_from_addresses


def parse_time(time_str):
    """
    Parse time string to datetime object
    
    Args:
        time_str (str): Time in "HH:MM" format
    
    Returns:
        datetime: Parsed time for today
    """
    return datetime.strptime(time_str, "%H:%M")


def calculate_time_gap(end_time_str, start_time_str):
    """
    Calculate time gap between two times in minutes
    
    Args:
        end_time_str (str): End time of first event (format: "HH:MM")
        start_time_str (str): Start time of second event (format: "HH:MM")
    
    Returns:
        int: Time gap in minutes
    """
    end_time = parse_time(end_time_str)
    start_time = parse_time(start_time_str)
    
    time_diff = start_time - end_time
    return int(time_diff.total_seconds() / 60)


def calculate_free_time(schedule_item_1, schedule_item_2):
    """
    Calculate actual free time between two schedule items
    accounting for travel time
    
    Args:
        schedule_item_1 (dict): First schedule item with 'end_time' and 'location'
        schedule_item_2 (dict): Second schedule item with 'start_time' and 'location'
    
    Returns:
        dict: Contains 'free_time' (minutes), 'travel_time' (minutes), 
              'total_gap' (minutes)
    """
    # Calculate total time gap
    gap_total = calculate_time_gap(
        schedule_item_1['end_time'], 
        schedule_item_2['start_time']
    )
    
    # Calculate travel time between locations
    travel_time = get_travel_time_from_addresses(
        schedule_item_1['location'],
        schedule_item_2['location'],
        include_buffer=True
    )
    
    # Calculate actual free time
    real_free_time = gap_total - travel_time
    
    return {
        'total_gap': gap_total,
        'travel_time': travel_time,
        'free_time': max(0, real_free_time)  # Don't return negative time
    }


def allocate_tasks(
    schedule: List[Dict],
    todo_list: List[Dict],
    return_summary: bool = False,
) -> List[Dict] | Tuple[List[Dict], List[Dict]]:
    """
    Allocate tasks from todo_list to free time slots in schedule
    
    Args:
        schedule (list): List of schedule items with 'name', 'start_time', 
                        'end_time', 'location'
        todo_list (list): List of tasks with 'task' and 'estimated_time'
    
    Returns:
        list: Optimized schedule with allocated tasks
    """
    optimized_schedule = []
    remaining_tasks = todo_list.copy()
    
    # Sort schedule by time
    sorted_schedule = sorted(schedule, key=lambda x: x.get('start_time', x.get('end_time')))
    
    for i in range(len(sorted_schedule)):
        # Add the schedule item
        optimized_schedule.append(sorted_schedule[i])
        
        # Check if there's a next item to calculate gap
        if i < len(sorted_schedule) - 1:
            current_item = sorted_schedule[i]
            next_item = sorted_schedule[i + 1]
            
            # Calculate free time
            time_info = calculate_free_time(current_item, next_item)
            free_time = time_info['free_time']
            
            print(f"\n⏰ 시간 분석: {current_item['name']} → {next_item['name']}")
            print(f"   총 간격: {time_info['total_gap']}분")
            print(f"   이동 시간: {time_info['travel_time']}분")
            print(f"   사용 가능한 시간: {free_time}분")
            
            # Try to allocate tasks
            allocated = []
            for task in remaining_tasks[:]:
                if task['estimated_time'] <= free_time:
                    # Allocate this task
                    start_time = parse_time(current_item['end_time']) + timedelta(minutes=time_info['travel_time'])
                    end_time = start_time + timedelta(minutes=task['estimated_time'])
                    
                    optimized_schedule.append({
                        'name': f"📝 {task['task']}",
                        'start_time': start_time.strftime("%H:%M"),
                        'end_time': end_time.strftime("%H:%M"),
                        'location': current_item['location'],  # Assume task done at previous location
                        'type': 'task'
                    })
                    
                    allocated.append(task)
                    free_time -= task['estimated_time']
                    print(f"   ✓ '{task['task']}' 할당됨 ({task['estimated_time']}분)")
            
            # Remove allocated tasks
            for task in allocated:
                remaining_tasks.remove(task)
    
    # Report unallocated tasks
    if remaining_tasks:
        print(f"\n⚠ 할당되지 않은 작업:")
        for task in remaining_tasks:
            print(f"   - {task['task']} ({task['estimated_time']}분)")
    
    if return_summary:
        return optimized_schedule, remaining_tasks
    return optimized_schedule


def print_schedule(schedule: List[Dict]):
    """Pretty print the schedule"""
    print("\n" + "="*60)
    print("📅 최적화된 일정표")
    print("="*60)
    
    for item in schedule:
        if item.get('type') == 'task':
            print(f"{item['start_time']}-{item['end_time']} | {item['name']}")
        else:
            start = item.get('start_time', '')
            end = item.get('end_time', '')
            if start and end:
                time_str = f"{start}-{end}"
            elif start:
                time_str = f"{start}"
            elif end:
                time_str = f"~{end}"
            else:
                time_str = "시간 미정"
            
            print(f"{time_str:13} | 📌 {item['name']} @ {item['location']}")
    
    print("="*60 + "\n")


def test_scheduler():
    """Test function for scheduler"""
    print("=== Scheduler Test ===\n")
    
    # Sample schedule
    current_schedule = [
        {
            "name": "수업 A",
            "end_time": "13:00",
            "location": "강남역"
        },
        {
            "name": "아르바이트",
            "start_time": "15:00",
            "location": "판교역"
        }
    ]
    
    # Sample todo list
    todo_list = [
        {"task": "온라인 강의 듣기", "estimated_time": 40},
        {"task": "보고서 작성", "estimated_time": 90}
    ]
    
    print("📋 원본 일정:")
    for item in current_schedule:
        print(f"   - {item['name']} @ {item['location']}")
    
    print("\n📝 해야 할 일:")
    for task in todo_list:
        print(f"   - {task['task']} ({task['estimated_time']}분)")
    
    # Allocate tasks
    optimized = allocate_tasks(current_schedule, todo_list)
    
    # Print result
    print_schedule(optimized)


if __name__ == "__main__":
    from backend.config import Config
    
    try:
        Config.validate()
        test_scheduler()
    except ValueError as e:
        print(f"Configuration error: {e}")

