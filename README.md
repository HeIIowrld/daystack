# daystack

To-do list Tetris program - optimizing your daily tasks with travel time consideration.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API keys
cp env.example .env
# Edit .env with your Naver Cloud Platform API keys

# 3. Check configuration
python check_api.py

# 4. Run
python daystack.py
```

## 📋 Requirements

- Python 3.8+
- Naver Cloud Platform account (free tier available)
- API keys for: Maps Geocoding, Directions 5

## 🔧 Getting Naver API Keys

1. Go to [Naver Cloud Platform](https://console.ncloud.com/)
2. Navigate to: `AI·NAVER API > Application`
3. Create new application
4. **Important:** Enable these APIs:
   - ✅ Maps - Web Dynamic Map
   - ✅ Geocoding - Map Geocoding  
   - ✅ Directions 5 - Map Directions 5
5. Copy Client ID and Client Secret to `.env` file

## 🐛 Troubleshooting 401 Error

**Error:** `Permission Denied - A subscription to the API is required`

**Solution:**
```bash
# Run the diagnostic tool
python check_api.py
```

This checks:
- ✅ .env file exists
- ✅ API keys loaded correctly
- ✅ Geocoding API enabled
- ✅ Directions API enabled

**Common fixes:**
1. Make sure you **enabled** the APIs in Naver Cloud Console (not just created the application)
2. Check API keys are correct (no typos)
3. Wait 1-2 minutes after enabling APIs

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## 📁 Files

- `daystack.py` - Main application
- `scheduler.py` - Task allocation algorithm
- `naver_api.py` - Naver Maps API wrapper (uses only `duration` field)
- `crawler.py` - LMS crawler (yontil-main patterns)
- `check_api.py` - Diagnostic tool for API issues
- `config.py` - Configuration loader

## 💻 Usage

```bash
# Full app
python daystack.py

# Test individual modules
python naver_api.py    # Test API
python scheduler.py    # Test algorithm
python crawler.py      # Test LMS crawler
```

## 🎓 LMS Integration

Based on **yontil-main** patterns:
- Multi-step login with CSRF token extraction
- Course → Tasks hierarchy
- Incomplete task filtering

See [SETUP.md](SETUP.md) for LMS customization guide.

## 📄 License

Educational project.
