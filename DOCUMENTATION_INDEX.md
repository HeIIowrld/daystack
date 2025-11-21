# Documentation Index - YCC Scheduler

Complete guide to all project documentation.

## 📚 Documentation Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    YCC SCHEDULER DOCS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🚀 GETTING STARTED                                              │
│  ├─ README.md ★ START HERE                                      │
│  ├─ QUICKSTART_COURSEMOS.md (5-min setup)                       │
│  └─ example.env (configuration template)                        │
│                                                                  │
│  📖 CORE CONCEPTS                                                │
│  ├─ PRD.md (original requirements)                              │
│  ├─ PROJECT_SUMMARY.md (complete overview)                      │
│  └─ VISUAL_FLOW.md (diagrams)                                   │
│                                                                  │
│  🔗 YONTIL-MAIN INTEGRATION                                      │
│  ├─ YONTIL_INTEGRATION_GUIDE.md (how patterns were applied)     │
│  ├─ ARCHITECTURE_COMPARISON.md (TS vs Python)                   │
│  └─ yontil-main/ (reference source code)                        │
│                                                                  │
│  💻 CODE DOCUMENTATION                                           │
│  ├─ config.py (inline comments)                                 │
│  ├─ geocoding.py (inline comments)                              │
│  ├─ directions.py (inline comments)                             │
│  ├─ scheduler.py (inline comments)                              │
│  ├─ coursemos_crawler.py (inline comments)                      │
│  └─ main.py (inline comments)                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Documentation by Goal

### "I want to run the scheduler right now"

1. **[README.md](README.md)** - Installation & basic usage
2. **[example.env](example.env)** - Get your API keys
3. Run: `python main.py --test`

**Est. time:** 10 minutes

---

### "I want to connect to my actual LMS"

1. **[QUICKSTART_COURSEMOS.md](QUICKSTART_COURSEMOS.md)** ⭐ **START HERE**
   - Step-by-step customization guide
   - How to find CSS selectors
   - Debugging tips
   - Real examples

2. **[coursemos_crawler.py](coursemos_crawler.py)** 
   - Update URLs
   - Update selectors
   - Test

**Est. time:** 30-60 minutes

---

### "I want to understand the architecture"

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete system overview
2. **[VISUAL_FLOW.md](VISUAL_FLOW.md)** - Visual diagrams
3. **[ARCHITECTURE_COMPARISON.md](ARCHITECTURE_COMPARISON.md)** - Deep dive

**Est. time:** 20 minutes reading

---

### "I want to understand the yontil-main patterns"

1. **[YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md)** ⭐ **START HERE**
   - Pattern-by-pattern explanation
   - Code side-by-side comparison
   - Usage examples

2. **[ARCHITECTURE_COMPARISON.md](ARCHITECTURE_COMPARISON.md)**
   - TypeScript vs Python
   - Flow diagrams
   - Performance comparison

3. **[yontil-main source code](yontil-main/)**
   - `src/core/login/` - Authentication patterns
   - `src/core/tasks/` - Task fetching patterns
   - `src/utils/` - Utility functions

**Est. time:** 45 minutes

---

### "I want to extend or modify the code"

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Module overview
2. Code files (all have inline documentation):
   - `config.py` - Add new settings
   - `geocoding.py` - Modify address handling
   - `directions.py` - Add transport modes
   - `scheduler.py` - Improve optimization algorithm
   - `coursemos_crawler.py` - Adapt for your LMS
3. **[YONTIL_INTEGRATION_GUIDE.md](YONTIL_INTEGRATION_GUIDE.md)** - Pattern reference

**Est. time:** Variable

---

## 📄 Document Descriptions

### README.md
- **Type:** Getting Started Guide
- **Length:** ~300 lines
- **Audience:** New users
- **Content:**
  - Project overview
  - Installation instructions
  - Basic usage examples
  - Configuration guide
  - Troubleshooting

**When to read:** First document to read

---

### PRD.md
- **Type:** Requirements Specification
- **Length:** ~150 lines
- **Audience:** Developers, Project managers
- **Content:**
  - Original project goals
  - Technical requirements
  - Naver API specifications
  - Algorithm pseudocode
  - Implementation notes

**When to read:** To understand "why" decisions were made

---

### PROJECT_SUMMARY.md
- **Type:** Comprehensive Overview
- **Length:** ~400 lines
- **Audience:** All users
- **Content:**
  - Complete system architecture
  - Module descriptions
  - Data flow
  - yontil-main integration
  - Use cases
  - Performance metrics

**When to read:** To understand the complete system

---

### QUICKSTART_COURSEMOS.md ⭐
- **Type:** Practical Tutorial
- **Length:** ~500 lines
- **Audience:** Users customizing the crawler
- **Content:**
  - 5-minute quick start
  - How to find CSS selectors
  - Debugging guide
  - Common issues & solutions
  - Real customization example

**When to read:** When adapting crawler for your LMS

---

### YONTIL_INTEGRATION_GUIDE.md ⭐
- **Type:** Technical Deep Dive
- **Length:** ~400 lines
- **Audience:** Developers
- **Content:**
  - yontil-main pattern explanations
  - Code comparisons (TS vs Python)
  - Pattern-by-pattern adaptation
  - Usage examples
  - Customization guide

**When to read:** To understand the crawler implementation

---

### ARCHITECTURE_COMPARISON.md
- **Type:** Architectural Analysis
- **Length:** ~600 lines
- **Audience:** Developers, Architects
- **Content:**
  - System diagrams
  - Login flow comparison
  - Task fetching comparison
  - Technical stack comparison
  - Performance analysis
  - Security considerations

**When to read:** For deep architectural understanding

---

### VISUAL_FLOW.md
- **Type:** Visual Reference
- **Length:** ~300 lines
- **Audience:** Visual learners
- **Content:**
  - Complete system flow diagram
  - Login flow visualization
  - Task fetching flow
  - API integration flow
  - Terminal output flow
  - Data structure flow

**When to read:** To visualize how everything connects

---

### example.env
- **Type:** Configuration Template
- **Length:** ~10 lines
- **Audience:** All users
- **Content:**
  - API key placeholders
  - Configuration options
  - Comments and instructions

**When to read:** During initial setup

---

## 🗺️ Learning Paths

### Path 1: Quick User (30 minutes)
```
1. README.md (Installation & Setup)
   ↓
2. example.env (Configure API keys)
   ↓
3. Run: python main.py --test
   ↓
4. Run: python main.py
   ↓
Done! ✅
```

### Path 2: LMS Integrator (2 hours)
```
1. README.md (Overview)
   ↓
2. QUICKSTART_COURSEMOS.md (Customization guide)
   ↓
3. Open coursemos_crawler.py
   ↓
4. Test with your LMS
   ↓
5. Debug using QUICKSTART_COURSEMOS.md tips
   ↓
Done! ✅
```

### Path 3: Developer (4 hours)
```
1. README.md (Overview)
   ↓
2. PROJECT_SUMMARY.md (Architecture)
   ↓
3. YONTIL_INTEGRATION_GUIDE.md (Patterns)
   ↓
4. ARCHITECTURE_COMPARISON.md (Deep dive)
   ↓
5. Read source code with inline docs
   ↓
6. VISUAL_FLOW.md (Understand flows)
   ↓
Done! ✅
```

### Path 4: Researcher (6 hours)
```
1. PRD.md (Original requirements)
   ↓
2. PROJECT_SUMMARY.md (Implementation)
   ↓
3. yontil-main source code (Reference)
   ↓
4. YONTIL_INTEGRATION_GUIDE.md (Pattern analysis)
   ↓
5. ARCHITECTURE_COMPARISON.md (Comparison)
   ↓
6. All code files (Complete understanding)
   ↓
Done! ✅
```

---

## 🔍 Quick Reference

### Commands
```bash
# Test API setup
python main.py --test

# Run main application
python main.py

# Test individual modules
python geocoding.py
python directions.py
python scheduler.py
python coursemos_crawler.py
```

### Key Files to Modify

**For Configuration:**
- `.env` - API keys and settings
- `config.py` - LOCATION_ALIASES, TRAVEL_TIME_BUFFER

**For LMS Integration:**
- `coursemos_crawler.py` - URLs, selectors, login logic

**For Schedule Source:**
- `main.py` - `get_sample_schedule()` function

**For Optimization Algorithm:**
- `scheduler.py` - `allocate_tasks()` function

---

## 📊 Documentation Stats

| Document | Lines | Words | Read Time | Level |
|----------|-------|-------|-----------|-------|
| README.md | ~300 | ~2000 | 8 min | Beginner |
| PRD.md | ~150 | ~1000 | 5 min | Intermediate |
| PROJECT_SUMMARY.md | ~400 | ~3000 | 15 min | All |
| QUICKSTART_COURSEMOS.md | ~500 | ~4000 | 20 min | Intermediate |
| YONTIL_INTEGRATION_GUIDE.md | ~400 | ~3500 | 18 min | Advanced |
| ARCHITECTURE_COMPARISON.md | ~600 | ~5000 | 25 min | Advanced |
| VISUAL_FLOW.md | ~300 | ~1500 | 10 min | All |
| **Total** | **~2650** | **~20000** | **~101 min** | - |

---

## 🎓 External Resources

### Naver Cloud Platform
- [Naver Maps API Docs](https://api.ncloud-docs.com/docs/ai-naver-mapsgeocoding)
- [Directions API Guide](https://api.ncloud-docs.com/docs/ai-naver-mapsdirections15)

### Python Libraries
- [Requests Documentation](https://docs.python-requests.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)

### yontil-main Project
- [Source Code](yontil-main/)
- Chrome Extension Architecture
- Moodle/LearnUs Integration Patterns

---

## 💡 Tips for Reading Documentation

### For Visual Learners
Start with:
1. VISUAL_FLOW.md
2. ARCHITECTURE_COMPARISON.md (diagrams)
3. Then read text documents

### For Hands-On Learners
Start with:
1. README.md (setup)
2. Run the code
3. QUICKSTART_COURSEMOS.md (customize)
4. Refer to other docs as needed

### For Theoretical Learners
Start with:
1. PRD.md
2. PROJECT_SUMMARY.md
3. YONTIL_INTEGRATION_GUIDE.md
4. Then try the code

---

## 🔄 Document Update Policy

### When to Update

- **README.md** - New features, installation changes
- **QUICKSTART_COURSEMOS.md** - New customization patterns, common issues
- **YONTIL_INTEGRATION_GUIDE.md** - New patterns from yontil-main
- **Code inline docs** - Every code change
- **VISUAL_FLOW.md** - Major flow changes

### Version History

- **v1.0.0** (2024-11-21) - Initial complete documentation
- Based on yontil-main patterns as of Nov 2024

---

## 📞 Getting Help

1. **Check Documentation** (this index!)
2. **Search Issues** (GitHub)
3. **Create New Issue** with:
   - What you tried
   - What happened
   - What you expected
   - Relevant logs
   - Which docs you read

---

## ✅ Documentation Checklist

Before starting development:
- [ ] Read README.md
- [ ] Understood PROJECT_SUMMARY.md
- [ ] Configured .env file
- [ ] Ran --test successfully

Before customizing crawler:
- [ ] Read QUICKSTART_COURSEMOS.md
- [ ] Inspected your LMS HTML
- [ ] Found correct CSS selectors
- [ ] Tested login flow

Before modifying code:
- [ ] Read relevant module docs
- [ ] Understood yontil-main patterns
- [ ] Reviewed VISUAL_FLOW.md
- [ ] Wrote tests

---

**Use this index as your roadmap through the YCC Scheduler documentation!**

**Last Updated:** 2024-11-21  
**Documentation Version:** 1.0.0


