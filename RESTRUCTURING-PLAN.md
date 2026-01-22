# SBDB BRANCH RESTRUCTURING PLAN
## Clean Repository Organization for KSE Production

**Date:** 2026-01-22  
**Status:** 🟢 READY TO EXECUTE  
**Timeline:** This session + follow-ups  
**Target:** Production-ready KSE repository structure

---

## 📋 RESTRUCTURING OVERVIEW

### What's Happening

We're transforming the existing sbdb branch from **experimental/duplicated code** into **production-grade KSE codebase** by:

1. **Removing duplicates** (5 old files)
2. **Renaming to KSE convention** (sbdb_*.py → kse_*.py)
3. **Organizing into directories** (config/, database/, tests/, docs/)
4. **Adding missing files** (SQL migrations, test files, configs)
5. **Updating main entry points** (run_v3.py, klar_browser_client.py)

---

## 🗑️ PHASE 1: DELETE DUPLICATE FILES

**These files are OLD/DUPLICATE and will be deleted:**

```
sbdbcore.py              ← Old version (use sbdb_core_advanced.py)
sbdbapi.py               ← Old version (use sbdb_api.py)
sbdbcrawler.py           ← Old version (use sbdb_crawler.py)
sbdbindex.py             ← Old version (use sbdb_index.py)
sbdb_core.py             ← Old version (use sbdb_core_advanced.py)
```

**These will KEEP (best versions):**
```
✅ sbdb_core_advanced.py → Will rename to kse_core.py
✅ sbdb_crawler.py       → Will rename to kse_crawler.py
✅ sbdb_index.py         → Will rename to kse_index.py
✅ sbdb_api.py           → Will rename to kse_api.py
✅ run_v3.py             → Keep (main entry point)
✅ klar_browser_sbdb_v3.py → Will rename to klar_browser_client.py
✅ requirements.txt      → Will update
```

---

## 📁 PHASE 2: RENAME & ORGANIZE

**Mapping of old → new filenames:**

```
sbdb_core_advanced.py    →  kse_core.py           (Advanced NLP + search logic)
sbdb_api.py              →  kse_api.py            (Flask API endpoints)
sbdb_crawler.py          →  kse_crawler.py        (Web crawler)
sbdb_index.py            →  kse_index.py          (Inverted index)

NEW FILES TO CREATE:
kse_server.py            (Flask app orchestrator)
kse_database.py          (PostgreSQL layer)
kse_nlp.py               (Swedish NLP engine - extract from kse_core.py)
kse_search.py            (Search algorithm - extract from kse_core.py)
kse_gui.py               (PyQt6 GUI - refactor run_v3.py)
klar_browser_client.py   (Rename klar_browser_sbdb_v3.py)
```

---

## 📂 PHASE 3: FINAL DIRECTORY STRUCTURE

After restructuring, the repository will look like:

```
klar/ (sbdb branch)
│
├── 🔧 MAIN ENTRY POINTS
│   ├── run_v3.py                      ← Server + GUI (Phase 1/2/3)
│   └── klar_browser_client.py         ← Client application
│
├── 🧠 CORE ENGINE (Refactored)
│   ├── kse_server.py                  ← Flask app orchestrator (NEW)
│   ├── kse_core.py                    ← Core logic (from sbdb_core_advanced.py)
│   ├── kse_nlp.py                     ← Swedish NLP engine (from kse_core.py)
│   ├── kse_search.py                  ← Search algorithm (from kse_core.py)
│   ├── kse_database.py                ← PostgreSQL layer (NEW)
│   ├── kse_api.py                     ← Flask API routes (from sbdb_api.py)
│   ├── kse_crawler.py                 ← Web crawler (from sbdb_crawler.py)
│   ├── kse_index.py                   ← Inverted index (from sbdb_index.py)
│   └── kse_gui.py                     ← PyQt6 GUI (from run_v3.py)
│
├── ⚙️ CONFIGURATION
│   ├── config/
│   │   ├── swedish_domains.json       ← 2,543 .se domains (NEW)
│   │   ├── swedish_stopwords.txt      ← Common words (NEW)
│   │   └── config_template.json       ← Example config (NEW)
│   └── .env.example                   ← Environment variables (NEW)
│
├── 💾 DATABASE
│   ├── database/
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql ← CREATE TABLE statements (NEW)
│   │   │   ├── 002_indexes.sql        ← Performance indexes (NEW)
│   │   │   └── 003_views.sql          ← Materialized views (NEW)
│   │   └── backup/
│   │       └── .gitkeep
│   └── kse_database.py                ← Migration runner
│
├── 🧪 TESTING
│   ├── tests/
│   │   ├── conftest.py                ← Pytest configuration (NEW)
│   │   ├── test_nlp.py                ← NLP tests (NEW)
│   │   ├── test_crawler.py            ← Crawler tests (NEW)
│   │   ├── test_search.py             ← Search algorithm tests (NEW)
│   │   ├── test_index.py              ← Index tests (NEW)
│   │   ├── test_database.py           ← Database tests (NEW)
│   │   ├── test_api.py                ← API tests (NEW)
│   │   └── test_gui.py                ← GUI tests (NEW)
│   └── pytest.ini                     ← Pytest config (NEW)
│
├── 📚 DOCUMENTATION
│   ├── docs/
│   │   ├── ARCHITECTURE.md            ← System design (NEW)
│   │   ├── API.md                     ← API reference (NEW)
│   │   ├── SETUP.md                   ← Installation guide (NEW)
│   │   ├── DEPLOYMENT.md              ← National deployment (NEW)
│   │   ├── TROUBLESHOOTING.md         ← Common issues (NEW)
│   │   └── CONTRIBUTING.md            ← Developer guide (NEW)
│   ├── README.md                      ← Project overview (UPDATE)
│   ├── KSE-STRATEGIC-VISION.md        ← Vision document (KEEP)
│   ├── KSE-MASTERPLAN.md              ← Master plan (KEEP)
│   └── KSE-IMPLEMENTATION-ROADMAP.md  ← Roadmap (KEEP)
│
├── 📦 PROJECT FILES
│   ├── requirements.txt                ← Python dependencies (UPDATE)
│   ├── setup.py                       ← Package setup (NEW)
│   ├── pyproject.toml                 ← Modern Python config (NEW)
│   ├── .gitignore                     ← Git ignore rules (UPDATE)
│   ├── LICENSE                        ← AGPL v3 (NEW)
│   └── RESTRUCTURING-PLAN.md          ← This file
│
└── 📝 DEPRECATED (TO DELETE)
    ├── sbdbcore.py                    ← DELETE
    ├── sbdbapi.py                     ← DELETE
    ├── sbdbcrawler.py                 ← DELETE
    ├── sbdbindex.py                   ← DELETE
    ├── sbdb_core.py                   ← DELETE
    ├── klar_browser.py                ← DELETE (old version)
    ├── DEPLOYMENT_CHECKLIST.md        ← ARCHIVE (merge into docs/)
    └── SBDB_README.md                 ← ARCHIVE (merge into README.md)
```

---

## ✅ EXECUTION CHECKLIST

### Step-by-Step Tasks

#### PHASE 1: DELETE DUPLICATES ✓
- [ ] Delete sbdbcore.py
- [ ] Delete sbdbapi.py
- [ ] Delete sbdbcrawler.py
- [ ] Delete sbdbindex.py
- [ ] Delete sbdb_core.py
- [ ] Delete klar_browser.py (old)
- [ ] Delete SBDB_README.md (archived)
- [ ] Delete DEPLOYMENT_CHECKLIST.md (archived)

#### PHASE 2: RENAME FILES ✓
- [ ] sbdb_core_advanced.py → kse_core.py
- [ ] sbdb_api.py → kse_api.py
- [ ] sbdb_crawler.py → kse_crawler.py
- [ ] sbdb_index.py → kse_index.py
- [ ] klar_browser_sbdb_v3.py → klar_browser_client.py

#### PHASE 3: CREATE DIRECTORIES ✓
- [ ] Create config/ directory
- [ ] Create database/migrations/ directory
- [ ] Create tests/ directory
- [ ] Create docs/ directory

#### PHASE 4: ADD NEW FILES ✓
- [ ] Create kse_server.py (Flask orchestrator)
- [ ] Create kse_database.py (PostgreSQL layer)
- [ ] Create kse_nlp.py (NLP engine)
- [ ] Create kse_search.py (Search algorithm)
- [ ] Create kse_gui.py (PyQt6 GUI)
- [ ] Create SQL migrations (001, 002, 003)
- [ ] Create test files (8 files)
- [ ] Create documentation files
- [ ] Create config/swedish_domains.json
- [ ] Create config/swedish_stopwords.txt
- [ ] Create setup.py
- [ ] Create pyproject.toml
- [ ] Create LICENSE (AGPL v3)

#### PHASE 5: UPDATE EXISTING FILES ✓
- [ ] Update run_v3.py (restructure GUI)
- [ ] Update requirements.txt
- [ ] Update README.md
- [ ] Update .gitignore

---

## 📊 IMPACT ANALYSIS

### Before Restructuring
```
Files: 16 Python files + 4 docs
Structure: Flat, confusing (sbdb_* + sbdbapi variants)
Duplicates: 5 old files
Issues: No tests, no SQL migrations, no docs, no config
Status: Experimental
```

### After Restructuring
```
Files: 25+ Python files + 6+ docs (organized)
Structure: Clean, professional (kse_* convention)
Duplicates: 0 (consolidated)
Quality: Tests, SQL, docs, configs included
Status: Production-ready
```

---

## 🚀 BENEFITS

### For Development
- ✅ Clear file organization
- ✅ Easy to find what you need
- ✅ Production-grade structure
- ✅ Ready for team collaboration
- ✅ Professional appearance

### For Deployment
- ✅ Configurations separate from code
- ✅ Database migrations tracked
- ✅ Tests ready to run
- ✅ Documentation complete
- ✅ Ready for production servers

### For Maintenance
- ✅ No duplicate code
- ✅ Clear separation of concerns
- ✅ Comprehensive documentation
- ✅ Easy to update/debug
- ✅ Version control friendly

---

## 📝 NOTES

1. **No data loss** - All existing code is preserved (just reorganized)
2. **Backward compatible** - Old file names mapped to new ones
3. **Incremental approach** - Can be done file-by-file
4. **Git history preserved** - All commits remain intact
5. **Production ready** - After restructuring, we can immediately begin adding features

---

## 🎯 NEXT ACTIONS

**This session:**
1. ✅ Create this restructuring plan
2. ▶️ Get your approval to proceed
3. ▶️ Execute Phase 1-3 (deletions, renames, directories)

**Next session:**
1. ▶️ Create new core files (kse_server.py, etc.)
2. ▶️ Create SQL migrations
3. ▶️ Create test suite

**Following sessions:**
1. ▶️ Add comprehensive documentation
2. ▶️ Refactor GUIs (Phase 1/2/3)
3. ▶️ Add configurations
4. ▶️ Final production quality sweep

---

**Status:** 🟢 READY TO EXECUTE  
**Approval Required:** YES - Proceed with Phase 1-3?  
**Estimated Time:** 2-3 hours for cleanup + organization

