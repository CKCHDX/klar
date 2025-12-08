# Klar 3.1 Windows Edition - Implementation Guide

## Quick Start

This guide explains how to integrate the new security and search enhancement modules into your Windows Klar browser.

---

## Files Added

### 1. `engine/domain_whitelist.py` (NEW)
**Purpose:** Enforce whitelist-only access to 111 Swedish domains

**Key Features:**
- URL validation against `domains.json`
- User-friendly Swedish security warning pages
- Subdomain handling
- Statistics tracking

**Usage:**
```python
from engine.domain_whitelist import DomainWhitelist

whitelist = DomainWhitelist("domains.json")
is_safe, reason = whitelist.is_whitelisted("https://google.com")

if not is_safe:
    blocked_html = whitelist.get_blocked_html(url, reason)
    browser.setHtml(blocked_html)
```

### 2. `engine/demographic_detector.py` (NEW)
**Purpose:** Detect user demographic to optimize search results

**Key Features:**
- 5 demographic profiles (seniors, women, men, teens, young adults)
- Keyword-based demographic detection
- Optimization hints for each demographic
- Detection history and statistics

**Usage:**
```python
from engine.demographic_detector import DemographicDetector

detector = DemographicDetector()
demographic, confidence, metadata = detector.detect("ont i bröstet")
# Returns: ('seniors_65plus', 0.75, {...})

hints = detector.get_optimization_hints(demographic)
# Returns result count, snippet length, etc. for that demographic
```

---

## Integration with klar_browser.py

### Step 1: Import New Modules

Add to the top of `klar_browser.py`:

```python
from engine.domain_whitelist import DomainWhitelist
from engine.demographic_detector import DemographicDetector
```

### Step 2: Initialize in KlarBrowser.__init__()

```python
def __init__(self):
    super().__init__()
    # ... existing code ...
    
    # NEW: Initialize security and search enhancement
    self.whitelist = DomainWhitelist("domains.json")
    self.demographic_detector = DemographicDetector()
```

### Step 3: Modify navigate_to_url() Method

**BEFORE:**
```python
def navigate_to_url(self):
    query = self.main_search_bar.text().strip()
    
    if not query:
        return
    
    # Check if it's a URL
    if self.is_url(query):
        url = query if query.startswith('http') else 'https://' + query
        self.current_browser().setUrl(QUrl(url))
        self.stacked_widget.setCurrentIndex(1)
    else:
        # It's a search query
        self.perform_search(query)
```

**AFTER:**
```python
def navigate_to_url(self):
    query = self.main_search_bar.text().strip()
    
    if not query:
        return
    
    # Check if it's a URL
    if self.is_url(query):
        # NEW: Check whitelist first
        is_safe, reason = self.whitelist.is_whitelisted(query)
        
        if not is_safe:
            # Show security warning page
            blocked_html = self.whitelist.get_blocked_html(query, reason)
            self.current_browser().setHtml(blocked_html, QUrl("about:blank"))
            self.stacked_widget.setCurrentIndex(1)
            self.status.showMessage(f"⚠️ Domän blockerad för säkerhet", 5000)
        else:
            # Domain is whitelisted, load it
            url = query if query.startswith('http') else 'https://' + query
            self.current_browser().setUrl(QUrl(url))
            self.stacked_widget.setCurrentIndex(1)
    else:
        # It's a search query
        self.perform_search(query)
```

### Step 4: Modify perform_search() Method

**BEFORE:**
```python
def perform_search(self, query):
    if self.is_searching:
        self.status.showMessage("Sökning pågår redan...", 2000)
        return
    
    self.is_searching = True
    self.status.showMessage(f"Söker efter: {query}...")
    
    # Show loading in browser
    self.show_loading_page(query)
    self.stacked_widget.setCurrentIndex(1)
    
    # Start background search
    self.search_worker = SearchWorker(self.search_engine, query)
    self.search_worker.finished.connect(self.on_search_finished)
    self.search_worker.error.connect(self.on_search_error)
    self.search_worker.start()
```

**AFTER:**
```python
def perform_search(self, query):
    if self.is_searching:
        self.status.showMessage("Sökning pågår redan...", 2000)
        return
    
    self.is_searching = True
    
    # NEW: Detect user demographic
    demographic, confidence, metadata = self.demographic_detector.detect(query)
    
    self.status.showMessage(f"Söker efter: {query}...")
    
    # Show loading in browser
    self.show_loading_page(query)
    self.stacked_widget.setCurrentIndex(1)
    
    # Start background search with demographic context
    # Pass demographic to search engine for optimized results
    self.search_worker = SearchWorker(
        self.search_engine, 
        query,
        demographic=demographic,
        metadata=metadata
    )
    self.search_worker.finished.connect(self.on_search_finished)
    self.search_worker.error.connect(self.on_search_error)
    self.search_worker.start()
```

### Step 5: Update SearchWorker Class

**BEFORE:**
```python
class SearchWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, search_engine, query):
        super().__init__()
        self.search_engine = search_engine
        self.query = query
    
    def run(self):
        try:
            results = self.search_engine.search(self.query)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
```

**AFTER:**
```python
class SearchWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, search_engine, query, demographic="general", metadata=None):
        super().__init__()
        self.search_engine = search_engine
        self.query = query
        self.demographic = demographic
        self.metadata = metadata or {}
    
    def run(self):
        try:
            # NEW: Pass demographic context to search engine
            results = self.search_engine.search(
                self.query,
                demographic=self.demographic
            )
            results['detected_demographic'] = self.demographic
            results['confidence'] = self.metadata
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
```

---

## Enhanced Search Engine (Existing)

Modify `engine/search_engine.py` to accept demographic parameter:

```python
def search(self, query: str, demographic: str = "general") -> dict:
    """
    Perform search with demographic-aware optimization.
    
    Args:
        query: Search query
        demographic: Detected user demographic
    
    Returns:
        Dict with optimized results for demographic
    """
    results = self._find_results(query)
    
    # Get optimization hints for this demographic
    if hasattr(self, 'demographic_detector'):
        hints = self.demographic_detector.get_optimization_hints(demographic)
        
        # Apply optimization:
        # - Limit result count based on demographic
        # - Adjust snippet length
        # - Prioritize safe domains for vulnerable groups
        results = results[:hints.get('result_count', 10)]
    
    return results
```

---

## Database Updates

### Expanded keywords_db.json

The current `keywords_db.json` needs to be expanded from ~500 to 3000+ keywords.

**Categories to add:**
1. Regional news (8 regions)
2. Regional services (4 cities)
3. Age-specific health
4. Hobby-specific topics
5. Shopping/comparison keywords
6. Entertainment categories

**Each keyword entry should include:**
```json
{
  "category": "name",
  "keywords": ["keyword1", "keyword2"],
  "priority_domains": ["domain.se"],
  "demographic_relevance": {
    "seniors_65plus": 0.9,
    "women_general": 0.3,
    "men_general": 0.5,
    "teens_10to20": 0.2,
    "young_adults_20to40": 0.8
  }
}
```

---

## Testing Checklist

### Security Tests
- [ ] Try to visit `google.com` → Shows security warning ✓
- [ ] Try to visit `svt.se` → Loads normally ✓
- [ ] Try URL with `www.svt.se` → Works ✓
- [ ] Try subdomain `nyheter.svt.se` → Works ✓
- [ ] Try typo `googlel.com` → Shows security warning ✓

### Demographic Detection Tests
- [ ] Senior query: "ont i bröstet" → Detects seniors_65plus ✓
- [ ] Teen query: "läxhjälp matematik" → Detects teens_10to20 ✓
- [ ] Woman query: "bästa makeup" → Detects women_general ✓
- [ ] Man query: "gaming dator" → Detects men_general ✓
- [ ] Young adult query: "först gången köpa lägenhet" → Detects young_adults_20to40 ✓

### Search Results Tests
- [ ] Results prioritize detected demographic's domains ✓
- [ ] Seniors see fewer, more detailed results ✓
- [ ] Safety warning only shown for blocked domains ✓
- [ ] No crashes with edge cases ✓
- [ ] Fast search response (<3 seconds) ✓

---

## Performance Notes

**Whitelist Lookup:** O(1) hash set lookup → ~1ms
**Demographic Detection:** Linear keyword matching → ~5-10ms  
**Search:** Existing algorithm + demographic weighting → <3 seconds total

**No performance degradation expected.**

---

## Debugging

### Enable Debug Logging

Add to `klar_browser.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Klar')

# In navigate_to_url():
logger.debug(f"URL validation: {query}")
logger.debug(f"Whitelist result: {is_safe}")

# In perform_search():
logger.debug(f"Detected demographic: {demographic} (confidence: {confidence})")
```

### Check Whitelist Status

```python
stats = self.whitelist.get_statistics()
print(f"Total whitelisted: {stats['total_whitelisted']}")
print(f"Blocked ratio: {stats['block_rate']:.2%}")
```

### Check Demographic Statistics

```python
stats = self.demographic_detector.get_statistics()
print(f"Total detections: {stats['total_detections']}")
print(f"Demographics found: {stats['demographics_found']}")
print(f"Most common: {stats['most_common']}")
```

---

## Next Steps

1. **Integrate modules** (estimated 2-3 hours)
2. **Expand keywords_db.json** to 3000+ keywords (2-3 hours)
3. **Test security layer** thoroughly (1-2 hours)
4. **Test demographic detection** with real users (2-3 hours)
5. **Optimize search ranking** based on feedback (ongoing)
6. **Create user documentation** in Swedish (1-2 hours)

---

## Support

For questions or issues:
1. Check `demographic_detector.py` docstrings
2. Review `domain_whitelist.py` for security logic
3. Test with provided test cases
4. Check GitHub issues on CKCHDX/klar

**Version:** 3.1 Implementation Guide
**Status:** Ready for integration
**Last Updated:** 2025-12-08
