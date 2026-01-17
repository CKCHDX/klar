"""
Klar Engine Wrapper for Chaquopy (Python in Android)
This module wraps the Klar search engine for direct Kotlin calls
Platform-agnostic: works on Windows, Linux, and Android
"""

import json
import sys
import os
from pathlib import Path

# ============================================
# PLATFORM DETECTION & PATH SETUP
# ============================================
def detect_platform():
    """Detect if running on Android via Chaquopy"""
    try:
        import android
        return "android"
    except ImportError:
        return "desktop"

PLATFORM = detect_platform()

# Setup engine path based on platform
if PLATFORM == "android":
    # On Android, files are in app's data directory
    try:
        from android.app import PythonActivity
        app_dir = PythonActivity.mActivity.getFilesDir().toString()
        engine_path = Path(app_dir) / "engine"
    except:
        engine_path = Path(__file__).parent / "engine"
else:
    # On desktop, use relative path
    engine_path = Path(__file__).parent / "engine"

if engine_path.exists():
    sys.path.insert(0, str(engine_path))
    sys.path.insert(0, str(engine_path.parent))

# ============================================
# IMPORT KLAR MODULES
# ============================================
try:
    from search_engine import SearchEngine
    from demographic_detector import DemographicDetector
    from domain_whitelist import DomainWhitelist
    from loki_system import LOKISystem
    HAS_ENGINES = True
except ImportError as e:
    print(f"[WARN] Could not import engines: {e}")
    print(f"[DEBUG] Engine path: {engine_path}")
    print(f"[DEBUG] sys.path: {sys.path}")
    HAS_ENGINES = False


class KlarEngine:
    """Klar search engine wrapper for Android and Desktop"""
    
    def __init__(self):
        """Initialize Klar engine with platform detection"""
        self.search_engine = None
        self.demographic_detector = None
        self.whitelist = None
        self.loki = None
        self.platform = PLATFORM
        
        print(f"[INFO] KlarEngine initializing on {self.platform}")
        
        if HAS_ENGINES:
            try:
                self.search_engine = SearchEngine()
                self.demographic_detector = DemographicDetector()
                
                # Try to load whitelist
                domains_file = engine_path.parent / "domains.json"
                if not domains_file.exists():
                    domains_file = Path(__file__).parent / "domains.json"
                    
                if domains_file.exists():
                    self.whitelist = DomainWhitelist(str(domains_file))
                    print(f"[INFO] Whitelist loaded from {domains_file}")
                
                # Initialize LOKI with platform-appropriate path
                if self.platform == "android":
                    try:
                        from android.app import PythonActivity
                        context = PythonActivity.mActivity
                        files_dir = Path(context.getFilesDir().toString())
                        data_path = files_dir / "Klar-data"
                    except:
                        data_path = Path.home() / "Klar-data"
                else:
                    data_path = Path.home() / "Klar-data"
                
                data_path.mkdir(parents=True, exist_ok=True)
                
                try:
                    self.loki = LOKISystem(str(data_path))
                    print(f"[INFO] LOKI initialized at {data_path}")
                except Exception as e:
                    print(f"[WARN] LOKI initialization failed: {e}")
                    self.loki = None
                    
            except Exception as e:
                print(f"[ERROR] Klar init failed: {e}")
                import traceback
                traceback.print_exc()
    
    def search(self, query):
        """
        Perform search query
        Returns JSON string with results
        """
        if not self.search_engine:
            return json.dumps({"error": "Engine not initialized"})
        
        try:
            query = query.strip()
            if not query:
                return json.dumps({"error": "Empty query"})
            
            # Detect demographic
            demographic = "general"
            confidence = 0.0
            
            if self.demographic_detector:
                try:
                    demographic, confidence, _ = self.demographic_detector.detect(query)
                except:
                    pass
            
            # Perform search
            results = self.search_engine.search(query, demographic=demographic)
            
            # Format response
            response = {
                "query": query,
                "detected_demographic": demographic,
                "confidence": float(confidence) if confidence else 0.0,
                "results": results.get("results", []) if isinstance(results, dict) else [],
                "total": len(results.get("results", [])) if isinstance(results, dict) else 0
            }
            
            # Cache in LOKI if available
            if self.loki:
                try:
                    self.loki.cache_page({
                        "url": f"search:{query}",
                        "title": f"Search: {query}",
                        "content": json.dumps(response)[:10000]
                    })
                except:
                    pass
            
            return json.dumps(response, ensure_ascii=False)
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "query": query
            })
    
    def offline_search(self, query):
        """
        Search offline cache (LOKI)
        Returns JSON string with results
        """
        if not self.loki:
            return json.dumps({"error": "LOKI not available"})
        
        try:
            results = self.loki.search(query)
            return json.dumps({
                "query": query,
                "offline": True,
                "results": results,
                "total": len(results) if results else 0
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def check_url(self, url):
        """Check if URL is whitelisted"""
        if not self.whitelist:
            return json.dumps({"whitelisted": True})  # Default allow
        
        try:
            is_allowed, reason = self.whitelist.is_whitelisted(url)
            return json.dumps({
                "url": url,
                "whitelisted": is_allowed,
                "reason": reason
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def get_status(self):
        """Get engine status"""
        return json.dumps({
            "version": "3.1",
            "platform": self.platform,
            "initialized": self.search_engine is not None,
            "loki_enabled": self.loki is not None,
            "has_whitelist": self.whitelist is not None
        })
