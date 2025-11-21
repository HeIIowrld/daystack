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
    
    if college_code and college_code in college_locations:
        return college_locations[college_code]
    
    # Default location if not found
    return "연세대학교"


def convert_lms_tasks(lms_tasks):
    """
    Convert LMS crawler output to Scheduler format.
    Scheduler expects: 'task', 'estimated_time', and 'location'
    """
    formatted_tasks = []
    print(f"\n📥 Converting {len(lms_tasks)} LMS tasks...")
    
    for t in lms_tasks:
        course_name = t.get('course', '')
        
        # Parse course ID to get college code
        college_code = parse_course_id(course_name)
        location = get_college_location(college_code)
        
        # Combine Course and Task Name for clarity
        full_name = f"[{course_name}] {t['task']}"
        
        # Heuristic: Default to 60 mins for assignments, can be adjusted
        default_duration = 60 
        
        formatted_tasks.append({
            "task": full_name,
            "estimated_time": default_duration,
            "course": course_name,
            "location": location,
        })
        
        if college_code:
            print(f"  ✓ {course_name} → {college_code} → {location}")
        else:
            print(f"  ⚠ {course_name} → (no course ID found) → {location}")
    
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
    
    # Get schedule
    schedule = get_schedule()
    
    print("\n📅 Today's Schedule:")
    for event in schedule:
        start = event.get('start_time', '')
        end = event.get('end_time', '')
        print(f"  {start}-{end}: {event['name']} @ {event['location']}")
    
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