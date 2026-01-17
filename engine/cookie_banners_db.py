"""
Cookie Banner Database for Klar Browser
Stores known cookie banner services and how to handle them
Based on: Cookie Auto Decline Firefox addon approach
"""

import json


class CookieBannersDB:
    """Database of known cookie banner services and their handlers"""
    
    def __init__(self):
        """Initialize banner database"""
        self.banners = self._init_banners()
    
    def _init_banners(self) -> dict:
        """Initialize known cookie banner patterns"""
        return {
            # OneTrust (used by 50k+ sites)
            "onetrust": {
                "name": "OneTrust",
                "patterns": ["onetrust", "cdn.cookielaw.org", "consent.oneitrust"],
                "selectors": {
                    "decline": [
                        "button[id*='onetrust-reject']",
                        "button.onetrust-pc-dark-filter-reject",
                        "[data-testid='ot-sdk-btn-reject']",
                        "button:contains('Reject')",
                        "button:contains('Avvisa')"
                    ],
                    "accept": [
                        "button[id*='onetrust-accept']",
                        "button.onetrust-pc-dark-filter-accept",
                        "[data-testid='ot-sdk-btn-accept']",
                        "button:contains('Accept')"
                    ]
                },
                "js": """
                // OneTrust
                (function() {
                    console.log('[Klar] OneTrust banner detected');
                    setTimeout(function() {
                        var rejectBtn = document.querySelector('[id*="onetrust-reject"], button.onetrust-pc-dark-filter-reject, [data-testid="ot-sdk-btn-reject"]');
                        if (rejectBtn && rejectBtn.offsetHeight > 0) {
                            rejectBtn.click();
                            console.log('[Klar] OneTrust: clicked reject');
                        } else {
                            var acceptBtn = document.querySelector('[id*="onetrust-accept"]');
                            if (acceptBtn) acceptBtn.click();
                        }
                    }, 500);
                })();
                """
            },
            
            # CookieBot (used by 100k+ sites)
            "cookiebot": {
                "name": "CookieBot",
                "patterns": ["cookiebot", "cdn.cookiebot.com"],
                "selectors": {
                    "decline": [
                        "button#CookiebotDialogBodyLevelButtonReject",
                        ".cm__close",
                        "button[aria-label*='Reject']"
                    ],
                    "accept": [
                        "button#CookiebotDialogBodyLevelButtonAccept"
                    ]
                },
                "js": """
                // CookieBot
                (function() {
                    console.log('[Klar] CookieBot banner detected');
                    setTimeout(function() {
                        var rejectBtn = document.querySelector('#CookiebotDialogBodyLevelButtonReject, .cm__close');
                        if (rejectBtn && rejectBtn.offsetHeight > 0) {
                            rejectBtn.click();
                            console.log('[Klar] CookieBot: clicked reject');
                        }
                    }, 500);
                })();
                """
            },
            
            # Usercentrics (used by 30k+ sites)
            "usercentrics": {
                "name": "Usercentrics",
                "patterns": ["usercentrics", "app.usercentrics.eu"],
                "selectors": {
                    "decline": [
                        "button[data-testid='uc.deny-all-button']",
                        "button[aria-label*='Reject']"
                    ],
                    "accept": [
                        "button[data-testid='uc.accept-all-button']"
                    ]
                },
                "js": """
                // Usercentrics
                (function() {
                    console.log('[Klar] Usercentrics banner detected');
                    setTimeout(function() {
                        var denyBtn = document.querySelector('[data-testid="uc.deny-all-button"]');
                        if (denyBtn && denyBtn.offsetHeight > 0) {
                            denyBtn.click();
                            console.log('[Klar] Usercentrics: clicked deny all');
                        }
                    }, 500);
                })();
                """
            },
            
            # ConsentManager (used by 10k+ sites)
            "consentmanager": {
                "name": "ConsentManager",
                "patterns": ["consentmanager.net", "select.consentmanager"],
                "selectors": {
                    "decline": [
                        "button[data-cm='no-all']",
                        "button[data-cm-action='reject']"
                    ],
                    "accept": [
                        "button[data-cm='yes-all']"
                    ]
                },
                "js": """
                // ConsentManager
                (function() {
                    console.log('[Klar] ConsentManager banner detected');
                    setTimeout(function() {
                        var noBtn = document.querySelector('[data-cm="no-all"]');
                        if (noBtn && noBtn.offsetHeight > 0) {
                            noBtn.click();
                            console.log('[Klar] ConsentManager: clicked no-all');
                        }
                    }, 500);
                })();
                """
            },
            
            # TrustArc
            "trustarc": {
                "name": "TrustArc",
                "patterns": ["truste", "trustarc"],
                "js": """
                // TrustArc
                (function() {
                    console.log('[Klar] TrustArc banner detected');
                    setTimeout(function() {
                        var denyBtn = document.querySelector('.truste_popframe a[href*="deny"]');
                        if (denyBtn) denyBtn.click();
                    }, 500);
                })();
                """
            },
            
            # Google (YouTube, Google Services)
            "google": {
                "name": "Google Consent",
                "patterns": ["google", "youtube", "consent.google"],
                "js": """
                // Google
                (function() {
                    console.log('[Klar] Google banner detected');
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button, [role="button"]');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = (buttons[i].textContent || '').toLowerCase();
                            if (text.includes('reject') || text.includes('decline')) {
                                buttons[i].click();
                                console.log('[Klar] Google: clicked reject');
                                return;
                            }
                        }
                    }, 500);
                })();
                """
            },
            
            # Generic fallback
            "generic": {
                "name": "Generic Banner",
                "js": """
                // Generic handler
                (function() {
                    console.log('[Klar] Using generic banner handler');
                    
                    function findButton(keywords) {
                        var buttons = document.querySelectorAll('button, [role="button"]');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = (buttons[i].textContent || '').toLowerCase();
                            for (var k = 0; k < keywords.length; k++) {
                                if (text.includes(keywords[k])) {
                                    return buttons[i];
                                }
                            }
                        }
                        return null;
                    }
                    
                    setTimeout(function() {
                        var declineKeywords = ['reject', 'decline', 'avvisa', 'neka', 'refuse'];
                        var btn = findButton(declineKeywords);
                        
                        if (btn && btn.offsetHeight > 0) {
                            btn.click();
                            console.log('[Klar] Generic: clicked decline button');
                        } else {
                            // Fallback to accept
                            var acceptKeywords = ['accept', 'acceptera', 'godkänn', 'agree', 'ok'];
                            btn = findButton(acceptKeywords);
                            if (btn) btn.click();
                        }
                        
                        // Hide popups
                        setTimeout(function() {
                            document.querySelectorAll('[class*="cookie"], [id*="cookie"], [role="dialog"]').forEach(function(el) {
                                if (el.offsetHeight > 0) el.style.display = 'none !important';
                            });
                        }, 200);
                    }, 600);
                })();
                """
            }
        }
    
    def detect_banner_type(self, domain: str, html_content: str = "") -> str:
        """
        Detect which cookie banner service is used on a domain
        
        Args:
            domain: Domain name
            html_content: Optional page HTML to check for patterns
            
        Returns:
            Banner service name or 'generic'
        """
        domain_lower = domain.lower()
        
        # Check domain-specific known services
        if 'spotify' in domain_lower:
            return 'spotify'
        elif 'aftonbladet' in domain_lower:
            return 'aftonbladet'
        
        # Check patterns in domain or content
        for service, config in self.banners.items():
            if service == 'generic':
                continue
            
            patterns = config.get('patterns', [])
            for pattern in patterns:
                if pattern.lower() in domain_lower or (html_content and pattern.lower() in html_content.lower()):
                    return service
        
        return 'generic'
    
    def get_handler_js(self, banner_type: str) -> str:
        """Get JavaScript handler for a banner type"""
        if banner_type in self.banners:
            return self.banners[banner_type].get('js', self.banners['generic']['js'])
        return self.banners['generic']['js']
    
    def get_banner_info(self, banner_type: str) -> dict:
        """Get info about a banner type"""
        return self.banners.get(banner_type, self.banners['generic'])
