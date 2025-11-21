# YCC 스케줄러 (YCC Scheduler)

이동 시간을 고려한 지능형 일정 자동 최적화 시스템

## 📋 프로젝트 개요

YCC 스케줄러는 Naver Maps API를 활용하여 실제 이동 시간을 계산하고, 일정 사이의 빈 시간에 할 일을 자동으로 배치하는 스마트 스케줄링 시스템입니다.

### 주요 기능

- ✅ **주소 자동 변환**: 텍스트 주소를 GPS 좌표로 변환 (Naver Geocoding API)
- ✅ **이동 시간 계산**: 두 지점 간 실제 이동 시간 산출 (Naver Directions 5 API)
- ✅ **자동 일정 최적화**: 이동 시간을 제외한 실제 가용 시간에 작업 자동 배치
- ✅ **안전 여유 시간**: 예상치 못한 지연을 위한 버퍼 타임 추가
- ✅ **Coursemos 크롤러**: LMS 과제 자동 수집 (yontil-main 패턴 기반)

## 🚀 시작하기

### 1. 사전 준비사항

#### Naver Cloud Platform API 키 발급

1. [Naver Cloud Platform](https://www.ncloud.com/) 회원가입
2. 콘솔에서 `AI·NAVER API > Application` 등록
3. 다음 API 활성화:
   - **Maps**: 지도 표시
   - **Geocoding**: 주소 → 좌표 변환
   - **Directions 5**: 길찾기 및 이동 시간 계산
4. `Client ID`와 `Client Secret` 발급받기

#### Python 환경

- Python 3.8 이상 권장
- pip 패키지 관리자

### 2. 설치

```bash
# 1. 저장소 클론 또는 다운로드
cd scheduler

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일을 생성하고 API 키를 입력하세요
```

### 3. 환경 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Naver Cloud Platform API Credentials
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here

# Optional: Add buffer time (in minutes) for travel calculations
TRAVEL_TIME_BUFFER=15
```

⚠️ **중요**: `.env` 파일은 절대 공개 저장소에 업로드하지 마세요!

### 4. 실행

```bash
# 메인 애플리케이션 실행
python main.py

# 빠른 테스트 (API 연결 확인)
python main.py --test
```

## 📚 Documentation

이 프로젝트는 포괄적인 문서를 제공합니다:

- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - 📖 모든 문서의 인덱스와 학습 경로

**빠른 링크:**
- 🚀 처음 사용: 이 README를 끝까지 읽으세요
- 🔧 크롤러 커스터마이징: [QUICKSTART_COURSEMOS.md](QUICKSTART_COURSEMOS.md)
- 🏗️ 아키텍처 이해: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- 🎯 yontil-main 패턴: [YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md)

## 📁 프로젝트 구조

```
scheduler/
│
├── main.py                          # 메인 애플리케이션
├── config.py                        # 설정 및 환경 변수 관리
├── geocoding.py                     # 주소 → 좌표 변환
├── directions.py                    # 이동 시간 계산
├── scheduler.py                     # 일정 최적화 로직
├── coursemos_crawler.py             # Coursemos LMS 크롤러 (yontil-main 기반)
│
├── requirements.txt                 # 필수 라이브러리 목록
├── example.env                      # 환경 변수 예시
├── .gitignore                       # Git 제외 파일 목록
├── README.md                        # 프로젝트 문서 (본 파일)
├── PRD.md                           # 제품 요구사항 명세서
│
├── YONTIL_INTEGRATION_GUIDE.md      # yontil-main 패턴 적용 가이드 ⭐
├── ARCHITECTURE_COMPARISON.md       # 아키텍처 상세 비교 ⭐
│
└── yontil-main/                     # 참조 프로젝트 (Learnus 크롤러)
    └── src/
        └── core/
            ├── login/               # 로그인 패턴 참조
            └── tasks/               # 과제 수집 패턴 참조
```

### 🔗 yontil-main 참조 프로젝트

이 프로젝트의 `coursemos_crawler.py`는 **yontil-main** (연세대학교 LearnUs LMS 크롬 확장 프로그램)의 검증된 로그인 및 과제 수집 패턴을 Python으로 적용했습니다.

**참조 문서:**
- **[QUICKSTART_COURSEMOS.md](QUICKSTART_COURSEMOS.md)** - Coursemos 크롤러 빠른 시작 가이드 ⭐ START HERE
- **[YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md)** - yontil-main 패턴을 어떻게 적용했는지 상세 설명
- **[ARCHITECTURE_COMPARISON.md](ARCHITECTURE_COMPARISON.md)** - TypeScript vs Python 구현 비교
- **[yontil-main 소스 코드](yontil-main/)** - 원본 참조 프로젝트

**주요 적용 패턴:**
- ✅ 다단계 로그인 플로우 (Multi-step authentication)
- ✅ HTML hidden field 파싱 (CSRF 토큰 추출)
- ✅ 코스별 과제 순회 수집 (Course → Tasks hierarchy)
- ✅ 미완료 과제 필터링 (`:not(.completed)` selector)
```

## 💻 사용 방법

### 기본 사용법

1. **프로그램 실행**
   ```bash
   python main.py
   ```

2. **모드 선택**
   - `1`: Coursemos 크롤러 사용 (현재는 샘플 데이터)
   - `2`: 수동으로 할 일 입력

3. **결과 확인**
   - 이동 시간을 고려한 최적화된 일정표 출력
   - 할당되지 않은 작업 목록 표시

### 개별 모듈 테스트

각 모듈은 독립적으로 실행하여 테스트할 수 있습니다:

```bash
# 주소 변환 테스트
python geocoding.py

# 이동 시간 계산 테스트
python directions.py

# 스케줄러 로직 테스트
python scheduler.py

# Coursemos 크롤러 테스트
python coursemos_crawler.py
```

## 🔧 코드 예제

### 주소를 좌표로 변환

```python
from geocoding import get_location_coords

coords = get_location_coords("강남역")
print(coords)  # "127.027926,37.497952"
```

### 이동 시간 계산

```python
from directions import get_travel_time_from_addresses

travel_time = get_travel_time_from_addresses("강남역", "판교역")
print(f"예상 소요 시간: {travel_time}분")
```

### 일정 최적화

```python
from scheduler import allocate_tasks, print_schedule

# 현재 일정
schedule = [
    {"name": "수업", "end_time": "13:00", "location": "강남역"},
    {"name": "아르바이트", "start_time": "15:00", "location": "판교역"}
]

# 할 일 목록
todos = [
    {"task": "과제 작성", "estimated_time": 40},
    {"task": "독서", "estimated_time": 30}
]

# 최적화 실행
optimized = allocate_tasks(schedule, todos)
print_schedule(optimized)
```

## ⚙️ 설정 옵션

### config.py에서 수정 가능한 항목

```python
# 이동 시간 버퍼 (분 단위)
TRAVEL_TIME_BUFFER = 15

# 위치 별칭 설정
LOCATION_ALIASES = {
    "학교": "분당구 불정로 6",
    "집": "서울시 강남구 역삼동",
    "도서관": "서울시 서초구 서초동"
}
```

## 📊 시스템 아키텍처

```
┌─────────────┐
│  사용자 입력  │ (주소, 일정, 할 일)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   Naver Geocoding API           │
│   (주소 → 좌표 변환)              │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Naver Directions 5 API        │
│   (이동 시간 계산)                │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   스케줄러 로직                   │
│   - 가용 시간 계산                │
│   - 작업 자동 배치                │
│   - 최적화된 일정 생성            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│ 최적화된 일정 │
└─────────────┘
```

## 🔍 주요 알고리즘

### 가용 시간 계산

```
실제 가용 시간 = (다음 일정 시작 시간 - 현재 일정 종료 시간) 
                - 이동 시간 
                - 안전 버퍼
```

### 작업 배치 전략

1. 일정을 시간순으로 정렬
2. 각 일정 사이의 간격 계산
3. 이동 시간 및 버퍼 차감
4. 남은 시간에 맞는 작업 할당
5. 할당되지 않은 작업 리포트

## ⚠️ 주의사항

1. **API 무료 사용량**
   - Naver Maps API는 월별 무료 사용량이 제한되어 있습니다
   - Directions 5: 월 300만 건 무료 (2024년 기준, 정책 변경 가능)

2. **주소 정확성**
   - "학교", "집" 같은 별칭은 `config.py`에 정확한 주소로 매핑해야 합니다
   - 모호한 주소는 API가 잘못된 좌표를 반환할 수 있습니다

3. **시간 예측 정확도**
   - API가 제공하는 시간은 '예상' 시간입니다
   - 실제 교통 상황에 따라 달라질 수 있으므로 버퍼 시간을 충분히 설정하세요

4. **Coursemos 크롤러**
   - **yontil-main** 프로젝트의 Learnus 로그인/크롤링 패턴을 기반으로 구현
   - requests + BeautifulSoup과 Selenium 두 가지 모드 지원
   - 실제 Coursemos 연동을 위한 가이드: `COURSEMOS_INTEGRATION_GUIDE.md` 참조

## 🔧 Coursemos 실제 연동

현재 `coursemos_crawler.py`는 **yontil-main 프로젝트**의 Learnus 크롤링 패턴을 기반으로 구현되어 있습니다.

실제 Coursemos와 연동하려면:
1. `COURSEMOS_INTEGRATION_GUIDE.md` 가이드 참조
2. Coursemos의 실제 URL과 HTML 구조에 맞게 수정
3. 로그인 프로세스 분석 및 적용
4. CSS 셀렉터 업데이트

### 참조 구현 (yontil-main)
- `yontil-main/src/core/login/login-learnus.ts` - 다단계 로그인
- `yontil-main/src/core/tasks/fetch-tasks.ts` - 과제 목록 크롤링
- `yontil-main/src/utils/parse-html-string.ts` - HTML 파싱

## 🚧 향후 개발 계획

- [ ] 대중교통 이동 시간 지원 (ODsay API 연동)
- [ ] 데이터베이스 연동 (일정 및 작업 저장)
- [ ] 웹 인터페이스 개발
- [ ] 모바일 앱 연동
- [ ] 작업 우선순위 설정
- [ ] 머신러닝 기반 작업 소요 시간 예측
- [ ] Google Calendar 연동

## 📝 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for YCC Project**

