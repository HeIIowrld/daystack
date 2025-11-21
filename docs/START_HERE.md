# 🎯 START HERE - YCC Scheduler

Welcome to the YCC Scheduler! This guide will get you started in 5 minutes.

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

## Step 2: Get Naver API Keys (External - 5-10 minutes)

1. Visit [Naver Cloud Platform](https://www.ncloud.com/)
2. Sign up / Log in
3. Go to: `AI·NAVER API > Application`
4. Create new application
5. Enable these APIs:
   - ✅ Maps
   - ✅ Geocoding
   - ✅ Directions 5
6. Copy your:
   - Client ID
   - Client Secret

## Step 3: Configure Environment (1 minute)

```bash
# Copy example file
cp example.env .env

# Edit .env file and paste your API keys
# NAVER_CLIENT_ID=your_actual_client_id
# NAVER_CLIENT_SECRET=your_actual_client_secret
```

## Step 4: Test (30 seconds)

```bash
python main.py --test
```

Expected output:
```
=== Geocoding Test ===
✓ 분당구 불정로 6 -> 127.111670,37.394953
✓ 강남역 -> 127.027926,37.497952

=== Travel Time Calculation Test ===
✓ 강남역 → 판교역: 55분

✅ 모든 테스트 통과!
```

## Step 5: Run (1 minute)

```bash
python main.py
```

Choose option 1 or 2:
- **Option 1:** Use Coursemos crawler (currently mock data)
- **Option 2:** Manually input tasks

The scheduler will:
1. ✅ Calculate travel time between locations
2. ✅ Find free time in your schedule
3. ✅ Automatically allocate tasks
4. ✅ Display optimized schedule

---

## What Next?

### ✅ Working? Great!

You can now:
- Use it daily with sample data
- Customize your schedule in `main.py` → `get_sample_schedule()`
- Add your frequent locations in `config.py` → `LOCATION_ALIASES`

### 🔧 Want to Connect Your Real LMS?

Read: **[QUICKSTART_COURSEMOS.md](QUICKSTART_COURSEMOS.md)**

It shows you how to:
- Update URLs for your LMS
- Find the right CSS selectors
- Test and debug
- Handle login flows

### 📚 Want to Understand the Code?

Read: **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)**

It provides:
- Complete documentation roadmap
- Learning paths for different goals
- Module explanations
- Architecture guides

### 🤔 Need Help?

1. Check [README.md](README.md) for full documentation
2. Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for specific topics
3. Search GitHub Issues
4. Create a new issue

---

## Quick Commands Reference

```bash
# Test API connection
python main.py --test

# Run main scheduler
python main.py

# Test individual modules
python geocoding.py          # Test address → coordinates
python directions.py         # Test travel time calculation
python scheduler.py          # Test scheduling algorithm
python coursemos_crawler.py  # Test LMS crawler (mock data)
```

---

## Common Issues

### "Configuration error: API keys not found"
→ Create `.env` file with your Naver API keys

### "Geocoding failed"
→ Check your internet connection
→ Verify API keys are correct

### "No linter errors found" but code doesn't work
→ Make sure you ran `pip install -r requirements.txt`
→ Check Python version (need 3.8+)

---

## Project Structure (Quick View)

```
scheduler/
├── main.py                  # ⭐ Main application - START HERE
├── config.py                # Configuration & API keys
├── geocoding.py             # Address → Coordinates
├── directions.py            # Travel time calculation
├── scheduler.py             # Optimization logic
├── coursemos_crawler.py     # LMS integration
│
├── .env                     # ⚠️ Your API keys (create this!)
├── requirements.txt         # Dependencies
│
└── 📚 Documentation/
    ├── README.md            # Full documentation
    ├── DOCUMENTATION_INDEX.md  # Doc roadmap
    ├── QUICKSTART_COURSEMOS.md # LMS customization
    └── ...more guides...
```

---

## Success Criteria ✅

You've successfully set up YCC Scheduler if:

- ✅ `python main.py --test` shows all green checkmarks
- ✅ `python main.py` runs without errors
- ✅ You see an optimized schedule output
- ✅ Travel times are calculated correctly

---

## Next Steps

Choose your path:

**Path A: Daily User**
→ Just use it! Customize `get_sample_schedule()` with your real schedule

**Path B: LMS Integrator**
→ Read [QUICKSTART_COURSEMOS.md](QUICKSTART_COURSEMOS.md)
→ Adapt crawler for your LMS

**Path C: Developer**
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
→ Explore the codebase
→ Check [YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md) for patterns

---

**🎉 Congratulations! You're ready to use YCC Scheduler!**

For more information, see: [README.md](README.md)


