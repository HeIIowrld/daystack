"""
DAYSTACK - To-do list Tetris
Optimizing your daily tasks with travel time consideration
"""

from scheduler import allocate_tasks, print_schedule
from crawler import LMSCrawler


def get_schedule():
    """Get today's schedule (hardcoded for now)"""
    return [
        {
            "name": "오전 수업",
            "start_time": "09:00",
            "end_time": "12:00",
            "location": "강남역"
        },
        {
            "name": "점심",
            "start_time": "12:30",
            "end_time": "13:30",
            "location": "강남역"
        },
        {
            "name": "아르바이트",
            "start_time": "16:00",
            "end_time": "20:00",
            "location": "판교역"
        }
    ]


def manual_input_tasks():
    """Manual task input"""
    print("\n📝 Enter tasks (empty line to finish):\n")
    tasks = []
    
    while True:
        name = input("Task name: ").strip()
        if not name:
            break
        
        try:
            duration = int(input("Duration (minutes): ").strip())
            tasks.append({"name": name, "duration": duration})
            print("✓ Added\n")
        except ValueError:
            print("✗ Invalid duration\n")
    
    return tasks


def main():
    print("\n" + "="*60)
    print("  DAYSTACK - To-do List Tetris")
    print("="*60)
    
    # Get tasks
    print("\nHow to get tasks?")
    print("  1. Fetch from LMS (mock data)")
    print("  2. Manual input")
    
    choice = input("\nChoice (1/2): ").strip()
    
    if choice == '1':
        crawler = LMSCrawler("https://coursemos.co.kr")
        tasks = crawler.fetch_tasks()
    else:
        tasks = manual_input_tasks()
    
    if not tasks:
        print("⚠️  No tasks to schedule")
        return
    
    # Get schedule
    schedule = get_schedule()
    
    print("\n📅 Today's Schedule:")
    for event in schedule:
        start = event.get('start_time', '')
        end = event.get('end_time', '')
        print(f"  {start}-{end}: {event['name']} @ {event['location']}")
    
    # Optimize
    print("\n🔄 Optimizing...")
    optimized = allocate_tasks(schedule, tasks)
    
    # Display result
    print_schedule(optimized)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")

