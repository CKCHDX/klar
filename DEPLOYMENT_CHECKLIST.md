# Klar SBDB - Production Deployment Checklist

## Pre-Launch Verification

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Swedish NLP models downloaded: `python -m spacy download sv_core_news_sm`

### System Resources
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space available
- [ ] Port 8080 not in use: `lsof -i :8080` (Linux/macOS)
- [ ] Network connectivity verified

### Code Verification
- [ ] All 5 modules present:
  - [ ] `run_v3.py` (main orchestrator)
  - [ ] `sbdbcore.py` (NLP + config)
  - [ ] `sbdbcrawler.py` (crawler + change detection)
  - [ ] `sbdbindex.py` (indexing + search)
  - [ ] `sbdbapi.py` (REST API)
- [ ] `requirements.txt` complete
- [ ] No import errors: `python -c "from sbdbcore import *; from sbdbcrawler import *; from sbdbindex import *; from sbdbapi import *"`

---

## Phase 1: First-Run Setup

### Launch
```bash
python run_v3.py
```
Expected: Phase 1 Setup Wizard dialog appears

### Step 1: Initialize
- [ ] Click "Initialize Database"
- [ ] Verify output:
  ```
  ✓ Database initialized at: .klarsbdbdata
  Created:
    - .klarsbdbdata/ directory
    - config.json
    - domains.json (2,543 Swedish domains)
    - pages.json (empty)
    - index.json (empty)
    - stats.json
    - logs/ directory
  ```
- [ ] Check disk: `du -sh .klarsbdbdata` should be ~10MB

### Step 2: Domain Discovery
- [ ] Click "Next" to proceed
- [ ] Verify 2,543 domains listed with categories
- [ ] Categories visible:
  - Government: 127
  - News & Media: 342
  - Business: 891
  - Education: 284
  - Cultural: 456
  - Other: 443

### Step 3: Domain Curation
- [ ] Check at least 5 domains (recommend 20-50 for production)
- [ ] Click "Select All" or manually select domains
- [ ] Example selection:
  - `sverigesradio.se` (news, high trust)
  - `svt.se` (TV, high trust)
  - `dn.se` (newspaper, high trust)
  - `stockholm.se` (city, high trust)
  - `kth.se` (university, high trust)
- [ ] Verify selection count displayed

### Step 4: Crawl Configuration
- [ ] Crawl Strategy: Select "Smart (.se only)" (default)
- [ ] Max Pages: 500 (good for demo), increase to 5000 for production
- [ ] Recrawl Frequency: "24 hours" (recommended)
- [ ] Change Detection: Checked (enabled)

### Step 5: Execute Crawl
- [ ] Click "Start Crawl"
- [ ] Monitor progress bar
- [ ] Expected output:
  ```
  Starting crawl...
  Crawling X domains...
  
  Crawling 1/5: sverigesradio.se...
    ✓ Crawled 50 pages, 2 errors
  Crawling 2/5: svt.se...
    ✓ Crawled 45 pages, 1 error
  ...
  
  ✓ Crawl complete! Building index...
  ✓ Setup complete! Ready for Phase 2.
  ```
- [ ] Check pages saved: `ls -lh .klarsbdbdata/pages.json`
- [ ] Verify index created: `ls -lh .klarsbdbdata/index.json`

---

## Phase 2: Control Center

After Phase 1, Control Center window appears.

### Verify Status Display
- [ ] Database Path shown
- [ ] Setup Date displayed
- [ ] Pages Indexed shown (should match crawled count)
- [ ] Status shows "READY (Not Running)"

### Option 1: Start Server
- [ ] Click "START SERVER (localhost:8080)"
- [ ] Expected: Message shows server starting
- [ ] Window closes

### Option 2: Re-initialize (Test)
- [ ] Click "RE-INITIALIZE SETUP"
- [ ] Confirm dialog appears
- [ ] On confirmation, returns to Phase 1 setup wizard
- [ ] Click Cancel to return to Control Center

### Option 3: Scan Corruption
- [ ] Click "SCAN FOR CORRUPTION"
- [ ] Expected message:
  ```
  Database scan:
  ✓ File integrity: OK
  ✓ Index cross-references: OK
  ✓ Orphaned entries: 0
  
  Status: HEALTHY
  ```

---

## Phase 3: Runtime Dashboard

After clicking "START SERVER" in Phase 2.

### Server Startup Verification
```bash
# In another terminal, test the API
curl http://127.0.0.1:8080/api/health
```
Expected response:
```json
{"status": "healthy", "timestamp": "2026-01-22T15:00:00"}
```

### Dashboard Displays
- [ ] Title shows "Klar SBDB - ACTIVE RUNNING" (green text)
- [ ] Uptime displays (starts at 0d 00h 00m 00s)
- [ ] Search speed shown (default ~0.347s)
- [ ] Index statistics displayed
- [ ] Algorithm information visible
- [ ] Crawl monitoring section shown

### API Endpoints Testing

#### Test 1: Search
```bash
curl -X POST http://127.0.0.1:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Stockholm restaurang", "top_k": 5}'
```
Expected:
- [ ] Returns JSON with `results` array
- [ ] Each result has: `title`, `url`, `snippet`, `trust_score`, `region`, `domain`
- [ ] Response time < 1 second
- [ ] No errors in response

#### Test 2: Status
```bash
curl http://127.0.0.1:8080/api/status
```
Expected:
- [ ] Returns `{"status": "active", "uptime_seconds": N, "queries_served": N, ...}`
- [ ] Queries served increments after searches

#### Test 3: Stats
```bash
curl http://127.0.0.1:8080/api/stats
```
Expected:
- [ ] Returns index statistics
- [ ] Fields: `domains_total`, `domains_selected`, `pages_indexed`, `unique_keywords`, `index_size_mb`
- [ ] Numbers match crawled data

#### Test 4: Corruption Scan
```bash
curl -X POST http://127.0.0.1:8080/api/admin/corruption/scan
```
Expected:
- [ ] Returns diagnostic info
- [ ] Status is `HEALTHY`, `WARNINGS`, or `CORRUPTED`
- [ ] Lists all checks performed

---

## Client Integration Testing

### Update klarbrowser.py
Ensure client points to new backend:
```python
SERVER_URL = "http://127.0.0.1:8080"
```

### Test Client
```bash
# In new terminal, compile and run client
pyinstaller --onefile --windowed klarbrowser.py
./dist/klarbrowser.exe  # Windows
./dist/klarbrowser     # Linux/macOS
```

Expected:
- [ ] Client window opens
- [ ] Connection status shows "connected" (subtle indicator)
- [ ] Search box active
- [ ] Type search query (e.g., "Stockholm")
- [ ] Press Enter
- [ ] Results appear with titles, URLs, snippets
- [ ] No backend URLs visible to user
- [ ] Searches under 1 second

---

## Performance Benchmarking

### Search Latency
```bash
for i in {1..10}; do
  time curl -X POST http://127.0.0.1:8080/api/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test query '$i'", "top_k": 10}' > /dev/null
done
```

Expected:
- [ ] Average response time: 300-500ms
- [ ] P95 (worst 5%): < 1 second
- [ ] All queries return results

### Index Size
```bash
du -sh .klarsbdbdata/
ls -lh .klarsbdbdata/{pages,index,config,domains}.json
```

Expected:
- [ ] Total directory: ~5-10GB (varies by crawl size)
- [ ] Pages file: ~3-5GB
- [ ] Index file: ~1-2GB

### Memory Usage
```bash
ps aux | grep python  # Check memory (VIRT/RES columns)
```

Expected:
- [ ] VIRT (virtual): ~8GB
- [ ] RES (resident): ~4-6GB
- [ ] Stable (no growing leaks)

---

## Logging Verification

### Search Logs
```bash
jq '.[-5:]' .klarsbdbdata/logs/searchlog.json  # Last 5 searches
```

Expected:
- [ ] Each entry has: `timestamp`, `query`, `results_count`, `response_time_ms`

### Crawl Logs
```bash
jq '.' .klarsbdbdata/logs/crawllog.json
```

Expected:
- [ ] Entry for each crawl session
- [ ] Contains: `timestamp`, `stats` (domains, pages, errors)

### Error Logs
```bash
jq '.[]' .klarsbdbdata/logs/errorlog.json
```

Expected:
- [ ] Empty initially (or minimal errors)
- [ ] Any errors have: `timestamp`, `error` description

### Diagnostic Logs
```bash
jq '.' .klarsbdbdata/logs/diagnosticlog.json
```

Expected:
- [ ] Corruption scans recorded
- [ ] Each scan shows: `timestamp`, `status`, `checks`

---

## Troubleshooting

### Issue: "Port 8080 already in use"
**Solution:**
```bash
# Find process using port 8080
lsof -i :8080
# Kill the process
kill -9 <PID>
```

### Issue: "ModuleNotFoundError: No module named 'spacy'"
**Solution:**
```bash
pip install -r requirements.txt
python -m spacy download sv_core_news_sm
```

### Issue: "Slow search queries (> 5 seconds)"
**Possible causes:**
- [ ] Index not fully loaded into memory
- [ ] Too many concurrent queries
- [ ] Disk I/O bottleneck

**Solutions:**
- [ ] Restart server to reload index
- [ ] Increase `Max Concurrent Queries` in settings
- [ ] Use SSD instead of HDD
- [ ] Reduce index size (fewer crawled domains)

### Issue: "Database corruption detected"
**Solution:**
```bash
# Run corruption scan
curl -X POST http://127.0.0.1:8080/api/admin/corruption/scan

# If repair needed, restart and use Phase 2 Control Center
python run_v3.py
# Click "SCAN FOR CORRUPTION" -> "Repair"
```

### Issue: "Client cannot connect to server"
**Possible causes:**
- [ ] Server not running
- [ ] Firewall blocking port 8080
- [ ] Incorrect server URL in client

**Solutions:**
- [ ] Verify server running: `curl http://127.0.0.1:8080/api/health`
- [ ] Check firewall: `sudo ufw allow 8080` (Linux)
- [ ] Verify client URL: `SERVER_URL = "http://127.0.0.1:8080"`

---

## Production Go-Live Checklist

### Code
- [ ] All modules tested and working
- [ ] No TODO or FIXME comments in critical code
- [ ] Error handling implemented
- [ ] Logging comprehensive
- [ ] README and documentation complete

### Data
- [ ] Domains curated (safety checked)
- [ ] Initial crawl complete
- [ ] Index built and verified
- [ ] Backup of `.klarsbdbdata/` directory created

### Performance
- [ ] Search latency < 1 second P95
- [ ] Memory usage stable
- [ ] Disk space adequate
- [ ] CPU utilization < 80%

### API
- [ ] All endpoints tested
- [ ] Error responses appropriate
- [ ] Logging working
- [ ] Rate limiting considered (if needed)

### Client
- [ ] klarbrowser.py updated
- [ ] UI shows no backend URLs
- [ ] Connection status indicator working
- [ ] Results display correct

### Operations
- [ ] Startup/shutdown procedures documented
- [ ] Backup strategy defined
- [ ] Monitoring alerts configured
- [ ] On-call runbook prepared

---

## Post-Launch Monitoring

### Daily Checks
- [ ] Server uptime > 99%
- [ ] Average search speed stable
- [ ] Error rate < 0.1%
- [ ] Disk space not filling up

### Weekly Checks
- [ ] Change detection working (domains recrawled)
- [ ] Index size reasonable
- [ ] Query patterns normal
- [ ] Backup executed successfully

### Monthly Checks
- [ ] Corruption scans clean
- [ ] Performance benchmarks meet targets
- [ ] Domain trust scores reviewed
- [ ] New high-quality domains considered for addition

---

## Success Metrics

✅ **Phase 1**: Setup wizard completes, domains crawled, index built

✅ **Phase 2**: Server starts cleanly, all diagnostic checks pass

✅ **Phase 3**: Dashboard shows live stats, search < 1s, API responsive

✅ **Client**: Searches execute, results display, zero backend exposure

✅ **Production**: All tests passing, documentation complete, team trained

---

## Sign-Off

- Deployment Date: ____________
- Deployed By: ____________
- Verified By: ____________
- Notes: ____________

**Status: ☐ Ready for Production ☐ Requires Fixes**
