"""
KLAR - Domain Whitelist Security System (FIXED)
Only allows access to whitelisted domains
Subdomains and subpages of whitelisted domains are automatically allowed
No unnecessary blocking of legitimate content
"""

import json
from typing import Tuple, Set
from urllib.parse import urlparse


class DomainWhitelist:
    """
    Security layer: Enforce whitelist-only domain access.
    FIXED: Properly handles subdomains and subpages
    - svt.se → allows svt.se, www.svt.se, svt.se/nyheter, nyheter.svt.se, etc.
    - sv.wikipedia.org → allows sv.wikipedia.org and all subpages
    """
    
    def __init__(self, domains_file: str = "domains.json"):
        self.whitelist: Set[str] = set()  # Whitelisted base domains
        self.load_whitelist(domains_file)
        self.blocked_count = 0
        self.allowed_count = 0
        print(f"[Security] ✓ Loaded {len(self.whitelist)} whitelisted domains")
    
    def load_whitelist(self, domains_file: str):
        """Load whitelisted domains from JSON file"""
        try:
            with open(domains_file, 'r', encoding='utf-8') as f:
                domains = json.load(f)
                # Normalize all domains to lowercase
                self.whitelist = set(domain.lower().strip() for domain in domains)
                print(f"[Security] ✓ Loaded {len(self.whitelist)} whitelisted domains")
        except FileNotFoundError:
            print(f"[Security] ⚠ Warning: {domains_file} not found")
            self.whitelist = set()
        except json.JSONDecodeError:
            print(f"[Security] ✗ Error: Invalid JSON in {domains_file}")
            self.whitelist = set()
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract CLEAN domain from URL.
        - Removes 'www.' prefix
        - Handles URLs with/without http scheme
        - Returns just the domain (e.g., 'svt.se' from 'https://www.svt.se/nyheter')
        """
        url_lower = url.lower().strip()
        
        # Add scheme if missing for proper parsing
        if not url_lower.startswith(('http://', 'https://')):
            if '.' in url_lower and '/' not in url_lower.split('.')[0]:
                url_lower = 'https://' + url_lower
            else:
                return ''
        
        try:
            parsed = urlparse(url_lower)
            netloc = parsed.netloc
            
            # Remove 'www.' prefix if present
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            return netloc if netloc else ''
        except:
            return ''
    
    def is_whitelisted(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL domain is whitelisted.
        FIXED: Properly handles subdomains and subpages
        
        Args:
            url: Full URL to check (e.g., 'https://www.svt.se/nyheter', 'svt.se', 'www.svt.se/nyheter')
        
        Returns:
            (is_allowed: bool, reason: str)
        """
        try:
            # Extract domain from URL
            domain = self._extract_domain(url)
            
            if not domain:
                self.blocked_count += 1
                return False, "Invalid URL: no domain found"
            
            domain_lower = domain.lower()
            
            # DIRECT MATCH: Is this exact domain whitelisted?
            if domain_lower in self.whitelist:
                self.allowed_count += 1
                print(f"[Security] ✓ Allowed (exact match): {domain_lower}")
                return True, f"✓ {domain_lower} is whitelisted"
            
            # SUBDOMAIN MATCH: Is this a subdomain of a whitelisted domain?
            # Example: 'nyheter.svt.se' should match 'svt.se'
            for whitelisted in self.whitelist:
                # If domain ends with '.whitelisted' it's a subdomain
                if domain_lower.endswith('.' + whitelisted):
                    self.allowed_count += 1
                    print(f"[Security] ✓ Allowed (subdomain): {domain_lower} is subdomain of {whitelisted}")
                    return True, f"✓ Subdomain of {whitelisted} is whitelisted"
                
                # If they're equal (handles www prefix removal)
                if domain_lower == whitelisted:
                    self.allowed_count += 1
                    print(f"[Security] ✓ Allowed (after normalization): {domain_lower}")
                    return True, f"✓ {whitelisted} is whitelisted"
            
            # NOT FOUND IN WHITELIST = BLOCKED
            self.blocked_count += 1
            print(f"[Security] ✗ BLOCKED: '{domain_lower}' NOT in whitelist")
            return False, f"Domain '{domain_lower}' is NOT on the whitelisted domains list"
        
        except Exception as e:
            self.blocked_count += 1
            print(f"[Security] ✗ Error checking domain: {str(e)}")
            return False, f"Invalid URL format: {str(e)}"
    
    def get_blocked_html(self, url: str, reason: str) -> str:
        """
        Generate HTML for blocked domain warning page.
        Shows user-friendly security message in Swedish.
        """
        # Escape URL for display
        display_url = url.replace('"', '&quot;').replace("'", '&#39;')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                    background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
                    color: #e8eaf0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{
                    max-width: 700px;
                    background: rgba(19, 24, 36, 0.9);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    border-radius: 16px;
                    padding: 50px 40px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                }}
                .warning-icon {{
                    font-size: 80px;
                    margin-bottom: 30px;
                    animation: float 3s ease-in-out infinite;
                }}
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0px); }}
                    50% {{ transform: translateY(-10px); }}
                }}
                h1 {{
                    color: #ef4444;
                    margin-bottom: 15px;
                    font-size: 28px;
                    font-weight: 700;
                }}
                h2 {{
                    color: #60a5fa;
                    font-size: 16px;
                    font-weight: 500;
                    margin-bottom: 25px;
                }}
                p {{
                    color: #a0a8c0;
                    font-size: 15px;
                    line-height: 1.6;
                    margin: 15px 0;
                }}
                .url {{
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    padding: 16px;
                    border-radius: 12px;
                    color: #fca5a5;
                    word-break: break-all;
                    font-family: 'Monaco', 'Courier New', monospace;
                    font-size: 13px;
                    margin: 25px 0;
                }}
                .reason {{
                    background: rgba(59, 130, 246, 0.1);
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    border-radius: 8px;
                    color: #93c5fd;
                    margin: 25px 0;
                    text-align: left;
                }}
                .info {{
                    background: rgba(34, 197, 94, 0.1);
                    border-left: 4px solid #22c55e;
                    padding: 20px;
                    border-radius: 8px;
                    color: #86efac;
                    margin: 25px 0;
                    text-align: left;
                }}
                .whitelisted-count {{
                    display: inline-block;
                    background: rgba(59, 130, 246, 0.1);
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin: 15px 0;
                }}
                .actions {{
                    margin-top: 30px;
                    display: flex;
                    gap: 12px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                .btn {{
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }}
                .btn-primary {{
                    background: #3b82f6;
                    color: white;
                }}
                .btn-primary:hover {{
                    background: #60a5fa;
                    transform: translateY(-2px);
                }}
                .btn-secondary {{
                    background: rgba(59, 130, 246, 0.2);
                    color: #60a5fa;
                    border: 1px solid #3b82f6;
                }}
                .btn-secondary:hover {{
                    background: rgba(59, 130, 246, 0.3);
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 25px;
                    border-top: 1px solid rgba(59, 130, 246, 0.2);
                    font-size: 12px;
                    color: #6b7390;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="warning-icon">🔒</div>
                <h1>Webbplats blockerad för säkerhet</h1>
                <h2>Denna domän är inte godkänd</h2>
                
                <p>Du försökte komma åt en webbplats som inte finns på vår säkra domänlista.</p>
                
                <div class="url">{display_url}</div>
                
                <div class="reason">
                    <strong>Varför är denna webbplats blockerad?</strong><br>
                    {reason}
                </div>
                
                <div class="info">
                    <strong>ℹ️ Om Klar-säkerhet:</strong><br>
                    Klar är designad för att skydda dig och din familj. Vi tillåter endast godkända svenska webbplatser för att undvika nätfiske, malvara och olämpligt innehål.
                </div>
                
                <div class="whitelisted-count">
                    ✓ 115 godkända svenska domäner tillgängliga
                </div>
                
                <div class="actions">
                    <button class="btn btn-primary" onclick="history.back()">← Gå tillbaka</button>
                </div>
                
                <div class="footer">
                    <p>Om du tror att denna webbplats bör vara tillgänglig, kontakta oss på oscyra.solutions</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def get_statistics(self) -> dict:
        """Get whitelist statistics"""
        return {
            "total_whitelisted": len(self.whitelist),
            "allowed_count": self.allowed_count,
            "blocked_count": self.blocked_count,
            "block_rate": self.blocked_count / max(1, self.allowed_count + self.blocked_count)
        }
