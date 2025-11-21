# Coursemos 크롤러 통합 가이드

이 가이드는 `coursemos_crawler.py`를 실제 Coursemos LMS와 통합하는 방법을 설명합니다.

## 📋 개요

`coursemos_crawler.py`는 **yontil-main** 프로젝트의 Learnus 로그인 및 과제 수집 패턴을 기반으로 작성되었습니다.

### 참조한 코드
- `yontil-main/src/core/login/login-learnus.ts` - 다단계 로그인 인증
- `yontil-main/src/core/login/login-portal.ts` - 포털 로그인 패턴
- `yontil-main/src/core/tasks/fetch-tasks.ts` - 과제 목록 수집
- `yontil-main/src/utils/parse-html-string.ts` - HTML 파싱 유틸리티

## 🔧 구현 방법

### 1단계: Coursemos URL 확인

실제 Coursemos 사이트의 URL을 확인하고 `coursemos_crawler.py`의 상수를 업데이트하세요:

```python
class CoursemosCrawler:
    # 실제 Coursemos URL로 변경
    COURSEMOS_ORIGIN = "https://your-coursemos-domain.com"
    LOGIN_URL = f"{COURSEMOS_ORIGIN}/login"  # 실제 로그인 페이지 경로
    MAIN_PAGE_URL = f"{COURSEMOS_ORIGIN}/main"  # 메인 대시보드 경로
```

### 2단계: 로그인 프로세스 분석

#### 방법 A: 브라우저 개발자 도구 사용

1. **Chrome/Edge 개발자 도구 열기** (F12)
2. **Network 탭** 선택
3. Coursemos에 **로그인 시도**
4. **HTTP 요청 분석**:
   - POST 요청 URL 확인
   - 요청 Body (Form Data) 확인
   - 필요한 헤더 확인
   - 쿠키/세션 처리 방식 확인

#### 예시: 로그인 요청 분석

```
POST https://coursemos.co.kr/auth/login
Content-Type: application/x-www-form-urlencoded

username=myuser&password=mypass&csrf_token=abc123&remember=false
```

#### 방법 B: yontil-main 패턴 적용

Learnus처럼 다단계 인증이 필요한 경우:

```python
def _login_requests(self):
    # Step 1: 로그인 페이지에서 토큰 가져오기
    response = self.session.get(self.LOGIN_URL)
    tokens = self.parse_input_tags_from_html(response.text)
    
    # Step 2: 인증 서버로 요청
    auth_response = self.session.post(
        "https://auth-server.com/authenticate",
        data={
            'username': self.username,
            'password': self.password,
            'csrf_token': tokens.get('csrf_token'),
            # 기타 필요한 필드
        }
    )
    
    # Step 3: 콜백 처리
    callback_data = self.parse_input_tags_from_html(auth_response.text)
    
    # Step 4: 최종 로그인
    final_response = self.session.post(
        self.LOGIN_URL,
        data=callback_data
    )
    
    return self._check_login_success(final_response)
```

### 3단계: HTML 셀렉터 업데이트

Coursemos의 실제 HTML 구조에 맞게 CSS 셀렉터를 수정하세요.

#### 과제 목록 페이지 분석

1. **브라우저에서 Coursemos 열기**
2. **개발자 도구의 Elements 탭**에서 구조 확인
3. **과제 항목의 클래스명/ID** 찾기

#### 예시: 셀렉터 업데이트

```python
def _fetch_assignments_requests(self):
    response = self.session.get(self.MAIN_PAGE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # ⚠️ 실제 Coursemos HTML 구조에 맞게 수정 필요
    course_elements = soup.select('.course-card')  # 실제 클래스명으로 변경
    
    for course_elem in course_elements:
        # 실제 셀렉터로 변경
        course_link = course_elem.select_one('a.course-title')
        course_name = course_link.get_text(strip=True)
        # ...
```

#### 일반적인 HTML 패턴

```html
<!-- 예시 1: 카드 형태 -->
<div class="course-card">
    <a href="/course/123" class="course-link">데이터베이스</a>
    <div class="assignments">
        <div class="assignment-item incomplete">
            <span class="title">과제 #3</span>
            <span class="deadline">2024-12-25 23:59</span>
        </div>
    </div>
</div>

<!-- 예시 2: 리스트 형태 -->
<ul class="my-courses">
    <li>
        <a href="/course/123">데이터베이스</a>
        <span class="badge">2</span> <!-- 미완료 과제 수 -->
    </li>
</ul>
```

#### 셀렉터 매핑

| 요소 | 예시 셀렉터 | 실제로 확인 필요 |
|------|------------|----------------|
| 과목 목록 | `.course-list li`, `.my-courses .course` | ✅ |
| 과목 링크 | `a.course-link`, `.course-title` | ✅ |
| 과제 항목 | `.assignment-item`, `.task` | ✅ |
| 과제 제목 | `.assignment-title`, `.task-name` | ✅ |
| 마감일 | `.deadline`, `.due-date` | ✅ |
| 미완료 표시 | `:not(.completed)`, `.incomplete` | ✅ |

### 4단계: 과제 상세 정보 수집

각 과제에서 더 많은 정보를 수집하려면:

```python
def _fetch_tasks_in_course(self, course_url: str, course_name: str):
    response = self.session.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    tasks = []
    task_elements = soup.select('.assignment-item:not(.submitted)')
    
    for task_elem in task_elements:
        # 기본 정보
        title = task_elem.select_one('.title').get_text(strip=True)
        
        # 마감일
        deadline_elem = task_elem.select_one('.deadline')
        deadline = self._parse_deadline(deadline_elem.get_text() if deadline_elem else None)
        
        # 추가 정보 (선택사항)
        description_elem = task_elem.select_one('.description')
        points_elem = task_elem.select_one('.points')
        
        task_data = {
            "task": title,
            "course": course_name,
            "deadline": deadline,
            "estimated_time": self.estimate_task_time(title),
            "url": course_url,
        }
        
        # 선택적 필드 추가
        if description_elem:
            task_data["description"] = description_elem.get_text(strip=True)
        if points_elem:
            task_data["points"] = points_elem.get_text(strip=True)
        
        tasks.append(task_data)
    
    return tasks
```

### 5단계: Selenium 모드 (JavaScript 페이지용)

Coursemos가 JavaScript를 많이 사용하는 경우 Selenium을 사용하세요.

#### Selenium 설치

```bash
pip install selenium webdriver-manager
```

#### Chrome Driver 자동 설정

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def _login_selenium(self):
    # 자동으로 ChromeDriver 다운로드 및 설정
    service = Service(ChromeDriverManager().install())
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 백그라운드 실행
    
    self.driver = webdriver.Chrome(service=service, options=options)
    self.driver.get(self.LOGIN_URL)
    
    # 나머지 로그인 로직...
```

#### 동적 컨텐츠 대기

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 요소가 로드될 때까지 대기
wait = WebDriverWait(self.driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "assignment-list"))
)
```

## 🧪 테스트 방법

### 단계별 테스트

#### 1. HTML 파싱 테스트

```python
python coursemos_crawler.py
# HTML parsing test가 성공하는지 확인
```

#### 2. 로그인 테스트 (Mock)

```python
crawler = CoursemosCrawler(username="test", password="test")
result = crawler.login()
print(f"Login result: {result}")
```

#### 3. 실제 로그인 테스트

```python
# .env 파일 또는 환경변수에 실제 계정 정보 설정
crawler = CoursemosCrawler(
    username="your_actual_username",
    password="your_actual_password"
)
result = crawler.login()
```

#### 4. 과제 수집 테스트

```python
crawler = CoursemosCrawler(username="user", password="pass")
assignments = crawler.fetch_assignments()

print(f"Found {len(assignments)} assignments")
for assignment in assignments:
    print(f"- {assignment['course']}: {assignment['task']}")
```

### 디버깅 팁

#### 1. HTTP 요청/응답 로깅

```python
import logging

# requests 라이브러리의 HTTP 트래픽 로깅
logging.basicConfig(level=logging.DEBUG)
```

#### 2. HTML 응답 저장

```python
def _login_requests(self):
    response = self.session.get(self.LOGIN_URL)
    
    # 디버깅: HTML 저장
    with open('debug_login_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    # 파싱 계속...
```

#### 3. Selenium 스크린샷

```python
def _login_selenium(self):
    self.driver.get(self.LOGIN_URL)
    
    # 디버깅: 스크린샷 저장
    self.driver.save_screenshot('debug_login_page.png')
    
    # 로그인 계속...
```

## 📝 환경 설정

### .env 파일 설정

```env
# Naver API (이미 설정됨)
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret

# Coursemos 계정 (새로 추가)
COURSEMOS_USERNAME=your_username
COURSEMOS_PASSWORD=your_password
COURSEMOS_USE_SELENIUM=false
```

### config.py 업데이트

```python
class Config:
    # ... 기존 설정 ...
    
    # Coursemos credentials
    COURSEMOS_USERNAME = os.getenv('COURSEMOS_USERNAME')
    COURSEMOS_PASSWORD = os.getenv('COURSEMOS_PASSWORD')
    COURSEMOS_USE_SELENIUM = os.getenv('COURSEMOS_USE_SELENIUM', 'false').lower() == 'true'
```

### main.py에서 사용

```python
from config import Config
from coursemos_crawler import CoursemosCrawler

def run_with_crawler():
    Config.validate()
    
    crawler = CoursemosCrawler(
        username=Config.COURSEMOS_USERNAME,
        password=Config.COURSEMOS_PASSWORD,
        use_selenium=Config.COURSEMOS_USE_SELENIUM
    )
    
    assignments = crawler.fetch_assignments()
    crawler.logout()
    
    return assignments
```

## ⚠️ 주의사항

### 1. 보안

- **절대로** 계정 정보를 코드에 하드코딩하지 마세요
- `.env` 파일을 `.gitignore`에 추가하세요
- 가능하면 2단계 인증이 없는 테스트 계정을 사용하세요

### 2. 웹사이트 이용 약관

- Coursemos의 이용 약관을 확인하세요
- 크롤링이 허용되는지 확인하세요
- API가 제공된다면 API 사용을 우선하세요

### 3. Rate Limiting

- 요청 사이에 적절한 지연 추가:

```python
import time

for course in courses:
    assignments = fetch_tasks(course)
    time.sleep(1)  # 1초 대기
```

### 4. 에러 핸들링

```python
def fetch_assignments(self):
    try:
        # 크롤링 로직
        pass
    except requests.exceptions.Timeout:
        print("⚠️  Timeout - 서버 응답 없음")
        return []
    except requests.exceptions.ConnectionError:
        print("⚠️  Connection error - 네트워크 확인")
        return []
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return []
```

## 🚀 실전 예제

### 완전한 통합 예제

```python
from config import Config
from coursemos_crawler import CoursemosCrawler
from scheduler import allocate_tasks, print_schedule

def main():
    # 1. 환경 설정 확인
    Config.validate()
    
    # 2. Coursemos에서 과제 가져오기
    print("📚 Coursemos에서 과제 수집 중...")
    
    with CoursemosCrawler(
        username=Config.COURSEMOS_USERNAME,
        password=Config.COURSEMOS_PASSWORD
    ) as crawler:
        assignments = crawler.fetch_assignments()
    
    # 3. 스케줄러 형식으로 변환
    todo_list = [
        {
            "task": assignment['task'],
            "estimated_time": assignment['estimated_time']
        }
        for assignment in assignments
    ]
    
    # 4. 일정 최적화
    schedule = get_current_schedule()  # 사용자의 일정
    optimized = allocate_tasks(schedule, todo_list)
    
    # 5. 결과 출력
    print_schedule(optimized)

if __name__ == "__main__":
    main()
```

## 📚 추가 리소스

### yontil-main 프로젝트 참조

- `yontil-main/src/core/login/` - 로그인 패턴
- `yontil-main/src/core/tasks/` - 과제 수집 패턴
- `yontil-main/src/utils/` - 유틸리티 함수들

### Python 라이브러리 문서

- [Requests](https://docs.python-requests.org/) - HTTP 요청
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML 파싱
- [Selenium](https://selenium-python.readthedocs.io/) - 브라우저 자동화

## 🤝 도움이 필요하신가요?

통합 과정에서 문제가 발생하면:

1. 디버깅 섹션의 팁을 활용하세요
2. HTML 구조를 다시 확인하세요
3. Selenium 모드를 시도해보세요
4. 이슈를 생성해주세요

---

**Made with reference to yontil-main project** 🙏

