# daystack

To-do list Tetris program - optimizing your daily tasks with travel time consideration.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API keys
cp env.example .env
# Edit .env with your Naver Cloud Platform API keys

# 3. Enable APIs (IMPORTANT!)
# Go to https://console.ncloud.com/
# AI·NAVER API > Your Application
# Enable BOTH:
#   ✅ Geocoding (Map Geocoding)
#   ✅ Directions 5 (Map Directions 5)

# 4. Test
python test_directions_only.py  # Test with coordinates
python check_api.py             # Full test

# 5. Run
python daystack.py
```

## ⚠️ IMPORTANT: Enable Both APIs

Your curl worked because **Directions API is enabled**. But you also need **Geocoding API**:

1. Go to [Naver Cloud Console](https://console.ncloud.com/)
2. Navigate to: `AI·NAVER API > Application > (Your App)`
3. Scroll to "서비스 선택" (Service Selection)
4. **Check BOTH boxes:**
   - ✅ **Geocoding** - Map Geocoding
   - ✅ **Directions 5** - Map Directions 5
5. Click "수정" (Modify) to save
6. Wait 1-2 minutes
7. Run: `python check_api.py`

## 🐛 Troubleshooting

**Directions works but Geocoding fails (401)?**
→ You enabled Directions but not Geocoding. Follow steps above.

**Want to test without Geocoding?**
```bash
python test_directions_only.py  # Uses hardcoded coordinates
```

## 📁 Files

- `daystack.py` - Main application
- `scheduler.py` - Task allocation
- `naver_api.py` - API wrapper (fixed URLs: maps.apigw.ntruss.com)
- `crawler.py` - LMS crawler
- `check_api.py` - Diagnostic tool
- `test_directions_only.py` - Test directions without geocoding

## 💻 Usage

```bash
python daystack.py              # Full app
python naver_api.py             # Test both APIs
python test_directions_only.py  # Test directions only
python check_api.py             # Diagnose issues
```

## 🎓 LMS Integration

Based on **yontil-main** patterns. See [SETUP.md](SETUP.md) for customization.

## 📄 License

Educational project.
