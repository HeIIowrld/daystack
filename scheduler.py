"""Core scheduling algorithm - "Tetris" task allocation"""
from datetime import datetime, timedelta
from naver_api import get_travel_duration_from_addresses


def parse_time(time_str):
    """Convert HH:MM string to datetime"""
    return datetime.strptime(time_str, "%H:%M")


def calculate_free_time(event1, event2):
    """
    Calculate free time between two events (accounting for travel)
    
    Returns: (total_gap, travel_time, free_time) in minutes
    """
    gap_minutes = int((parse_time(event2['start_time']) - parse_time(event1['end_time'])).total_seconds() / 60)
    
    travel_minutes = get_travel_duration_from_addresses(
        event1['location'],
        event2['location']
    )
    
    free_minutes = max(0, gap_minutes - travel_minutes)
    
    return gap_minutes, travel_minutes, free_minutes


def allocate_tasks(schedule, tasks):
    """
    Allocate tasks to free time slots (Tetris-style)
    
    Args:
        schedule: List of events with start_time, end_time, location
        tasks: List of tasks with name, duration (minutes)
    
    Returns:
        List of allocated time blocks
    """
    result = []
    remaining_tasks = tasks.copy()
    
    schedule = sorted(schedule, key=lambda x: x.get('start_time', x.get('end_time')))
    
    for i in range(len(schedule)):
        result.append(schedule[i])
        
        if i < len(schedule) - 1:
            gap, travel, free = calculate_free_time(schedule[i], schedule[i + 1])
            
            print(f"\n📊 Gap: {schedule[i]['name']} → {schedule[i + 1]['name']}")
            print(f"   Total: {gap}분 | Travel: {travel}분 | Free: {free}분")
            
            # Allocate tasks that fit
            current_time = parse_time(schedule[i]['end_time']) + timedelta(minutes=travel)
            
            for task in remaining_tasks[:]:
                if task['duration'] <= free:
                    result.append({
                        'name': f"✓ {task['name']}",
                        'start_time': current_time.strftime("%H:%M"),
                        'end_time': (current_time + timedelta(minutes=task['duration'])).strftime("%H:%M"),
                        'location': schedule[i]['location'],
                        'type': 'task'
                    })
                    current_time += timedelta(minutes=task['duration'])
                    free -= task['duration']
                    remaining_tasks.remove(task)
                    print(f"   ✓ Allocated: {task['name']} ({task['duration']}분)")
    
    if remaining_tasks:
        print(f"\n⚠️  Unallocated tasks:")
        for task in remaining_tasks:
            print(f"   - {task['name']} ({task['duration']}분)")
    
    return result


def print_schedule(schedule):
    """Pretty print the schedule"""
    print("\n" + "="*60)
    print("📅 DAYSTACK - Optimized Schedule")
    print("="*60)
    
    for item in schedule:
        start = item.get('start_time', '')
        end = item.get('end_time', '')
        time_str = f"{start}-{end}" if start and end else start or end
        
        icon = "✓" if item.get('type') == 'task' else "📌"
        print(f"{time_str:13} {icon} {item['name']}")
    
    print("="*60)


if __name__ == "__main__":
    # Test
    test_schedule = [
        {"name": "수업", "end_time": "13:00", "location": "강남역"},
        {"name": "아르바이트", "start_time": "16:00", "location": "판교역"}
    ]
    
    test_tasks = [
        {"name": "온라인 강의", "duration": 40},
        {"name": "과제 작성", "duration": 30}
    ]
    
    result = allocate_tasks(test_schedule, test_tasks)
    print_schedule(result)

