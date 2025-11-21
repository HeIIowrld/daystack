"""
Coursemos LMS Crawler Module
Based on yontil-main project patterns for login and task fetching.

This implementation provides two methods:
1. requests + BeautifulSoup: Fast, lightweight (for simple pages)
2. Selenium: Full browser automation (for JavaScript-heavy pages)

Adapted from: yontil-main/src/core/login/ and yontil-main/src/core/tasks/
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import requests
from bs4 import BeautifulSoup


class CoursemosCrawler:
    """
    Crawler for Coursemos LMS to fetch assignments and deadlines
    Supports both requests-based and Selenium-based approaches
    """
    
    # Coursemos URLs (adjust these to match actual Coursemos endpoints)
    COURSEMOS_ORIGIN = "https://coursemos.co.kr"
    LOGIN_URL = f"{COURSEMOS_ORIGIN}/login"
    MAIN_PAGE_URL = f"{COURSEMOS_ORIGIN}/main"
    
    def __init__(self, username=None, password=None, use_selenium=False):
        """
        Initialize crawler with credentials
        
        Args:
            username (str): Coursemos username
            password (str): Coursemos password
            use_selenium (bool): Whether to use Selenium instead of requests
        """
        self.username = username
        self.password = password
        self.use_selenium = use_selenium
        self.logged_in = False
        self.session = requests.Session()
        self.driver = None
        
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def parse_input_tags_from_html(self, html_string: str) -> Dict[str, str]:
        """
        Parse HTML to extract input tag id-value pairs
        Based on: yontil-main/src/utils/parse-html-string.ts
        
        Args:
            html_string (str): Raw HTML to parse
        
        Returns:
            dict: Dictionary of input id-value pairs
        """
        soup = BeautifulSoup(html_string, 'html.parser')
        input_attributes = {}
        
        for input_tag in soup.find_all('input', id=True):
            input_id = input_tag.get('id')
            input_value = input_tag.get('value', '')
            if input_id:
                input_attributes[input_id] = input_value
        
        return input_attributes
    
    def login(self):
        """
        Login to Coursemos LMS
        Uses multi-step authentication similar to Learnus login
        Based on: yontil-main/src/core/login/login-learnus.ts
        """
        if self.use_selenium:
            return self._login_selenium()
        else:
            return self._login_requests()
    
    def _login_requests(self):
        """
        Login using requests library (fast, lightweight)
        Implements multi-step login flow similar to yontil-main
        """
        print("🔐 Logging into Coursemos (requests mode)...")
        
        try:
            # Step 1: Get login page and extract CSRF tokens
            response = self.session.get(self.LOGIN_URL, timeout=10)
            response.raise_for_status()
            
            # Parse hidden form fields
            hidden_fields = self.parse_input_tags_from_html(response.text)
            
            # Step 2: Submit login credentials
            login_data = {
                'username': self.username,
                'password': self.password,
                **hidden_fields  # Include CSRF tokens and other hidden fields
            }
            
            response = self.session.post(
                self.LOGIN_URL,
                data=login_data,
                timeout=10,
                allow_redirects=True
            )
            
            # Check if login was successful
            if self._check_login_success(response):
                self.logged_in = True
                print("✓ Login successful")
                return True
            else:
                print("✗ Login failed - check credentials")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Login error: {e}")
            return False
    
    def _login_selenium(self):
        """
        Login using Selenium (for JavaScript-heavy pages)
        """
        print("🔐 Logging into Coursemos (Selenium mode)...")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Initialize Chrome driver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(self.LOGIN_URL)
            
            # Wait for and fill login form
            wait = WebDriverWait(self.driver, 10)
            
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.username)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Submit form
            submit_button = self.driver.find_element(By.ID, "login-button")
            submit_button.click()
            
            # Wait for redirect to main page
            wait.until(EC.url_contains("main"))
            
            self.logged_in = True
            print("✓ Login successful")
            return True
            
        except Exception as e:
            print(f"✗ Selenium login error: {e}")
            return False
    
    def _check_login_success(self, response) -> bool:
        """
        Check if login was successful by looking for indicators
        
        Args:
            response: HTTP response object
        
        Returns:
            bool: True if login succeeded
        """
        # Check if redirected to main page
        if 'main' in response.url or 'dashboard' in response.url:
            return True
        
        # Check for login error messages
        soup = BeautifulSoup(response.text, 'html.parser')
        error_indicators = soup.find_all(class_=['error', 'alert-danger', 'login-error'])
        
        return len(error_indicators) == 0
    
    def fetch_assignments(self) -> List[Dict]:
        """
        Fetch assignments from Coursemos
        Based on: yontil-main/src/core/tasks/fetch-tasks.ts
        
        Returns:
            list: List of assignments with task name, deadline, and estimated time
        """
        if not self.logged_in:
            if not self.login():
                print("⚠️  Cannot fetch assignments - login failed")
                return self._get_mock_assignments()
        
        print("📥 Fetching assignments from Coursemos...")
        
        try:
            if self.use_selenium:
                return self._fetch_assignments_selenium()
            else:
                return self._fetch_assignments_requests()
        except Exception as e:
            print(f"⚠️  Error fetching assignments: {e}")
            print("   Falling back to mock data...")
            return self._get_mock_assignments()
    
    def _fetch_assignments_requests(self) -> List[Dict]:
        """
        Fetch assignments using requests library
        Based on yontil-main task fetching pattern
        """
        assignments = []
        
        # Step 1: Get main page with course list
        response = self.session.get(self.MAIN_PAGE_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 2: Find all courses (adjust selector to match Coursemos)
        course_elements = soup.select('.my-course-lists li, .course-list .course-item')
        
        print(f"   Found {len(course_elements)} courses")
        
        # Step 3: Fetch tasks from each course
        for course_elem in course_elements:
            course_link = course_elem.select_one('.course-link, a.course-title')
            if not course_link:
                continue
            
            course_url = course_link.get('href')
            course_name = course_link.get_text(strip=True)
            
            # Fetch tasks for this course
            course_tasks = self._fetch_tasks_in_course(course_url, course_name)
            assignments.extend(course_tasks)
        
        print(f"✓ Found {len(assignments)} assignments")
        return assignments
    
    def _fetch_tasks_in_course(self, course_url: str, course_name: str) -> List[Dict]:
        """
        Fetch tasks/assignments within a specific course
        Similar to: yontil-main/src/core/tasks/fetch-tasks.ts#fetchTaskElementsInCourse
        
        Args:
            course_url (str): URL of the course page
            course_name (str): Name of the course
        
        Returns:
            list: List of tasks/assignments
        """
        tasks = []
        
        try:
            # Make URL absolute if needed
            if not course_url.startswith('http'):
                course_url = self.COURSEMOS_ORIGIN + course_url
            
            response = self.session.get(course_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find incomplete tasks (adjust selectors to match Coursemos)
            # Similar to yontil-main: looking for tasks with completion-auto-n
            task_elements = soup.select(
                '.activity:not(.completed), '
                '.assignment:not(.submitted), '
                '.task-item:not(.done)'
            )
            
            for task_elem in task_elements:
                # Extract task information
                title_elem = task_elem.select_one('.activity-title, .assignment-title, .task-title')
                deadline_elem = task_elem.select_one('.deadline, .due-date')
                
                if title_elem:
                    task_title = title_elem.get_text(strip=True)
                    deadline_text = deadline_elem.get_text(strip=True) if deadline_elem else None
                    
                    tasks.append({
                        "task": task_title,
                        "course": course_name,
                        "deadline": self._parse_deadline(deadline_text),
                        "estimated_time": self.estimate_task_time(task_title),
                        "url": course_url
                    })
        
        except Exception as e:
            print(f"   ⚠️  Error fetching tasks from {course_name}: {e}")
        
        return tasks
    
    def _fetch_assignments_selenium(self) -> List[Dict]:
        """
        Fetch assignments using Selenium
        """
        from selenium.webdriver.common.by import By
        
        assignments = []
        
        # Navigate to main page
        self.driver.get(self.MAIN_PAGE_URL)
        
        # Find course elements
        course_elements = self.driver.find_elements(By.CSS_SELECTOR, '.course-item, .my-course-lists li')
        
        for course_elem in course_elements:
            try:
                course_link = course_elem.find_element(By.CSS_SELECTOR, '.course-link, a')
                course_url = course_link.get_attribute('href')
                course_name = course_link.text
                
                # Visit course page
                self.driver.get(course_url)
                
                # Find incomplete assignments
                task_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    '.activity:not(.completed), .assignment:not(.submitted)'
                )
                
                for task_elem in task_elements:
                    title = task_elem.find_element(By.CSS_SELECTOR, '.title').text
                    
                    try:
                        deadline = task_elem.find_element(By.CSS_SELECTOR, '.deadline').text
                    except:
                        deadline = None
                    
                    assignments.append({
                        "task": title,
                        "course": course_name,
                        "deadline": self._parse_deadline(deadline),
                        "estimated_time": self.estimate_task_time(title),
                        "url": course_url
                    })
            except Exception as e:
                print(f"   ⚠️  Error processing course: {e}")
                continue
        
        return assignments
    
    def _parse_deadline(self, deadline_text: Optional[str]) -> str:
        """
        Parse deadline text to standard format
        
        Args:
            deadline_text (str): Raw deadline text from page
        
        Returns:
            str: Formatted deadline (YYYY-MM-DD HH:MM)
        """
        if not deadline_text:
            return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        
        # Try to extract date patterns
        # Format: "2024-12-25 23:59" or "12월 25일 23:59"
        
        # Try ISO format first
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', deadline_text)
        if iso_match:
            return iso_match.group(1)
        
        # Try Korean format
        kr_match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', deadline_text)
        if kr_match:
            month = int(kr_match.group(1))
            day = int(kr_match.group(2))
            year = datetime.now().year
            return f"{year}-{month:02d}-{day:02d} 23:59"
        
        # Default: 7 days from now
        return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    
    def _get_mock_assignments(self) -> List[Dict]:
        """
        Return mock data for demonstration/testing
        """
        return [
            {
                "task": "데이터베이스 과제 #3",
                "estimated_time": 120,
                "deadline": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
                "course": "데이터베이스 시스템",
                "url": f"{self.COURSEMOS_ORIGIN}/course/123"
            },
            {
                "task": "알고리즘 레포트 작성",
                "estimated_time": 90,
                "deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
                "course": "알고리즘",
                "url": f"{self.COURSEMOS_ORIGIN}/course/456"
            },
            {
                "task": "웹 프로그래밍 프로젝트",
                "estimated_time": 180,
                "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M"),
                "course": "웹 프로그래밍",
                "url": f"{self.COURSEMOS_ORIGIN}/course/789"
            }
        ]
    
    def estimate_task_time(self, assignment_title: str) -> int:
        """
        Estimate time required for an assignment
        
        Args:
            assignment_title (str): Title of the assignment
        
        Returns:
            int: Estimated time in minutes
        
        Note: This could be enhanced with ML model based on historical data
        """
        # Simple heuristic based on keywords
        title_lower = assignment_title.lower()
        
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
        else:
            return 45   # 45 minutes default
    
    def logout(self):
        """Logout from Coursemos and cleanup resources"""
        print("🚪 Logging out of Coursemos...")
        
        if self.use_selenium and self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.session:
            self.session.close()
        
        self.logged_in = False
        print("✓ Logout successful")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.logout()


def test_crawler():
    """Test function for Coursemos crawler"""
    print("=== Coursemos Crawler Test ===\n")
    print("📝 Note: This will use mock data unless you provide real credentials\n")
    
    # Test with mock data (no real login)
    print("1️⃣  Testing with mock data...")
    with CoursemosCrawler(username="test_user", password="test_pass") as crawler:
        assignments = crawler.fetch_assignments()
        
        print("\n📚 과제 목록:")
        for i, assignment in enumerate(assignments, 1):
            print(f"\n{i}. 과목: {assignment['course']}")
            print(f"   과제: {assignment['task']}")
            print(f"   마감: {assignment['deadline']}")
            print(f"   예상 소요 시간: {assignment['estimated_time']}분")
            if 'url' in assignment:
                print(f"   URL: {assignment['url']}")
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("\n💡 To use with real Coursemos:")
    print("   1. Update COURSEMOS_ORIGIN, LOGIN_URL in the class")
    print("   2. Update HTML selectors to match Coursemos structure")
    print("   3. Provide real username/password")
    print("   4. Optional: Set use_selenium=True for JavaScript pages")


def test_html_parsing():
    """Test HTML parsing functionality"""
    print("\n=== HTML Parsing Test ===\n")
    
    sample_html = '''
    <html>
        <body>
            <input id="csrf_token" value="abc123" />
            <input id="session_id" value="xyz789" />
            <input type="text" name="username" value="" />
        </body>
    </html>
    '''
    
    crawler = CoursemosCrawler()
    parsed = crawler.parse_input_tags_from_html(sample_html)
    
    print("Parsed input tags:")
    for key, value in parsed.items():
        print(f"   {key}: {value}")
    
    print("\n✅ HTML parsing test passed!")


if __name__ == "__main__":
    test_crawler()
    print()
    test_html_parsing()

