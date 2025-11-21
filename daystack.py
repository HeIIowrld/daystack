"""
DAYSTACK - To-do list Tetris
Optimizing your daily tasks with travel time consideration
"""

from typing import Dict, List, Tuple

from typing import Dict, List, Tuple

from scheduler import allocate_tasks, print_schedule
from crawler import LMSCrawler
from config import YONSEI_USERNAME, YONSEI_PASSWORD

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
    tasks: List[Dict] = []
    tasks: List[Dict] = []
    
    while True:
        name = input("Task name: ").strip()
        if not name:
            break
        
        try:
            duration = int(input("Duration (minutes): ").strip())
            tasks.append({"task": name, "estimated_time": duration})
            tasks.append({"task": name, "estimated_time": duration})
            print("✓ Added\n")
        except ValueError:
            print("✗ Invalid duration\n")
    
    return tasks

def convert_lms_tasks(lms_tasks):
    """
    Convert LMS crawler output to Scheduler format.
    Since LMS doesn't provide 'duration', we set a default.
    """
    formatted_tasks = []
    print(f"\n📥 Converting {len(lms_tasks)} LMS tasks...")
    
    for t in lms_tasks:
        # Combine Course and Task Name for clarity
        full_name = f"[{t['course']}] {t['task']}"
        
        # Heuristic: Default to 60 mins for assignments, can be adjusted
        default_duration = 60 
        
        formatted_tasks.append({
            "name": full_name,
            "duration": default_duration,
            # You can pass due_date to scheduler if it supports it
            # "due_date": t['due_date'] 
        })
    return formatted_tasks

def main():
    print("\n" + "="*60)
    print("  DAYSTACK - To-do List Tetris")
    print("="*60)
    
    # Get tasks
    print("\nHow to get tasks?")
    print("  1. Fetch from LMS (mock data)")
    print("  2. Manual input")
    
    choice = input("\nChoice (1/2): ").strip()
    tasks = []

    if choice == '1':
        if YONSEI_USERNAME and YONSEI_PASSWORD:
            print("Using credentials from .env file...")
            crawler = LMSCrawler(YONSEI_USERNAME, YONSEI_PASSWORD)
            
            # --- FIX: MUST LOGIN BEFORE FETCHING ---
            if crawler.login():
                raw_tasks = crawler.fetch_tasks()
                if raw_tasks:
                    tasks = convert_lms_tasks(raw_tasks)
                else:
                    print("⚠️  Login successful, but no incomplete tasks found.")
            else:
                print("❌ Login failed. Please check your credentials.")
                return
        else:
            print("❌ No credentials found in .env")
            return
    else:
        tasks = manual_input_tasks()
    
    if not tasks:
        print("⚠️  No tasks to schedule")
        return
    
    print("\n📅 Today's Schedule:")
    for event in schedule:
        start = event.get('start_time', '')
        end = event.get('end_time', '')
        print(f"  {start}-{end}: {event['name']} @ {event['location']}")
    
    print("\n📚 Tasks:")
    for task in tasks:
        course = f" ({task['course']})" if task.get("course") else ""
        print(f"  - {task['task']}{course} / {task['estimated_time']}분")
    
    print("\n📚 Tasks:")
    for task in tasks:
        course = f" ({task['course']})" if task.get("course") else ""
        print(f"  - {task['task']}{course} / {task['estimated_time']}분")
    
    # Optimize
    print("\n🔄 Optimizing...")
    # Ensure allocate_tasks exists and accepts these arguments
    optimized = allocate_tasks(schedule, tasks)
    
    # Display result
    print_schedule(optimized)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")