# Setup Guide for daystack

## 1. Get Naver API Keys (5 minutes)

1. Go to [Naver Cloud Platform](https://www.ncloud.com/)
2. Sign up or log in
3. Navigate to: `AI·NAVER API > Application`
4. Click **"애플리케이션 등록"** (Register Application)
5. Fill in application name (e.g., "daystack")
6. Click **"등록"** (Register)
7. **IMPORTANT:** Enable these APIs (check the boxes):
   - ✅ **Maps** - Web Dynamic Map
   - ✅ **Geocoding** - Map Geocoding
   - ✅ **Directions 5** - Map Directions 5
8. Copy your:
   - **Client ID** (인증 정보 > Client ID)
   - **Client Secret** (인증 정보 > Client Secret)

⚠️ **Common Issue:** If you get "Permission Denied" error, make sure you checked ALL the API boxes in step 7!

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
# Run diagnostic checker
python check_api.py

# This will check:
# 1. .env file exists
# 2. API keys are loaded
# 3. Geocoding API works
# 4. Directions API works

# If all checks pass, you'll see:
# ✅ ALL CHECKS PASSED!
```

### Troubleshooting 401 Error

If you get **"Error 401: Permission Denied"**:

1. **Check API keys are correct:**
   ```bash
   cat .env  # On Linux/Mac
   type .env # On Windows
   ```
   Make sure keys match those in Naver Cloud Console

2. **Enable APIs in Naver Cloud:**
   - Go to https://console.ncloud.com/
   - Navigate to: AI·NAVER API > Application
   - Click your application name
   - Scroll down to **"서비스 선택"** (Service Selection)
   - Make sure these are **checked**:
     - ✅ Maps - Web Dynamic Map
     - ✅ Geocoding - Map Geocoding
     - ✅ Directions 5 - Map Directions 5
   - Click **"수정"** (Modify) to save

3. **Wait a few minutes:**
   - API activation can take 1-2 minutes
   - Try again after waiting

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

