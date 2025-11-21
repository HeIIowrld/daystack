# Architecture Comparison: yontil-main vs YCC Scheduler

This document provides a visual comparison between the yontil-main Chrome extension architecture and our YCC Scheduler implementation.

## 🏗️ System Architecture Comparison

### yontil-main (Chrome Extension)

```
┌─────────────────────────────────────────────────────────────┐
│                     Chrome Extension                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Background │  │   Content    │  │    Popup     │       │
│  │   Script    │◄─┤   Scripts    │  │      UI      │       │
│  └──────┬──────┘  └──────┬───────┘  └──────────────┘       │
│         │                 │                                   │
│         │                 │                                   │
│  ┌──────▼─────────────────▼───────┐                          │
│  │      Chrome Storage API        │                          │
│  │  (Login Data, Tasks, Session)  │                          │
│  └────────────────────────────────┘                          │
│                                                               │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    │ fetch() API
                    │
        ┌───────────▼──────────────┐
        │   Yonsei University LMS   │
        ├───────────────────────────┤
        │  • ys.learnus.org         │
        │  • portal.yonsei.ac.kr    │
        │  • infra.yonsei.ac.kr     │
        └───────────────────────────┘
```

### YCC Scheduler (Python Application)

```
┌─────────────────────────────────────────────────────────────┐
│                  YCC Scheduler (Python)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   main.py   │  │  scheduler   │  │  directions  │       │
│  │    (CLI)    │─►│    .py       │─►│     .py      │       │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │               │
│         │                 │                  │               │
│  ┌──────▼─────────────────▼──────────────────▼───────┐      │
│  │            config.py (Environment)                 │      │
│  │         (API Keys, Settings, Aliases)              │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────┐        │
│  │        coursemos_crawler.py                      │        │
│  │  (Adapted from yontil-main patterns)             │        │
│  │  • requests.Session() instead of fetch()         │        │
│  │  • BeautifulSoup instead of DOMParser            │        │
│  └──────────────────┬───────────────────────────────┘        │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
         ┌────────────┴─────────────┐
         │                          │
         │                          │
┌────────▼────────┐      ┌─────────▼──────────┐
│  Coursemos LMS  │      │  Naver Cloud APIs  │
│                 │      │  • Geocoding       │
│  • Assignments  │      │  • Directions 5    │
│  • Deadlines    │      │  • Maps            │
└─────────────────┘      └────────────────────┘
```

## 🔄 Login Flow Comparison

### yontil-main: Multi-Step SSO Login

```
User Credentials
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│              login-learnus.ts                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: fetch1()                                        │
│  GET /passni/sso/spLogin2.php                           │
│  Extract: S1 token                                       │
│          │                                               │
│          ▼                                               │
│  Step 2: fetch2()                                        │
│  POST /sso/PmSSOService                                 │
│  Extract: ssoChallenge, RSA public key                  │
│          │                                               │
│          ▼                                               │
│  Step 3: fetch3()                                        │
│  POST /sso/PmSSOAuthService                             │
│  Send: RSA-encrypted credentials                        │
│  Extract: E3, E4, S2, CLTID                             │
│          │                                               │
│          ▼                                               │
│  Step 4: fetch4()                                        │
│  POST /passni/sso/spLoginData.php                       │
│  Send: E3, E4, S2, CLTID                                │
│          │                                               │
│          ▼                                               │
│  Step 5: fetch5()                                        │
│  GET /passni/spLoginProcess.php                         │
│  Finalize session                                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
      │
      ▼
✅ Logged In (Session cookies set)
```

### YCC Scheduler: Simplified Login

```
User Credentials
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│           coursemos_crawler.py                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Get Login Page                                 │
│  GET /login                                             │
│  Parse: CSRF tokens, hidden fields                      │
│          │                                               │
│          ▼                                               │
│  Step 2: Submit Login                                    │
│  POST /login                                            │
│  Send: {                                                │
│    username,                                            │
│    password,                                            │
│    ...csrf_tokens  ← yontil-main pattern!              │
│  }                                                      │
│          │                                               │
│          ▼                                               │
│  Step 3: Verify Success                                  │
│  Check: redirect to /main or /dashboard                │
│  No error messages present                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
      │
      ▼
✅ Logged In (Session cookies in requests.Session)
```

**Key Difference:** 
- yontil-main: Complex SSO with RSA encryption (5 steps)
- YCC Scheduler: Simplified form-based auth (2-3 steps)
- **Common Pattern:** Both extract and include hidden form fields!

## 📝 Task Fetching Flow Comparison

### Both Systems Use Same Pattern!

```
                    ┌──────────────────────┐
                    │   Get Main/Home Page │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Parse Course List   │
                    │  • .my-course-lists  │
                    │  • .course-item      │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │  For each course:       │
                  └────────────┬────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Visit Course Page   │
                    │  GET /course/{id}    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Find Incomplete     │
                    │  Tasks/Assignments   │
                    │  CSS: :not(.done)    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Extract Metadata    │
                    │  • Title             │
                    │  • Deadline          │
                    │  • Course name       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Aggregate Results   │
                    │  Return task list    │
                    └──────────────────────┘
```

### Code Side-by-Side

#### yontil-main (TypeScript)
```typescript
// Outer loop: iterate courses
const courseElements = document.querySelectorAll('.my-course-lists li')

for (const courseElement of courseElements) {
  const courseLinkElement = courseElement.querySelector('.course-link')
  const courseUrl = courseLinkElement.href
  
  // Inner: fetch tasks in this course
  const taskElements = await fetchTaskElementsInCourse(courseUrl)
  
  tasksCourses.push({ url: courseUrl, taskElements })
}

// Inner function
async function fetchTaskElementsInCourse(courseUrl: string) {
  const html = await response.text()
  const document = parser.parseFromString(html, 'text/html')
  
  // Find incomplete tasks
  return document.querySelectorAll(
    '.activity:has(img[src$="completion-auto-n"])'
  )
}
```

#### YCC Scheduler (Python)
```python
# Outer loop: iterate courses
course_elements = soup.select('.my-course-lists li')

for course_elem in course_elements:
    course_link = course_elem.select_one('.course-link')
    course_url = course_link.get('href')
    
    # Inner: fetch tasks in this course
    course_tasks = self._fetch_tasks_in_course(course_url, course_name)
    
    assignments.extend(course_tasks)

# Inner function
def _fetch_tasks_in_course(self, course_url: str):
    response = self.session.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find incomplete tasks
    return soup.select('.activity:not(.completed)')
```

**🎯 Same Logic, Different Language!**

## 🛠️ Technical Stack Comparison

| Feature | yontil-main | YCC Scheduler |
|---------|-------------|---------------|
| **Language** | TypeScript | Python 3.8+ |
| **Runtime** | Chrome Extension | Standalone CLI |
| **HTTP Client** | `fetch()` API | `requests` library |
| **HTML Parsing** | `DOMParser`, regex | `BeautifulSoup4` |
| **CSS Selectors** | `querySelector()` | `.select()` / `.select_one()` |
| **Storage** | Chrome Storage API | Environment variables (.env) |
| **Async** | async/await | Synchronous (optional: aiohttp) |
| **UI** | Chrome popup/overlay | Terminal CLI |
| **Session** | Browser cookies | `requests.Session()` |
| **Scheduling** | Chrome alarms | N/A (run on-demand) |

## 🔐 Security Comparison

### yontil-main

```
✅ Chrome extension sandboxing
✅ Credentials stored in Chrome Storage (encrypted by Chrome)
✅ HTTPS enforced by browser
✅ Content Security Policy
✅ No credential exposure to websites
⚠️  Must trust Chrome's security model
```

### YCC Scheduler

```
✅ Credentials in .env file (user-controlled)
✅ .gitignore prevents accidental commits
✅ HTTPS enforced by requests library
✅ No third-party storage
⚠️  User responsible for .env security
⚠️  No built-in encryption (add keyring if needed)
```

## 📊 Data Flow Comparison

### yontil-main: Real-time Monitoring

```
User Opens Chrome
      │
      ▼
Extension Loads
      │
      ├──► Background Script (always running)
      │         │
      │         ├──► Alarm: Refresh session every 30min
      │         │
      │         └──► Alarm: Fetch tasks every 1 hour
      │
      ├──► Content Script (on LearnUs pages)
      │         │
      │         └──► Inject UI elements (task counter)
      │
      └──► Popup (when clicked)
                │
                └──► Display cached tasks from storage
```

### YCC Scheduler: On-Demand Execution

```
User Runs: python main.py
      │
      ▼
Load Config (.env)
      │
      ▼
Choose Mode (Crawler / Manual)
      │
      ├──► Crawler Mode
      │         │
      │         ├──► Login to Coursemos
      │         ├──► Fetch assignments
      │         └──► Convert to tasks
      │
      └──► Manual Mode
                │
                └──► User inputs tasks
      │
      ▼
Fetch Today's Schedule (hardcoded/DB)
      │
      ▼
For each schedule gap:
      │
      ├──► Geocode addresses (Naver API)
      ├──► Calculate travel time (Naver API)
      ├──► Calculate free time
      └──► Allocate tasks
      │
      ▼
Print Optimized Schedule
      │
      ▼
Exit
```

## 🎯 Key Architectural Lessons from yontil-main

### 1. **Separation of Concerns** ✅

```
yontil-main structure:
core/
├── login/              # Authentication logic
├── tasks/              # Task fetching logic
└── alarm.ts            # Scheduling logic

YCC Scheduler (adopted):
├── config.py           # Configuration
├── geocoding.py        # Address conversion
├── directions.py       # Travel time
├── scheduler.py        # Optimization logic
└── coursemos_crawler.py # LMS integration
```

### 2. **Reusable Utilities** ✅

```typescript
// yontil-main
export function parseInputTagsFromHtml(html: string) { ... }
```

```python
# YCC Scheduler (adopted)
def parse_input_tags_from_html(self, html_string: str) -> Dict { ... }
```

### 3. **Error Handling with Retries** ✅

```typescript
// yontil-main
let tryCount = 1
const MAX_TRIES = 3

while (tryCount <= MAX_TRIES) {
  try {
    await refreshSession()
    break
  } catch (e) {
    if (tryCount === MAX_TRIES) {
      console.log('Giving up')
    }
    tryCount++
  }
}
```

**Adoption recommended** for production YCC Scheduler!

### 4. **Session Validation** ✅

```typescript
// yontil-main
async function checkIfSessionAlive(): Promise<boolean> {
  const response = await fetch(LEARNUS_ORIGIN)
  return !response.url.includes('login')
}
```

```python
# YCC Scheduler (can add)
def _check_session_alive(self) -> bool:
    response = self.session.get(self.MAIN_PAGE_URL)
    return 'login' not in response.url
```

## 🚀 Performance Comparison

| Metric | yontil-main | YCC Scheduler |
|--------|-------------|---------------|
| **Startup Time** | <100ms (extension load) | ~1-2s (Python imports) |
| **Login Time** | 2-3s (5-step SSO) | 1-2s (simplified auth) |
| **Task Fetch Time** | 5-10s (10 courses) | 5-10s (similar) |
| **Memory Usage** | ~50MB (Chrome ext) | ~30-50MB (Python) |
| **CPU Usage** | Minimal (async) | Minimal (sync) |
| **Background Running** | Yes (always on) | No (on-demand) |

## 📈 Scalability Comparison

### yontil-main
- **Users:** One per Chrome profile
- **Concurrent:** N/A (single user)
- **Storage:** Chrome Storage (~5MB limit)
- **Rate Limits:** Browser enforced

### YCC Scheduler
- **Users:** One per execution (or multi-user with DB)
- **Concurrent:** Can run multiple instances
- **Storage:** Unlimited (file system / DB)
- **Rate Limits:** Naver API limits (300만 calls/month)

## 🎓 What We Can Still Learn from yontil-main

### Features to Adopt:

1. **Auto Session Refresh**
   ```typescript
   // yontil-main has automatic session refresh
   // YCC Scheduler: Add cron job or background task
   ```

2. **Cache Management**
   ```typescript
   // yontil-main caches tasks to reduce API calls
   // YCC Scheduler: Add Redis or file cache
   ```

3. **Network Status Handling**
   ```typescript
   // yontil-main checks network before API calls
   // YCC Scheduler: Add connection checks
   ```

4. **Graceful Degradation**
   ```typescript
   // yontil-main falls back gracefully on errors
   // YCC Scheduler: Already does this (mock data fallback)
   ```

## 📚 Summary

| Aspect | yontil-main | YCC Scheduler |
|--------|-------------|---------------|
| **Purpose** | Monitor LearnUs tasks | Optimize schedule with travel time |
| **Platform** | Browser extension | CLI application |
| **Complexity** | High (SSO, RSA) | Medium (form auth) |
| **Patterns Used** | ✅ Multi-step auth<br>✅ HTML parsing<br>✅ Task fetching<br>✅ Session refresh | ✅ Multi-step auth (simplified)<br>✅ HTML parsing<br>✅ Task fetching<br>⚠️ Session refresh (TODO) |
| **Added Features** | - | ✅ Geocoding<br>✅ Travel time calc<br>✅ Schedule optimization |

---

**Conclusion:** YCC Scheduler successfully adapts yontil-main's robust patterns while adding unique scheduling features!


