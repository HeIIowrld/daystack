# daystack

To-do list Tetris program optimizing your daily tasks with travel time consideration.

## 🎯 What is daystack?

Daystack automatically fits your to-do tasks into your daily schedule like Tetris blocks, considering real travel time between locations.

```
Your Schedule:        Tasks to do:          Result:
┌──────────┐         ┌──────────┐          ┌──────────┐
│ 09:00    │         │ Task A   │          │ 09:00    │
│ Class    │         │ (40 min) │          │ Class    │
│ 12:00    │         └──────────┘          │ 12:00    │
└──────────┘         ┌──────────┐          ├──────────┤
     │               │ Task B   │          │ 12:40    │
     │ 4 hours       │ (30 min) │   →      │ Task A ✓ │
     │               └──────────┘          │ 13:20    │
     ↓                                     ├──────────┤
┌──────────┐                              │ 13:20    │
│ 16:00    │                              │ Task B ✓ │
│ Part-time│                              │ 13:50    │
│ 20:00    │                              ├──────────┤
└──────────┘                              │ 14:00    │
                                          │ Travel   │
                                          │ 15:30    │
                                          ├──────────┤
                                          │ 16:00    │
                                          │ Part-time│
                                          │ 20:00    │
                                          └──────────┘
```

## 🚀 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Configure

Copy `env.example` to `.env` and add your API keys:

```bash
cp env.example .env
# Then edit .env with your Naver Cloud Platform API keys
```

Get API keys from [Naver Cloud Platform](https://www.ncloud.com/)

### 3. Run

```bash
python daystack.py
```

## 📁 Project Structure

```
daystack/
├── daystack.py          # Main application
├── scheduler.py         # Tetris allocation algorithm
├── naver_api.py         # Naver Maps API (duration only)
├── crawler.py           # LMS crawler (yontil-main patterns)
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── .env                 # API keys (create this)
```

## 🔧 How It Works

1. **Get your schedule** (events with times and locations)
2. **Get your tasks** (from LMS or manual input)
3. **Calculate travel time** between locations (Naver Directions API)
4. **Allocate tasks** to free time slots (Tetris-style)
5. **Get optimized schedule** with tasks fitted in

### API Usage

From Naver Directions API response, we only use `duration`:

```json
{
  "route": {
    "traoptimal": [{
      "summary": {
        "duration": 15856847  // ← Only this is used (ms → minutes)
      }
    }]
  }
}
```

## 🎓 LMS Integration (yontil-main patterns)

The `crawler.py` uses patterns from **yontil-main** project (Yonsei LearnUs Chrome extension):

**Key Patterns Applied:**
- **`parse_input_tags_from_html()`** - Extract hidden form fields (CSRF tokens)
- **Multi-step login** - Get page → Extract tokens → Submit with tokens
- **Course → Tasks hierarchy** - Iterate courses, then tasks within each course
- **Incomplete task filtering** - `.select('.activity:not(.completed)')`

**Reference Files:** (see `yontil-main/` directory)
- `src/core/login/login-learnus.ts` - Authentication flow
- `src/core/tasks/fetch-tasks.ts` - Task crawling
- `src/utils/parse-html-string.ts` - HTML parsing utility

**To customize for your LMS:**
See [SETUP.md](SETUP.md) for detailed guide

## 💻 Usage Examples

### Test Naver API

```bash
python naver_api.py
```

### Test Scheduler

```bash
python scheduler.py
```

### Test Crawler

```bash
python crawler.py
```

### Full Application

```bash
python daystack.py
```

## ⚙️ Configuration

Edit `config.py` or `.env`:

- `TRAVEL_TIME_BUFFER` - Extra minutes to add to travel time (default: 15)
- Location aliases - Add frequently visited places

## 🎯 Future Plans

- [ ] Google Calendar integration
- [ ] Database for persistent schedules
- [ ] Web UI
- [ ] Mobile app
- [ ] ML-based task duration prediction
- [ ] Public transportation support (ODsay API)

## 📄 License

Educational project

---

**Stack your day efficiently!** 📚✨
