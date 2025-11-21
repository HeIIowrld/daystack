# Yontil-Main Integration Guide

This document explains how patterns from **yontil-main** (Yonsei LearnUs Chrome Extension) were adapted for the Coursemos LMS crawler.

## 📚 Reference Project: yontil-main

**yontil-main** is a Chrome extension for Yonsei University's LearnUs LMS that:
- Handles multi-step SSO authentication
- Fetches and displays incomplete course assignments
- Manages session refresh automatically

### Key Components Referenced

1. **Login System** (`yontil-main/src/core/login/`)
2. **Task Fetching** (`yontil-main/src/core/tasks/`)
3. **HTML Parsing** (`yontil-main/src/utils/parse-html-string.ts`)

---

## 🔐 Pattern 1: Multi-Step Login Flow

### yontil-main Implementation

```typescript
// yontil-main/src/core/login/login-learnus.ts
export default async function loginLearnUs(
  id: string,
  password: string
): Promise<void> {
  const data1 = await fetch1()      // Get initial tokens
  const data2 = await fetch2(data1) // Get SSO challenge
  const data4 = await fetch3(data2, id, password) // Authenticate
  await fetch4(data4)               // Process callback
  await fetch5()                    // Finalize session
}
```

**Key Patterns:**
- ✅ Multi-step authentication flow
- ✅ Token/challenge extraction at each step
- ✅ Hidden form field parsing
- ✅ Session cookie management

### Coursemos Adaptation

```python
# coursemos_crawler.py
def _login_requests(self):
    """
    Login using requests library
    Implements multi-step login flow similar to yontil-main
    """
    # Step 1: Get login page and extract CSRF tokens
    response = self.session.get(self.LOGIN_URL, timeout=10)
    hidden_fields = self.parse_input_tags_from_html(response.text)
    
    # Step 2: Submit login credentials with hidden fields
    login_data = {
        'username': self.username,
        'password': self.password,
        **hidden_fields  # Include CSRF tokens (yontil-main pattern)
    }
    
    response = self.session.post(
        self.LOGIN_URL,
        data=login_data,
        allow_redirects=True
    )
    
    # Step 3: Verify login success
    return self._check_login_success(response)
```

**Adaptations:**
- ✅ Simplified to 2-3 steps (Coursemos may not need complex SSO)
- ✅ Uses `requests.Session()` for cookie persistence
- ✅ Maintains pattern of extracting hidden fields
- ✅ Added login verification step

---

## 🧩 Pattern 2: HTML Parsing for Hidden Fields

### yontil-main Implementation

```typescript
// yontil-main/src/utils/parse-html-string.ts
export function parseInputTagsFromHtml(
  htmlString: string
): Record<string, string> {
  const inputRegex =
    /<input[^>]*\sid=["']([^"']*)["'][^>]*\svalue=["']([^"']*)["'][^>]*>/gi

  const inputAttributes: Record<string, string> = {}
  let match: RegExpExecArray | null

  while ((match = inputRegex.exec(htmlString)) !== null) {
    const id = match[1]
    const value = match[2]
    inputAttributes[id] = value
  }

  return inputAttributes
}
```

**Purpose:**
- Extract CSRF tokens, session IDs, and other hidden form fields
- Critical for bypassing anti-CSRF protections

### Coursemos Adaptation

```python
# coursemos_crawler.py
def parse_input_tags_from_html(self, html_string: str) -> Dict[str, str]:
    """
    Parse HTML to extract input tag id-value pairs
    Based on: yontil-main/src/utils/parse-html-string.ts
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    input_attributes = {}
    
    for input_tag in soup.find_all('input', id=True):
        input_id = input_tag.get('id')
        input_value = input_tag.get('value', '')
        if input_id:
            input_attributes[input_id] = input_value
    
    return input_attributes
```

**Adaptations:**
- ✅ Uses BeautifulSoup instead of regex (more Pythonic)
- ✅ Same logic: extract id-value pairs from input tags
- ✅ Returns same data structure (dict/Record)

---

## 📝 Pattern 3: Task/Assignment Fetching

### yontil-main Implementation

```typescript
// yontil-main/src/core/tasks/fetch-tasks.ts
export default async function fetchTasks(): Promise<TasksCourse[]> {
  // Step 1: Get course list from main page
  const courseElements = document.querySelectorAll('.my-course-lists li')
  const tasksCourses: TasksCourse[] = []

  // Step 2: For each course, fetch its tasks
  for (const courseElement of courseElements) {
    const courseLinkElement = courseElement.querySelector('.course-link')
    const courseUrl = courseLinkElement.href
    const taskElements = await fetchTaskElementsInCourse(courseUrl)

    tasksCourses.push({ url: courseUrl, taskElements })
  }

  return tasksCourses
}

async function fetchTaskElementsInCourse(
  courseUrl: string
): Promise<Element[]> {
  const response = await fetch(courseUrl)
  const html = await response.text()
  const document = parser.parseFromString(html, 'text/html')

  // Find incomplete tasks
  const fixedTasks = document.querySelectorAll(
    '.course-box-top .activity:has(img[src$="completion-auto-n"])'
  )
  const weekTasks = document.querySelectorAll(
    '.total-sections .activity:has(img[src$="completion-auto-n"])'
  )

  return [...fixedTasks, ...weekTasks]
}
```

**Key Patterns:**
- ✅ Two-level traversal: courses → tasks within course
- ✅ CSS selector-based element finding
- ✅ Filter for incomplete tasks only
- ✅ Return structured data

### Coursemos Adaptation

```python
# coursemos_crawler.py
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
    
    return assignments

def _fetch_tasks_in_course(self, course_url: str, course_name: str) -> List[Dict]:
    """
    Fetch tasks/assignments within a specific course
    Similar to: yontil-main fetchTaskElementsInCourse
    """
    tasks = []
    
    response = self.session.get(course_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find incomplete tasks (adjust selectors to match Coursemos)
    task_elements = soup.select(
        '.activity:not(.completed), '
        '.assignment:not(.submitted), '
        '.task-item:not(.done)'
    )
    
    for task_elem in task_elements:
        title_elem = task_elem.select_one('.activity-title, .assignment-title')
        deadline_elem = task_elem.select_one('.deadline, .due-date')
        
        if title_elem:
            tasks.append({
                "task": title_elem.get_text(strip=True),
                "course": course_name,
                "deadline": self._parse_deadline(deadline_elem.get_text() if deadline_elem else None),
                "estimated_time": self.estimate_task_time(title_elem.get_text()),
                "url": course_url
            })
    
    return tasks
```

**Adaptations:**
- ✅ Same two-level structure: courses → tasks
- ✅ Uses BeautifulSoup `.select()` (equivalent to `querySelectorAll`)
- ✅ Filters incomplete tasks with `:not()` pseudo-class
- ✅ Extracts title, deadline, and metadata

---

## 🔄 Pattern 4: Session Management

### yontil-main Implementation

```typescript
// yontil-main/src/core/login/refresh-session.ts
export async function refreshSession(): Promise<void> {
  const loginData = await getLoginData()
  
  let tryCount = 1
  const MAX_TRIES = 3

  while (tryCount <= MAX_TRIES) {
    try {
      const isSessionAlive = await checkIfSessionAlive()

      if (!isSessionAlive) {
        await loginLearnUs(loginData.id, loginData.password)
        await loginPortal()
      }

      break
    } catch (e) {
      if (tryCount === MAX_TRIES) {
        console.log('Max tries reached, giving up.')
      }
      tryCount++
    }
  }
}
```

**Key Patterns:**
- ✅ Retry logic with max attempts
- ✅ Session validity checking
- ✅ Auto re-login on session expiry

### Coursemos Adaptation

```python
# coursemos_crawler.py (can be added)
def ensure_logged_in(self):
    """
    Ensure session is active, re-login if necessary
    Based on: yontil-main refresh-session.ts
    """
    MAX_TRIES = 3
    
    for attempt in range(1, MAX_TRIES + 1):
        try:
            if self._check_session_alive():
                return True
            
            # Session expired, re-login
            print(f"⚠️  Session expired, re-logging in (attempt {attempt}/{MAX_TRIES})...")
            if self.login():
                return True
                
        except Exception as e:
            print(f"❌ Login attempt {attempt} failed: {e}")
            if attempt == MAX_TRIES:
                print("Max retries reached, giving up.")
                return False
    
    return False

def _check_session_alive(self) -> bool:
    """Check if current session is still valid"""
    try:
        response = self.session.get(self.MAIN_PAGE_URL, timeout=5)
        # If redirected to login page, session is dead
        return 'login' not in response.url
    except:
        return False
```

---

## 🎯 Key Takeaways

### What We Learned from yontil-main

1. **Multi-Step Auth is Common**
   - Modern LMS systems use CSRF protection and SSO
   - Always extract hidden form fields

2. **CSS Selectors are Your Friend**
   - Use specific selectors to find incomplete tasks
   - `:not()`, `:has()` pseudo-classes are powerful

3. **Session Management Matters**
   - Sessions expire; implement retry logic
   - Check session validity before making requests

4. **Structure Matters**
   - Separate concerns: login, fetch, parse
   - Make functions reusable and testable

### Differences: TypeScript (yontil-main) vs Python (Coursemos)

| Feature | yontil-main (TypeScript) | coursemos_crawler.py (Python) |
|---------|-------------------------|-------------------------------|
| HTTP Client | `fetch()` API | `requests.Session()` |
| HTML Parsing | `DOMParser` / regex | `BeautifulSoup` |
| Selectors | `querySelectorAll()` | `.select()` / `.select_one()` |
| Async | `async`/`await` | Synchronous (can add `aiohttp`) |
| Error Handling | Try-catch | Try-except |
| Context | Browser extension | Standalone script |

---

## 🚀 Usage Examples

### Basic Usage

```python
from coursemos_crawler import CoursemosCrawler

# Create crawler instance
crawler = CoursemosCrawler(
    username="your_username",
    password="your_password",
    use_selenium=False  # Use requests (faster)
)

# Login and fetch assignments
if crawler.login():
    assignments = crawler.fetch_assignments()
    
    for assignment in assignments:
        print(f"📝 {assignment['task']}")
        print(f"   Course: {assignment['course']}")
        print(f"   Deadline: {assignment['deadline']}")
        print(f"   Estimated: {assignment['estimated_time']} min")

crawler.logout()
```

### With Context Manager

```python
with CoursemosCrawler(username="user", password="pass") as crawler:
    assignments = crawler.fetch_assignments()
    # Auto cleanup on exit
```

### Integration with Scheduler

```python
from coursemos_crawler import CoursemosCrawler
from scheduler import allocate_tasks, print_schedule

# Fetch assignments from Coursemos
crawler = CoursemosCrawler(username="user", password="pass")
assignments = crawler.fetch_assignments()

# Convert to scheduler format
todos = [
    {
        "task": a['task'],
        "estimated_time": a['estimated_time']
    }
    for a in assignments
]

# Optimize schedule
schedule = get_my_schedule()  # Your daily schedule
optimized = allocate_tasks(schedule, todos)
print_schedule(optimized)
```

---

## 🔧 Customization Guide

### 1. Update URLs for Your LMS

```python
class CoursemosCrawler:
    COURSEMOS_ORIGIN = "https://your-lms-domain.com"
    LOGIN_URL = f"{COURSEMOS_ORIGIN}/login"
    MAIN_PAGE_URL = f"{COURSEMOS_ORIGIN}/dashboard"
```

### 2. Update CSS Selectors

Inspect your LMS's HTML structure and update selectors:

```python
# Course list selectors
course_elements = soup.select('.your-course-class li')

# Task selectors  
task_elements = soup.select('.your-task-class:not(.completed)')

# Title/deadline selectors
title = task_elem.select_one('.your-title-class')
deadline = task_elem.select_one('.your-deadline-class')
```

### 3. Add Custom Login Steps

If your LMS requires additional authentication steps:

```python
def _login_requests(self):
    # Step 1: Get login page
    response = self.session.get(self.LOGIN_URL)
    
    # Step 2: Extract tokens
    hidden_fields = self.parse_input_tags_from_html(response.text)
    
    # Step 3: Your custom step (e.g., 2FA)
    two_fa_code = input("Enter 2FA code: ")
    
    # Step 4: Submit with all data
    login_data = {
        'username': self.username,
        'password': self.password,
        'two_fa': two_fa_code,
        **hidden_fields
    }
    
    return self.session.post(self.LOGIN_URL, data=login_data)
```

---

## 📊 Comparison Chart

### Authentication Flow

```
yontil-main (LearnUs):
User Input → fetch1 (Get S1) → fetch2 (Get Challenge) → 
fetch3 (RSA Encrypt + Auth) → fetch4 (Callback) → fetch5 (Finalize) → Success

coursemos_crawler:
User Input → Get Login Page → Extract CSRF → 
Submit Login + CSRF → Verify Success → Done
```

### Task Fetching Flow

```
Both follow same pattern:
Main Page → Get Course List → For Each Course → 
Visit Course Page → Extract Incomplete Tasks → Aggregate Results
```

---

## 🎓 Learning Resources

To understand the yontil-main patterns better:

1. **Read the source:**
   - `yontil-main/src/core/login/login-learnus.ts`
   - `yontil-main/src/core/tasks/fetch-tasks.ts`
   - `yontil-main/src/utils/parse-html-string.ts`

2. **Key concepts:**
   - SSO (Single Sign-On) flows
   - CSRF token handling
   - DOM manipulation and querying
   - Session cookie management

3. **Tools to inspect your LMS:**
   - Chrome DevTools (Network tab)
   - Inspector to find CSS selectors
   - Console to test selectors

---

## ✅ Validation Checklist

Before deploying your Coursemos crawler:

- [ ] URLs updated to match your LMS
- [ ] CSS selectors tested and validated
- [ ] Login flow tested with real credentials
- [ ] Task fetching returns actual data
- [ ] Deadline parsing handles your LMS's format
- [ ] Session management works (test with expired session)
- [ ] Error handling covers edge cases
- [ ] Logout properly cleans up resources

---

**Last Updated:** Based on yontil-main patterns as of November 2024

**Maintained By:** YCC Scheduler Project

