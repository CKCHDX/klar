"""
Domain-Specific Cookie Handlers for Klar Browser
Each domain has custom JavaScript to handle its specific cookie popup
"""

import json


class DomainHandlers:
    """Manages per-domain cookie handling strategies"""
    
    def __init__(self):
        """Initialize handlers"""
        self.handlers = self._init_handlers()
    
    def _init_handlers(self) -> dict:
        """Initialize all domain-specific handlers"""
        return {
            # Swedish sites that WORK with universal handler
            "svt.se": self._universal_handler("decline_all"),
            "dn.se": self._universal_handler("decline_all"),
            
            # Swedish sites that need specific handling
            "aftonbladet.se": self._aftonbladet_handler(),
            "shl.se": self._shl_handler(),
            
            # Streaming/Music
            "spotify.com": self._spotify_handler(),
            "open.spotify.com": self._spotify_handler(),
            
            # Default for unknown sites
            "default": self._universal_handler("decline_all")
        }
    
    def get_handler_for_domain(self, domain: str) -> str:
        """Get the JavaScript handler for a domain"""
        domain = domain.lower().replace('www.', '')
        
        if domain in self.handlers:
            print(f"[DomainHandler] Using custom handler for {domain}")
            return self.handlers[domain]
        
        # Try base domain
        parts = domain.split('.')
        if len(parts) >= 2:
            base = '.'.join(parts[-2:])
            if base in self.handlers:
                print(f"[DomainHandler] Using handler for base domain {base}")
                return self.handlers[base]
        
        print(f"[DomainHandler] Using default handler for {domain}")
        return self.handlers["default"]
    
    def _universal_handler(self, action: str = "decline_all") -> str:
        """Generic handler that works for most sites"""
        return f"""
        (function() {{
            console.log('[Klar] Universal handler: {action}');
            
            function normalizeText(text) {{
                return text.toLowerCase().trim();
            }}
            
            function findButton(keywords) {{
                var buttons = document.querySelectorAll('button, [role="button"]');
                for (var i = 0; i < buttons.length; i++) {{
                    var text = normalizeText(buttons[i].textContent || buttons[i].innerText || '');
                    for (var j = 0; j < keywords.length; j++) {{
                        if (text.indexOf(normalizeText(keywords[j])) !== -1) {{
                            return buttons[i];
                        }}
                    }}
                }}
                return null;
            }}
            
            setTimeout(function() {{
                var keywords = {json.dumps(['decline', 'reject', 'avvisa', 'neka', 'refuse', 'deny'])};
                var btn = findButton(keywords);
                if (btn) {{
                    console.log('[Klar] Clicking decline button');
                    btn.click();
                }} else {{
                    // Fallback: accept all
                    keywords = {json.dumps(['accept', 'acceptera', 'godkänn', 'agree', 'ok'])};
                    btn = findButton(keywords);
                    if (btn) {{
                        console.log('[Klar] Clicking accept button (fallback)');
                        btn.click();
                    }}
                }}
                
                // Hide remaining popups
                setTimeout(function() {{
                    document.querySelectorAll('[class*="cookie"], [id*="cookie"], [role="dialog"]').forEach(function(el) {{
                        if (el.offsetHeight > 0) el.style.display = 'none !important';
                    }});
                }}, 100);
            }}, 500);
        }})();
        """
    
    def _aftonbladet_handler(self) -> str:
        """Aftonbladet-specific handler"""
        return """
        (function() {
            console.log('[Klar] Aftonbladet handler start');

            function normalize(text) {
                return (text || '').toLowerCase().trim();
            }

            setTimeout(function() {
                var buttons = document.querySelectorAll('button, [role="button"]');
                console.log('[Klar] Aftonbladet: found ' + buttons.length + ' buttons');

                var target = null;

                for (var i = 0; i < buttons.length; i++) {
                    var b = buttons[i];
                    var text = normalize(b.textContent || b.innerText);
                    var aria = normalize(b.getAttribute('aria-label'));

                    // Match "Godkänn alla cookies" in text or aria-label
                    if (text.indexOf('godkänn alla cookies') !== -1 ||
                        aria.indexOf('godkänn alla cookies') !== -1) {
                        target = b;
                        break;
                    }
                }

                if (target) {
                    console.log('[Klar] Aftonbladet: clicking \"Godkänn alla cookies\"');
                    target.click();
                } else {
                    console.log('[Klar] Aftonbladet: button not found');
                }

                // Hide remaining cookie UI as fallback
                setTimeout(function() {
                    var sel = '[class*=\"cookie\"], [id*=\"cookie\"], [class*=\"consent\"], [role=\"dialog\"]';
                    document.querySelectorAll(sel).forEach(function(el) {
                        if (el.offsetHeight > 0) {
                            el.style.display = 'none !important';
                            el.style.visibility = 'hidden !important';
                        }
                    });
                }, 200);

            }, 700); // wait for popup to render
        })();
        """

    
    def _spotify_handler(self) -> str:
        """Spotify-specific handler"""
        return """
        (function() {
            console.log('[Klar] Spotify handler');
            
            setTimeout(function() {
                var buttons = document.querySelectorAll('button');
                var found = false;
                
                // Look for "REJECT ALL" button (all caps on Spotify)
                for (var i = 0; i < buttons.length; i++) {
                    var text = buttons[i].textContent.toUpperCase();
                    
                    if (text.indexOf('REJECT ALL') !== -1) {
                        console.log('[Klar] Found REJECT ALL button');
                        buttons[i].click();
                        found = true;
                        break;
                    }
                }
                
                // Fallback: look for any reject button
                if (!found) {
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].textContent.toLowerCase();
                        if ((text.indexOf('reject') !== -1 || text.indexOf('decline') !== -1) && text.length < 30) {
                            console.log('[Klar] Found reject/decline button');
                            buttons[i].click();
                            found = true;
                            break;
                        }
                    }
                }
                
                console.log('[Klar] Spotify handler complete, found=' + found);
                
            }, 800);
        })();
        """
    
    def _shl_handler(self) -> str:
        """SHL (Swedish Hockey League) handler"""
        return """
        (function() {
            console.log('[Klar] SHL handler');
            
            setTimeout(function() {
                // SHL uses different cookie popup structure
                var buttons = document.querySelectorAll('button');
                
                // Try to find Inställningar (Settings) button first
                for (var i = 0; i < buttons.length; i++) {
                    var text = buttons[i].textContent.toLowerCase();
                    if (text.indexOf('inställning') !== -1 || text.indexOf('settings') !== -1) {
                        console.log('[Klar] Found settings button');
                        buttons[i].click();
                        
                        // After clicking settings, find and click reject
                        setTimeout(function() {
                            var settingsButtons = document.querySelectorAll('button');
                            for (var j = 0; j < settingsButtons.length; j++) {
                                var settingsText = settingsButtons[j].textContent.toLowerCase();
                                if (settingsText.indexOf('avvisa') !== -1 || settingsText.indexOf('reject') !== -1) {
                                    console.log('[Klar] Clicking reject in settings');
                                    settingsButtons[j].click();
                                    break;
                                }
                            }
                        }, 300);
                        break;
                    }
                }
                
                // Hide popups
                setTimeout(function() {
                    document.querySelectorAll('[class*="cookie"], [role="dialog"]').forEach(function(el) {
                        if (el.offsetHeight > 0) el.style.display = 'none !important';
                    });
                }, 500);
                
            }, 700);
        })();
        """
