"""LMS Crawler - Based on yontil-main patterns"""
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


class LMSCrawler:
    """
    LMS Crawler using yontil-main patterns:
    - parse_input_tags_from_html (hidden field extraction)
    - Multi-step login flow
    - Course → Tasks hierarchy
    """
    
    def __init__(self, lms_url, username=None, password=None):
        self.lms_url = lms_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.logged_in = False
    
    def parse_input_tags_from_html(self, html):
        """Extract hidden form fields (yontil-main pattern)"""
        soup = BeautifulSoup(html, 'html.parser')
        fields = {}
        for input_tag in soup.find_all('input', id=True):
            field_id = input_tag.get('id')
            field_value = input_tag.get('value', '')
            if field_id:
                fields[field_id] = field_value
        return fields
    
    def login(self):
        """Login with hidden field support (yontil-main pattern)"""
        print(f"🔐 Logging in to {self.lms_url}...")
        
        # Step 1: Get login page and extract hidden fields
        response = self.session.get(f"{self.lms_url}/login")
        hidden_fields = self.parse_input_tags_from_html(response.text)
        
        # Step 2: Submit credentials with hidden fields
        login_data = {
            'username': self.username,
            'password': self.password,
            **hidden_fields  # Include CSRF tokens
        }
        
        response = self.session.post(f"{self.lms_url}/login", data=login_data)
        
        # Check success
        if 'logout' in response.text or 'dashboard' in response.url:
            self.logged_in = True
            print("✓ Login successful")
            return True
        else:
            print("✗ Login failed")
            return False
    
    def fetch_tasks(self):
        """
        Fetch tasks from LMS (yontil-main pattern)
        Course list → For each course → Extract incomplete tasks
        """
        if not self.logged_in:
            print("⚠️  Not logged in, using mock data")
            return self._mock_tasks()
        
        print("📥 Fetching tasks...")
        
        # Step 1: Get course list
        response = self.session.get(f"{self.lms_url}/courses")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        courses = soup.select('.course-list .course-item')
        all_tasks = []
        
        # Step 2: For each course, get tasks
        for course in courses:
            course_link = course.select_one('a.course-link')
            if not course_link:
                continue
            
            course_url = course_link.get('href')
            course_name = course_link.get_text(strip=True)
            
            # Get tasks in this course
            course_response = self.session.get(course_url)
            course_soup = BeautifulSoup(course_response.text, 'html.parser')
            
            # Find incomplete tasks (yontil-main pattern)
            tasks = course_soup.select('.activity:not(.completed)')
            
            for task in tasks:
                title = task.select_one('.activity-title')
                if title:
                    all_tasks.append({
                        'name': title.get_text(strip=True),
                        'course': course_name,
                        'duration': self._estimate_duration(title.get_text())
                    })
        
        print(f"✓ Found {len(all_tasks)} tasks")
        return all_tasks
    
    def _estimate_duration(self, task_name):
        """Estimate task duration based on keywords"""
        name_lower = task_name.lower()
        if any(word in name_lower for word in ['프로젝트', 'project']):
            return 180
        elif any(word in name_lower for word in ['레포트', 'report', '보고서']):
            return 90
        elif any(word in name_lower for word in ['퀴즈', 'quiz']):
            return 30
        else:
            return 60
    
    def _mock_tasks(self):
        """Mock data for testing"""
        return [
            {'name': '데이터베이스 과제', 'course': '데이터베이스', 'duration': 120},
            {'name': '알고리즘 레포트', 'course': '알고리즘', 'duration': 90},
            {'name': '웹 프로그래밍 프로젝트', 'course': '웹 프로그래밍', 'duration': 180}
        ]


if __name__ == "__main__":
    # Test with mock data
    crawler = LMSCrawler(
        lms_url="https://coursemos.co.kr",
        username="test",
        password="test"
    )
    
    tasks = crawler.fetch_tasks()
    
    print("\n📚 Tasks:")
    for task in tasks:
        print(f"  - {task['name']} ({task['duration']}분)")

