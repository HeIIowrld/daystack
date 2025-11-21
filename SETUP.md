# Setup Guide for daystack

## 1. Get Naver API Keys (5 minutes)

1. Go to [Naver Cloud Platform](https://www.ncloud.com/)
2. Sign up or log in
3. Navigate to: `AI·NAVER API > Application`
4. Create new application
5. Enable these APIs:
   - ✅ Geocoding
   - ✅ Directions
6. Copy your Client ID and Client Secret

## 2. Configure Environment

```bash
# Copy example file
cp env.example .env

# Or create .env manually with:
# NAVER_CLIENT_ID=paste_your_client_id
# NAVER_CLIENT_SECRET=paste_your_client_secret
# TRAVEL_TIME_BUFFER=15
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Test

```bash
# Test Naver API connection
python naver_api.py

# Expected output:
# Testing Naver API...
# 강남역 coordinates: 127.027926,37.497952
# 강남역 → 판교역: 55분
```

## 5. Run

```bash
python daystack.py
```

## Customizing for Your LMS

The `crawler.py` uses patterns from [yontil-main](yontil-main/) project. To adapt:

1. **Update URLs** in `crawler.py`:
   ```python
   self.lms_url = "https://your-lms.com"
   ```

2. **Find CSS Selectors** using browser DevTools:
   - Open your LMS in Chrome
   - Press F12 → Elements tab
   - Find course list: `document.querySelectorAll('.your-course-selector')`
   - Find tasks: `document.querySelectorAll('.your-task-selector')`

3. **Update selectors** in `crawler.py`:
   ```python
   courses = soup.select('.your-course-selector')
   tasks = course_soup.select('.your-task-selector:not(.completed)')
   ```

4. **Test**:
   ```bash
   python crawler.py
   ```

## yontil-main Reference

The crawler implementation references these files from yontil-main:

- `yontil-main/src/core/login/login-learnus.ts` - Multi-step login
- `yontil-main/src/core/tasks/fetch-tasks.ts` - Task fetching hierarchy  
- `yontil-main/src/utils/parse-html-string.ts` - HTML parsing

Key patterns applied:
1. Extract hidden form fields (CSRF tokens)
2. Include them in login POST
3. Iterate courses, then tasks within each
4. Filter incomplete tasks with CSS selectors

## Troubleshooting

**"Configuration error: API keys not found"**
→ Create `.env` file with your Naver API keys

**"Geocoding failed"**
→ Check internet connection and API key validity

**"Login failed"**
→ Update LMS URL and selectors to match your LMS structure

