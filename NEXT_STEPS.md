# ✅ What's Working & Next Steps

## ✅ What's Working Now

- **Directions API** - ✅ WORKS with `maps.apigw.ntruss.com`
- Your curl command is successful
- Python code now uses correct URL

## ❌ What's Not Working

- **Geocoding API** - ❌ Returns 401 "Permission Denied"
- This prevents converting addresses like "강남역" to coordinates

## 🔧 To Fix Geocoding (5 minutes)

### Step 1: Go to Naver Cloud Console
https://console.ncloud.com/

### Step 2: Navigate to Your Application
- Click: `AI·NAVER API` (left menu)
- Click: `Application` 
- Click: Your application name (e.g., "daystack")

### Step 3: Enable Geocoding API
- Scroll down to **"서비스 선택"** (Service Selection)
- You'll see a list of APIs
- Find and CHECK:
  - ✅ **Geocoding** (Map Geocoding)
  - ✅ **Directions 5** (Map Directions 5) ← Already enabled
- Click **"수정"** (Modify/Save) button at bottom

### Step 4: Wait & Test
```bash
# Wait 1-2 minutes for activation
python check_api.py
```

## 🎯 Alternative: Use Coordinates Directly

If you don't need address-to-coordinate conversion, you can use coordinates directly:

```python
from scheduler import allocate_tasks

schedule = [
    {
        "name": "수업",
        "end_time": "13:00",
        "coordinates": "127.027926,37.497952"  # Instead of location name
    },
    {
        "name": "아르바이트", 
        "start_time": "16:00",
        "coordinates": "127.111670,37.394953"
    }
]
```

Then modify `scheduler.py` to use coordinates directly instead of calling geocoding.

## 📊 Current Status

| API | Status | URL | Solution |
|-----|--------|-----|----------|
| **Directions** | ✅ Working | `maps.apigw.ntruss.com` | Already fixed |
| **Geocoding** | ❌ 401 Error | `naveropenapi.apigw.ntruss.com` | Enable in console |

## ✨ Once Both APIs Work

You'll be able to:
1. ✅ Convert addresses to coordinates ("강남역" → lat/lon)
2. ✅ Calculate travel time between locations
3. ✅ Run full daystack scheduler
4. ✅ Optimize your daily tasks automatically

## 🚀 Quick Test Commands

```bash
# Test only Directions (works now)
python test_directions_only.py

# Test both APIs (will work after enabling Geocoding)
python check_api.py

# Full app (will work after enabling Geocoding)
python daystack.py
```

---

**TL;DR:** Directions API works! Now just enable Geocoding API in Naver Cloud Console.

