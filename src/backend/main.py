"""
YCC Scheduler - Main Application
Automatic schedule optimization with travel time consideration
"""

import sys
from datetime import datetime
from config import Config
from coursemos_crawler import CoursemosCrawler
from scheduler import allocate_tasks, print_schedule
from geocoding import get_location_coords
from directions import get_travel_time_from_addresses


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  YCC 스케줄러 - 이동시간 고려 일정 자동 최적화")
    print("="*60 + "\n")


def get_sample_schedule():
    """
    Get sample schedule for demonstration
    In production, this would come from user's calendar or database
    """
    return [
        {
            "name": "오전 수업",
            "start_time": "09:00",
            "end_time": "12:00",
            "location": "강남역"
        },
        {
            "name": "점심 약속",
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


def get_manual_todos():
    """
    Get todo list from user input or return sample data
    """
    print("📝 해야 할 일을 입력하세요 (샘플 데이터를 사용하려면 Enter를 누르세요)")
    print()
    
    use_sample = input("샘플 데이터를 사용하시겠습니까? (Y/n): ").strip().lower()
    
    if use_sample == 'n':
        todos = []
        print("\n작업을 입력하세요 (완료하려면 빈 줄 입력):")
        
        while True:
            task_name = input("  작업 이름: ").strip()
            if not task_name:
                break
            
            try:
                estimated_time = int(input("  예상 소요 시간 (분): ").strip())
                todos.append({
                    "task": task_name,
                    "estimated_time": estimated_time
                })
                print("  ✓ 추가됨\n")
            except ValueError:
                print("  ✗ 잘못된 시간 형식입니다. 다시 시도하세요.\n")
        
        return todos
    else:
        # Return sample data
        return [
            {"task": "온라인 강의 듣기", "estimated_time": 40},
            {"task": "영어 과제", "estimated_time": 30},
            {"task": "독서", "estimated_time": 45}
        ]


def run_with_crawler():
    """Run scheduler with Coursemos crawler"""
    print("🤖 Coursemos 크롤러 모드")
    print()
    
    # Initialize crawler
    crawler = CoursemosCrawler()
    
    # Fetch assignments (currently returns mock data)
    assignments = crawler.fetch_assignments()
    
    # Convert assignments to todo format
    todo_list = [
        {
            "task": assignment['task'],
            "estimated_time": assignment['estimated_time']
        }
        for assignment in assignments
    ]
    
    print(f"\n📚 가져온 과제: {len(todo_list)}개")
    
    return todo_list


def run_manual_mode():
    """Run scheduler with manual todo input"""
    print("✍️  수동 입력 모드")
    print()
    
    return get_manual_todos()


def main():
    """Main application entry point"""
    print_banner()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("\n.env 파일을 생성하고 Naver API 키를 설정해주세요.")
        print("예시는 .env.example 파일을 참조하세요.")
        sys.exit(1)
    
    print("✓ API 설정 확인 완료")
    print(f"✓ 이동 시간 버퍼: {Config.TRAVEL_TIME_BUFFER}분")
    print()
    
    # Choose mode
    print("모드 선택:")
    print("  1. Coursemos 크롤러 사용 (현재는 샘플 데이터)")
    print("  2. 수동으로 할 일 입력")
    print()
    
    choice = input("선택 (1/2): ").strip()
    print()
    
    if choice == '1':
        todo_list = run_with_crawler()
    else:
        todo_list = run_manual_mode()
    
    if not todo_list:
        print("⚠️  할 일이 없습니다.")
        sys.exit(0)
    
    # Get schedule (in production, this would come from user's calendar)
    print("\n📅 오늘의 일정:")
    current_schedule = get_sample_schedule()
    for item in current_schedule:
        start = item.get('start_time', '')
        end = item.get('end_time', '')
        print(f"   {start}-{end}: {item['name']} @ {item['location']}")
    
    print("\n" + "-"*60)
    print("🔄 일정 최적화 중...")
    print("-"*60)
    
    # Allocate tasks to free time slots
    optimized_schedule = allocate_tasks(current_schedule, todo_list)
    
    # Print optimized schedule
    print_schedule(optimized_schedule)
    
    print("✅ 일정 최적화 완료!")
    print()


def quick_test():
    """Quick test of core functionality"""
    print_banner()
    print("🧪 빠른 테스트 모드\n")
    
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        sys.exit(1)
    
    # Test geocoding
    print("1️⃣  주소 → 좌표 변환 테스트")
    test_address = "강남역"
    coords = get_location_coords(test_address)
    if coords:
        print(f"   ✓ {test_address} → {coords}\n")
    else:
        print(f"   ✗ 변환 실패\n")
        return
    
    # Test travel time
    print("2️⃣  이동 시간 계산 테스트")
    start = "강남역"
    end = "판교역"
    travel_time = get_travel_time_from_addresses(start, end)
    print(f"   ✓ {start} → {end}: {travel_time}분\n")
    
    print("✅ 모든 테스트 통과!\n")


if __name__ == "__main__":
    # Check if test mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            sys.exit(0)

