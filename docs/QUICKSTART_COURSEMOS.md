# Coursemos Crawler Quick Start Guide

A practical guide to using and customizing the Coursemos crawler based on yontil-main patterns.

## 🚀 Quick Start (5 Minutes)

### Step 1: Test with Mock Data (No Setup Required)

```bash
# Run the crawler test
python coursemos_crawler.py
```

You'll see:
```
=== Coursemos Crawler Test ===

1️⃣  Testing with mock data...
📥 Fetching assignments from Coursemos...
✓ Found 3 assignments (mock data)

📚 과제 목록:

1. 과목: 데이터베이스 시스템
   과제: 데이터베이스 과제 #3
   마감: 2024-11-24 15:30
   예상 소요 시간: 120분
   URL: https://coursemos.co.kr/course/123
   
...

✅ Test completed!
```

### Step 2: Understand the Code Structure

```python
from coursemos_crawler import CoursemosCrawler

# Initialize crawler
crawler = CoursemosCrawler(
    username="your_username",
    password="your_password",
    use_selenium=False  # True = use browser, False = use requests
)

# Login
if crawler.login():
    # Fetch assignments
    assignments = crawler.fetch_assignments()
    
    # Use the data
    for assignment in assignments:
        print(f"{assignment['task']} - {assignment['deadline']}")

# Cleanup
crawler.logout()
```

### Step 3: Integration with Main Scheduler

```bash
# Run main application
python main.py

# Choose option 1: "Coursemos 크롤러 사용"
```

---

## 🔧 Customization Guide

### Part 1: Update URLs for Your LMS

Open `coursemos_crawler.py` and update these lines:

```python
class CoursemosCrawler:
    # CHANGE THESE to match your actual LMS
    COURSEMOS_ORIGIN = "https://your-actual-lms.com"
    LOGIN_URL = f"{COURSEMOS_ORIGIN}/login"  # or /auth, /signin
    MAIN_PAGE_URL = f"{COURSEMOS_ORIGIN}/main"  # or /dashboard, /home
```

### Part 2: Find the Right CSS Selectors

#### 2.1 Open Your LMS in Chrome

1. Login to your LMS manually
2. Press `F12` to open DevTools
3. Go to the "Elements" tab

#### 2.2 Find Course List Selectors

On the main/dashboard page, find the course list:

```html
<!-- Example HTML structure - yours may differ -->
<div class="course-container">
  <ul class="my-courses">
    <li class="course-item">
      <a href="/course/123" class="course-link">Database Systems</a>
    </li>
    <li class="course-item">
      <a href="/course/456" class="course-link">Algorithms</a>
    </li>
  </ul>
</div>
```

In DevTools Console, test your selector:
```javascript
// Find course list
document.querySelectorAll('.my-courses li')
// or
document.querySelectorAll('.course-item')
```

Update in `coursemos_crawler.py`:
```python
def _fetch_assignments_requests(self):
    # UPDATE THIS selector
    course_elements = soup.select('.my-courses li')  # ← Your selector here
```

#### 2.3 Find Course Link Selector

```javascript
// In console, from a course item:
document.querySelector('.course-item').querySelector('.course-link')
// or
document.querySelector('.course-item a')
```

Update:
```python
course_link = course_elem.select_one('.course-link')  # ← Your selector
```

#### 2.4 Find Assignment/Task Selectors

Open a course page and find incomplete assignments:

```html
<!-- Example structure -->
<div class="activities">
  <div class="activity completed">
    <span class="activity-title">Completed Assignment</span>
  </div>
  <div class="activity">  <!-- NO 'completed' class = incomplete -->
    <span class="activity-title">Pending Assignment</span>
    <span class="deadline">2024-11-30 23:59</span>
  </div>
</div>
```

Test in console:
```javascript
// Find incomplete tasks
document.querySelectorAll('.activity:not(.completed)')
// or
document.querySelectorAll('.assignment:not(.submitted)')
```

Update:
```python
def _fetch_tasks_in_course(self, course_url, course_name):
    # UPDATE THESE selectors
    task_elements = soup.select(
        '.activity:not(.completed), '  # ← Your selector
        '.assignment:not(.submitted)'   # ← Alternative selector
    )
    
    # UPDATE title and deadline selectors
    title_elem = task_elem.select_one('.activity-title')  # ← Your selector
    deadline_elem = task_elem.select_one('.deadline')      # ← Your selector
```

### Part 3: Test Your Selectors

Create a test script:

```python
# test_selectors.py
from coursemos_crawler import CoursemosCrawler

crawler = CoursemosCrawler(
    username="your_username",
    password="your_password"
)

# Test login
print("Testing login...")
if crawler.login():
    print("✅ Login successful!")
    
    # Test main page fetch
    print("\nTesting course list fetch...")
    response = crawler.session.get(crawler.MAIN_PAGE_URL)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Test your selector
    courses = soup.select('.my-courses li')  # ← Your selector
    print(f"Found {len(courses)} courses")
    
    if len(courses) > 0:
        print("✅ Course selector works!")
        
        # Test course link selector
        first_course = courses[0]
        link = first_course.select_one('.course-link')  # ← Your selector
        if link:
            print(f"✅ Course link selector works! URL: {link.get('href')}")
        else:
            print("❌ Course link selector failed!")
    else:
        print("❌ Course selector didn't find any courses!")
else:
    print("❌ Login failed!")

crawler.logout()
```

Run:
```bash
python test_selectors.py
```

### Part 4: Handle Login Forms

#### 4.1 Simple Form Login

If your LMS uses a simple login form:

```python
# This is already implemented in _login_requests()
def _login_requests(self):
    # Get login page
    response = self.session.get(self.LOGIN_URL)
    
    # Extract hidden fields (CSRF tokens, etc.)
    hidden_fields = self.parse_input_tags_from_html(response.text)
    
    # Submit with username, password, AND hidden fields
    login_data = {
        'username': self.username,  # ← Change field name if needed
        'password': self.password,   # ← Change field name if needed
        **hidden_fields
    }
    
    response = self.session.post(self.LOGIN_URL, data=login_data)
    return self._check_login_success(response)
```

**If your LMS uses different field names:**

Inspect the login form HTML:
```html
<form action="/login" method="POST">
  <input type="text" name="user_id" />      ← Not "username"
  <input type="password" name="user_pwd" /> ← Not "password"
</form>
```

Update:
```python
login_data = {
    'user_id': self.username,   # ← Changed
    'user_pwd': self.password,  # ← Changed
    **hidden_fields
}
```

#### 4.2 Multi-Step Login (like yontil-main)

If your LMS requires multiple steps:

```python
def _login_requests_multistep(self):
    # Step 1: Get initial token
    response1 = self.session.get(f"{self.COURSEMOS_ORIGIN}/auth/step1")
    token1 = self.parse_input_tags_from_html(response1.text)
    
    # Step 2: Submit token and get challenge
    response2 = self.session.post(
        f"{self.COURSEMOS_ORIGIN}/auth/step2",
        data={'token': token1['session_token']}
    )
    challenge = response2.json()['challenge']
    
    # Step 3: Submit credentials with challenge
    response3 = self.session.post(
        f"{self.COURSEMOS_ORIGIN}/auth/step3",
        data={
            'username': self.username,
            'password': self.password,
            'challenge': challenge
        }
    )
    
    return self._check_login_success(response3)
```

---

## 🐛 Debugging Tips

### Enable Verbose Logging

Add this to see all HTTP requests:

```python
import logging
import http.client

http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
```

### Save HTML for Inspection

```python
def _fetch_assignments_requests(self):
    response = self.session.get(self.MAIN_PAGE_URL)
    
    # Save HTML to file for inspection
    with open('main_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    # Continue with parsing...
```

Then open `main_page.html` in your browser to see what the crawler sees.

### Check Cookies

```python
# After login, print cookies
print("Current cookies:", self.session.cookies.get_dict())
```

### Test in Browser First

Use browser DevTools Network tab:
1. Clear cache and cookies
2. Login manually
3. Watch Network tab for requests
4. Note: URLs, method (GET/POST), form data
5. Replicate in crawler code

---

## 🎯 Common Issues & Solutions

### Issue 1: "Login failed - check credentials"

**Cause:** Wrong field names or missing CSRF token

**Solution:**
```python
# Debug: Print form fields
response = self.session.get(self.LOGIN_URL)
print("HTML:", response.text[:1000])  # First 1000 chars

# Check what fields are expected
from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form')
for input_tag in form.find_all('input'):
    print(f"Field: {input_tag.get('name')} (type: {input_tag.get('type')})")
```

### Issue 2: "Found 0 courses"

**Cause:** Wrong CSS selector or page requires JavaScript

**Solution 1:** Check selector
```python
# Try different selectors
selectors_to_try = [
    '.my-course-lists li',
    '.course-list .course-item',
    '.courses li',
    'div.course',
    'ul[class*="course"] li'
]

for selector in selectors_to_try:
    result = soup.select(selector)
    print(f"{selector}: found {len(result)} elements")
```

**Solution 2:** Use Selenium (page needs JavaScript)
```python
crawler = CoursemosCrawler(
    username="user",
    password="pass",
    use_selenium=True  # ← Enable browser automation
)
```

### Issue 3: "Found courses but no tasks"

**Cause:** Wrong task selector or tasks are dynamically loaded

**Solution:** Same as Issue 2 - try different selectors or enable Selenium

### Issue 4: CAPTCHA or 2FA

**Cause:** LMS has anti-bot protection

**Solution 1:** Manual session export
```python
# 1. Login manually in browser
# 2. Export cookies using extension like "EditThisCookie"
# 3. Import to crawler

cookies = {
    'session_id': 'your_session_id_here',
    'csrf_token': 'your_csrf_token_here'
}

for name, value in cookies.items():
    crawler.session.cookies.set(name, value)

# Now skip login, directly fetch assignments
assignments = crawler.fetch_assignments()
```

**Solution 2:** Use Selenium with manual intervention
```python
# Don't use headless mode
options = webdriver.ChromeOptions()
# Remove: options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get(LOGIN_URL)

# Manually solve CAPTCHA, then press Enter in terminal
input("Solve CAPTCHA in browser, then press Enter...")

# Continue automation
# ...
```

---

## 📊 Real Example: Customizing for "MyUniversity LMS"

Let's say you're adapting for a fictional "MyUniversity LMS":

```python
# coursemos_crawler.py - customized

class CoursemosCrawler:
    # Step 1: Update URLs
    COURSEMOS_ORIGIN = "https://lms.myuniversity.edu"
    LOGIN_URL = f"{COURSEMOS_ORIGIN}/user/login"
    MAIN_PAGE_URL = f"{COURSEMOS_ORIGIN}/dashboard"
    
    # ...
    
    def _login_requests(self):
        # Step 2: Update login fields (found via browser inspection)
        login_data = {
            'email': self.username,        # ← They use 'email' not 'username'
            'pwd': self.password,          # ← They use 'pwd' not 'password'
            'remember': 'true',            # ← Extra field
            **hidden_fields
        }
        # ...
    
    def _fetch_assignments_requests(self):
        # Step 3: Update course selector
        course_elements = soup.select('div.dashboard-course-card')  # ← Their class
        
        for course_elem in course_elements:
            # Step 4: Update link selector
            course_link = course_elem.select_one('h3 a')  # ← Their structure
            # ...
    
    def _fetch_tasks_in_course(self, course_url, course_name):
        # Step 5: Update task selectors
        task_elements = soup.select(
            'li.task-item[data-status="incomplete"]'  # ← Their structure
        )
        
        for task_elem in task_elements:
            # Step 6: Update metadata selectors
            title_elem = task_elem.select_one('h4.task-name')  # ← Their class
            deadline_elem = task_elem.select_one('time.due-date')  # ← Their class
            # ...
```

Test:
```bash
python coursemos_crawler.py
```

If successful:
```
✓ Found 5 courses
✓ Found 12 assignments
```

---

## 🎓 Advanced: Adding New Features

### Feature 1: Priority Detection

```python
def _fetch_tasks_in_course(self, course_url, course_name):
    for task_elem in task_elements:
        # ...existing code...
        
        # Add priority detection
        priority = "normal"
        if task_elem.select_one('.badge-urgent, .priority-high'):
            priority = "high"
        elif task_elem.select_one('.badge-low'):
            priority = "low"
        
        tasks.append({
            # ...existing fields...
            "priority": priority  # ← New field
        })
```

### Feature 2: Task Categorization

```python
def estimate_task_time(self, assignment_title: str) -> tuple[int, str]:
    """Returns (time_minutes, category)"""
    
    title_lower = assignment_title.lower()
    
    if any(word in title_lower for word in ["프로젝트", "project"]):
        return (180, "project")
    elif any(word in title_lower for word in ["퀴즈", "quiz"]):
        return (30, "quiz")
    elif any(word in title_lower for word in ["시험", "exam"]):
        return (120, "exam")
    else:
        return (60, "assignment")
```

### Feature 3: Cache Support

```python
import json
from datetime import datetime, timedelta

def fetch_assignments(self, use_cache=True, cache_duration_hours=1):
    cache_file = 'assignments_cache.json'
    
    # Check cache
    if use_cache and os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            
            if datetime.now() - cache_time < timedelta(hours=cache_duration_hours):
                print("✓ Using cached data")
                return cache['assignments']
    
    # Fetch fresh data
    assignments = self._fetch_assignments_requests()
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'assignments': assignments
        }, f)
    
    return assignments
```

---

## ✅ Checklist: Before Going Live

- [ ] URLs updated to real LMS domain
- [ ] Login field names verified
- [ ] Course list selector tested and working
- [ ] Course link selector tested and working
- [ ] Task list selector tested and working
- [ ] Task title selector tested and working
- [ ] Deadline selector tested and working (or defaults work)
- [ ] Login success/failure detection works
- [ ] Session persistence works across requests
- [ ] Error handling doesn't crash the program
- [ ] Tested with actual credentials
- [ ] Tested with at least 3 different courses
- [ ] Deadline parsing handles your LMS's date format

---

## 📚 Further Reading

- **[YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md)** - Detailed pattern explanations
- **[ARCHITECTURE_COMPARISON.md](ARCHITECTURE_COMPARISON.md)** - yontil-main vs Python comparison
- **[yontil-main source code](yontil-main/)** - Original reference implementation

---

**Need help?** Check the main [README.md](README.md) or create an issue!


