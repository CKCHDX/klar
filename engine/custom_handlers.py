"""
Custom Handlers for Klar Browser
User-defined handlers for sites not covered by the cookie banners database
"""

import json
from pathlib import Path


class CustomHandlers:
    """Manages custom per-site handlers"""
    
    def __init__(self, data_path: str = None):
        """Initialize custom handlers"""
        self.data_path = Path(data_path) if data_path else Path.home() / "Klar-data"
        self.handlers_file = self.data_path / "custom_cookie_handlers.json"
        self.handlers = self._load_handlers()
    
    def _load_handlers(self) -> dict:
        """Load custom handlers from file"""
        if self.handlers_file.exists():
            try:
                with open(self.handlers_file, 'r', encoding='utf-8') as f:
                    handlers = json.load(f)
                    print(f"[CustomHandlers] Loaded {len(handlers)} custom handlers")
                    return handlers
            except Exception as e:
                print(f"[CustomHandlers] Error loading: {e}")
        
        # Return default empty handlers with examples
        defaults = {
            "aftonbladet.se": {
                "description": "Aftonbladet - Swedish newspaper",
                "button_text": "Godkänn alla cookies",
                "button_class": "message-button",
                "js": """
                // Aftonbladet custom handler
                (function() {
                    console.log('[Klar] Aftonbladet handler');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent.toLowerCase();
                            if (text.indexOf('godkänn alla cookies') !== -1) {
                                console.log('[Klar] Clicking Godkänn alla cookies');
                                buttons[i].click();
                                break;
                            }
                        }
                        // Hide popup
                        setTimeout(function() {
                            document.querySelectorAll('[role="dialog"]').forEach(function(el) {
                                el.style.display = 'none !important';
                            });
                        }, 100);
                    }, 700);
                })();
                """
            },
            "spotify.com": {
                "description": "Spotify - Music streaming",
                "button_text": "REJECT ALL",
                "js": """
                // Spotify custom handler
                (function() {
                    console.log('[Klar] Spotify handler');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent.toUpperCase();
                            if (text.indexOf('REJECT ALL') !== -1) {
                                console.log('[Klar] Clicking REJECT ALL');
                                buttons[i].click();
                                break;
                            }
                        }
                    }, 800);
                })();
                """
            },
            "open.spotify.com": {
                "description": "Spotify Web - Music streaming",
                "button_text": "REJECT ALL",
                "js": """
                // Spotify Web custom handler
                (function() {
                    console.log('[Klar] Spotify Web handler');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent.toUpperCase();
                            if (text.indexOf('REJECT ALL') !== -1) {
                                console.log('[Klar] Clicking REJECT ALL');
                                buttons[i].click();
                                break;
                            }
                        }
                    }, 800);
                })();
                """
            },
            "ur.se": {
                "description": "UR - Swedish education broadcaster",
                "button_text": "Avvisa alla",
                "js": """
                // UR custom handler
                (function() {
                    console.log('[Klar] UR handler');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent.toLowerCase();
                            // Try to find decline button
                            if (text.indexOf('avvisa') !== -1) {
                                console.log('[Klar] Clicking Avvisa');
                                buttons[i].click();
                                break;
                            }
                        }
                        // Hide popup as fallback
                        setTimeout(function() {
                            document.querySelectorAll('[class*="cookie"], [role="dialog"]').forEach(function(el) {
                                el.style.display = 'none !important';
                            });
                        }, 100);
                    }, 700);
                })();
                """
            },
            "svtplay.se": {
                "description": "SVT Play - Swedish streaming",
                "button_text": "Avvisa alla cookies",
                "js": """
                // SVT Play custom handler
                (function() {
                    console.log('[Klar] SVT Play handler');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent.toLowerCase();
                            if (text.indexOf('avvisa alla') !== -1 && text.indexOf('cookie') !== -1) {
                                console.log('[Klar] Clicking decline');
                                buttons[i].click();
                                break;
                            }
                        }
                    }, 700);
                })();
                """
            },
            "netonnet.se": {
                "description": "NetOnNet - Swedish electronics retailer",
                "button_text": "Avsluta",
                "js": """
                // NetOnNet custom handler
                (function() {
                    console.log('[Klar] NetOnNet handler');
                    setTimeout(function() {
                        // Try close button first
                        var closeBtn = document.querySelector('button[aria-label*="Stäng"], button[aria-label*="Close"]');
                        if (closeBtn) {
                            closeBtn.click();
                            console.log('[Klar] NetOnNet: clicked close');
                        } else {
                            // Find and click accept essential
                            var buttons = document.querySelectorAll('button');
                            for (var i = 0; i < buttons.length; i++) {
                                var text = buttons[i].textContent.toLowerCase();
                                if (text.indexOf('avsluta') !== -1 || text.indexOf('accept') !== -1) {
                                    buttons[i].click();
                                    break;
                                }
                            }
                        }
                    }, 700);
                })();
                """
            },
            "sj.se": {
                "description": "SJ - Swedish railways",
                "button_text": "Close / Stäng",
                "js": """
                // SJ custom handler
                (function() {
                    console.log('[Klar] SJ handler');
                    setTimeout(function() {
                        // Look for close button
                        var closeBtn = document.querySelector('button[class*="close"], button[aria-label*="close"]');
                        if (closeBtn) {
                            closeBtn.click();
                            console.log('[Klar] SJ: clicked close');
                        } else {
                            // Look for accept button
                            var buttons = document.querySelectorAll('button');
                            for (var i = 0; i < buttons.length; i++) {
                                var text = buttons[i].textContent.toLowerCase();
                                if (text.indexOf('acceptera') !== -1 || text.indexOf('godkänn') !== -1) {
                                    buttons[i].click();
                                    break;
                                }
                            }
                        }
                        // Hide modal
                        setTimeout(function() {
                            document.querySelectorAll('[role="dialog"]').forEach(function(el) {
                                el.style.display = 'none !important';
                            });
                        }, 200);
                    }, 700);
                })();
                """
            }
        }
        
        self._save_handlers(defaults)
        return defaults
    
    def _save_handlers(self, handlers: dict):
        """Save handlers to file"""
        try:
            self.data_path.mkdir(parents=True, exist_ok=True)
            with open(self.handlers_file, 'w', encoding='utf-8') as f:
                json.dump(handlers, f, indent=2, ensure_ascii=False)
                print(f"[CustomHandlers] Saved handlers to {self.handlers_file}")
        except Exception as e:
            print(f"[CustomHandlers] Error saving: {e}")
    
    def get_handler(self, domain: str) -> str:
        """Get custom handler for a domain"""
        domain = domain.lower().replace('www.', '')
        
        if domain in self.handlers:
            handler = self.handlers[domain]
            print(f"[CustomHandlers] Using handler for {domain}: {handler.get('description', '')}")
            return handler.get('js', '')
        
        # Try base domain
        parts = domain.split('.')
        if len(parts) >= 2:
            base = '.'.join(parts[-2:])
            if base in self.handlers:
                handler = self.handlers[base]
                print(f"[CustomHandlers] Using handler for base domain {base}")
                return handler.get('js', '')
        
        return None
    
    def add_handler(self, domain: str, js_code: str, description: str = ""):
        """Add a new custom handler"""
        domain = domain.lower()
        
        self.handlers[domain] = {
            "description": description,
            "js": js_code,
            "added": str(__import__('datetime').datetime.now().isoformat())
        }
        
        self._save_handlers(self.handlers)
        print(f"[CustomHandlers] Added handler for {domain}")
    
    def list_handlers(self) -> list:
        """List all custom handlers"""
        return [
            {"domain": domain, **handler}
            for domain, handler in self.handlers.items()
        ]
