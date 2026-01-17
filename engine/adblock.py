"""
Klar AdBlock Engine
Lightweight ad/tracker blocking via rule engine + cosmetic filters.
Designed for school/government institutional use.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse

class AdBlockRules:
    """
    Load and manage ad blocking rules.
    Format: JSON with 'hosts', 'patterns', 'exceptions'.
    """
    
    def __init__(self, rules_file: Path = None):
        self.hosts: set = set()  # Exact host matches: ads.google.com
        self.patterns: List[re.Pattern] = []  # Regex patterns for URLs
        self.exceptions: set = set()  # URLs/hosts to never block
        self.cosmetic_selectors: List[str] = []  # CSS selectors to hide
        
        if rules_file and rules_file.exists():
            self.load_from_file(rules_file)
        else:
            self.load_defaults()
    
    def load_defaults(self):
        """Load built-in minimal rules (until you have a full list)."""
        # Core trackers & ad networks (Swedish + international)
        self.hosts = {
            # Google ad ecosystem
            "ads.google.com", "googleadservices.com", "googlesyndication.com",
            "google-analytics.com", "www.google-analytics.com",
            "analytics.google.com", "google.com:443",
            
            # Facebook tracking
            "connect.facebook.net", "facebook.com", "pixel.facebook.com",
            
            # Major ad networks
            "doubleclick.net", "adnxs.com", "criteo.com", "taboola.com",
            "outbrain.com", "scorecardresearch.com",
            
            # Swedish media ad servers
            "ad.abc.se", "ads.aftonbladet.se", "adserver.se",
            "adx.se", "adsbox.se",
            
            # Analytics & tracking
            "segment.com", "mix.com", "mixpanel.com", "amplitude.com",
            "hotjar.com", "mouseflow.com", "contentsquare.com",
        }
        
        # Patterns for URLs containing ad indicators
        patterns_str = [
            r".*\/ads\/.*",
            r".*\/ad\.js.*",
            r".*\/adserver\/.*",
            r".*\/(advertise|advertising|advert).*",
            r".*tracking\.js.*",
            r".*tracker\.js.*",
            r".*beacon.*",
            r".*pixel\.gif.*",
            r".*(google)?ads.*",
        ]
        
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns_str]
        
        # Hosts we never block (even if they match a pattern)
        self.exceptions = {
            "github.com", "stackoverflow.com", "wikipedia.org",
            "svt.se", "polisen.se", "regeringen.se",
        }
        
        # Cosmetic selectors (CSS classes/IDs to hide)
        self.cosmetic_selectors = [
            "[class*='ad-']", "[id*='ad-']", "[class*='ads-']", "[id*='ads-']",
            "[class*='annons']", "[id*='annons']",  # Swedish for "ad"
            "[class*='advertisement']", "[id*='advertisement']",
            "[class*='advert']", "[id*='advert']",
            "[class*='sponsored']", "[class*='sponsrat']",  # Swedish for "sponsored"
            "[data-ad-slot]", "[data-adslot]",
            "iframe[src*='ads']", "iframe[src*='doubleclick']",
            "[aria-label*='Annons']", "[aria-label*='annons']",
        ]
    
    def load_from_file(self, path: Path):
        """Load rules from JSON file (for future expansion to real filter lists)."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.hosts = set(data.get('hosts', []))
            self.exceptions = set(data.get('exceptions', []))
            self.cosmetic_selectors = data.get('cosmetic_selectors', [])
            patterns = data.get('patterns', [])
            self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        except Exception as e:
            print(f"[AdBlock] Error loading rules from {path}: {e}")
            self.load_defaults()


class AdBlocker:
    """
    Main ad blocker: decide whether to block a request.
    """
    
    def __init__(self, rules: AdBlockRules = None):
        self.rules = rules or AdBlockRules()
        self.blocked_requests: Dict[str, int] = {}  # For stats
    
    def should_block(self, url: str, first_party: str = None, 
                     resource_type: str = None) -> Tuple[bool, Optional[str]]:
        """
        Determine if a request should be blocked.
        
        Returns:
            (block: bool, reason: str or None)
        """
        
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            path = (parsed.path or "").lower()
            
            # 1. Check if host is in exception list
            if host in self.rules.exceptions:
                return False, None
            
            # 2. Check first-party: never block same-domain requests
            if first_party:
                fp_parsed = urlparse(first_party)
                fp_host = (fp_parsed.hostname or "").lower()
                # Remove 'www.' for comparison
                if host.replace("www.", "") == fp_host.replace("www.", ""):
                    return False, None
            
            # 3. Check exact host match
            for blocked_host in self.rules.hosts:
                if host == blocked_host or host.endswith("." + blocked_host):
                    reason = f"host_match: {blocked_host}"
                    self.blocked_requests[url] = self.blocked_requests.get(url, 0) + 1
                    return True, reason
            
            # 4. Check URL path patterns
            full_url = url.lower()
            for pattern in self.rules.patterns:
                if pattern.match(full_url):
                    reason = f"pattern_match"
                    self.blocked_requests[url] = self.blocked_requests.get(url, 0) + 1
                    return True, reason
            
            # 5. Heuristic: very small images + ad keywords = likely tracking pixel
            if resource_type in ["image", "img"]:
                if "pixel" in path or "beacon" in path or "tracker" in path:
                    reason = "tracking_pixel"
                    self.blocked_requests[url] = self.blocked_requests.get(url, 0) + 1
                    return True, reason
            
            return False, None
        
        except Exception as e:
            print(f"[AdBlock] Error in should_block: {e}")
            return False, None
    
    def get_cosmetic_filters_js(self) -> str:
        """
        Generate JavaScript code to hide ad containers via CSS.
        Run this on loadFinished to kill visual ad placeholders.
        """
        
        selectors_json = json.dumps(self.rules.cosmetic_selectors)
        
        js_code = fr"""
(function() {{
    function hideAdContainers() {{
        var selectors = {selectors_json};
        var hidden = 0;
        
        selectors.forEach(function(sel) {{
            try {{
                var elements = document.querySelectorAll(sel);
                elements.forEach(function(el) {{
                    el.style.setProperty("display", "none", "important");
                    el.style.setProperty("visibility", "hidden", "important");
                    hidden++;
                }});
            }} catch (e) {{
                console.log('[Klar AdBlock] Error with selector: ' + sel);
            }}
        }});
        
        if (hidden > 0) {{
            console.log('[Klar AdBlock] Hidden ' + hidden + ' ad containers');
        }}
    }}
    
    // Initial run
    hideAdContainers();
    
    // Re-run after dynamic content loads
    setTimeout(hideAdContainers, 2000);
    
    // Observe for lazy-loaded ads
    try {{
        var observer = new MutationObserver(function(mutations) {{
            hideAdContainers();
        }});
        observer.observe(document.documentElement || document.body, {{
            childList: true,
            subtree: true
        }});
    }} catch (e) {{
        console.log('[Klar AdBlock] MutationObserver not available');
    }}
}})();
"""
        return js_code
    
    def get_stats(self) -> dict:
        """Return blocking statistics."""
        return {
            "total_rules_loaded": len(self.rules.hosts) + len(self.rules.patterns),
            "total_host_rules": len(self.rules.hosts),
            "total_pattern_rules": len(self.rules.patterns),
            "unique_blocked_urls": len(self.blocked_requests),
            "total_blocks": sum(self.blocked_requests.values()),
        }
