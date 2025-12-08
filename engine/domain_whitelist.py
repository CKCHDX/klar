"""
KLAR - Domain Whitelist Security System
Only allows access to whitelisted Swedish domains
All other URLs are blocked with security warning
Advanced users can bypass with explicit disclaimer acknowledgment
"""

import json
from typing import Tuple, Set
from urllib.parse import urlparse


class DomainWhitelist:
    """
    Security layer: Enforce whitelist-only domain access.
    Protects users from phishing, malware, and unwanted content.
    Advanced users can bypass with explicit acknowledgment.
    """
    
    def __init__(self, domains_file: str = "domains.json"):
        self.whitelist: Set[str] = set()
        self.bypass_tokens: Set[str] = set()  # Track users who acknowledged bypass
        self.load_whitelist(domains_file)
        self.blocked_count = 0
        self.allowed_count = 0
        self.bypass_count = 0
    
    def load_whitelist(self, domains_file: str):
        """Load whitelisted domains from JSON file"""
        try:
            with open(domains_file, 'r', encoding='utf-8') as f:
                domains = json.load(f)
                self.whitelist = set(domain.lower() for domain in domains)
                print(f"[Security] ✓ Loaded {len(self.whitelist)} whitelisted domains")
        except FileNotFoundError:
            print(f"[Security] ⚠ Warning: {domains_file} not found")
            self.whitelist = set()
        except json.JSONDecodeError:
            print(f"[Security] ✗ Error: Invalid JSON in {domains_file}")
            self.whitelist = set()
    
    def is_whitelisted(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL domain is whitelisted.
        
        Args:
            url: Full URL to check
        
        Returns:
            (is_whitelisted: bool, reason: str)
        """
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            if not domain:
                return False, "Invalid URL: no domain found"
            
            # Extract main domain intelligently
            parts = domain.split('.')
            
            # Handle .co.uk, .ac.uk, etc.
            if len(parts) > 2 and parts[-2] in ['co', 'ac', 'gov']:
                main_domain = '.'.join(parts[-3:])
            else:
                main_domain = '.'.join(parts[-2:]) if len(parts) > 1 else domain
            
            # Check variations
            if domain in self.whitelist:
                self.allowed_count += 1
                return True, f"✓ {domain} is whitelisted"
            
            if main_domain in self.whitelist:
                self.allowed_count += 1
                return True, f"✓ {main_domain} is whitelisted"
            
            # Check if it's a subdomain of whitelisted domain
            for whitelisted in self.whitelist:
                if domain.endswith('.' + whitelisted):
                    self.allowed_count += 1
                    return True, f"✓ Subdomain of {whitelisted} is whitelisted"
            
            self.blocked_count += 1
            return False, f"Domain '{domain}' is NOT on the whitelisted domains list"
        
        except Exception as e:
            self.blocked_count += 1
            return False, f"Invalid URL format: {str(e)}"
    
    def generate_bypass_token(self) -> str:
        """
        Generate a unique bypass token for this session.
        Returns a token that user must confirm to bypass security.
        """
        import uuid
        token = str(uuid.uuid4())
        self.bypass_tokens.add(token)
        return token
    
    def verify_bypass_acknowledgment(self, token: str) -> bool:
        """
        Verify that user has acknowledged the bypass disclaimer.
        
        Args:
            token: Bypass token generated earlier
        
        Returns:
            True if token is valid and acknowledged
        """
        return token in self.bypass_tokens
    
    def get_blocked_html(self, url: str, reason: str) -> str:
        """
        Generate HTML for blocked domain warning page.
        Shows user-friendly security message in Swedish with bypass option.
        """
        bypass_token = self.generate_bypass_token()
        
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
                .reason strong {{
                    color: #60a5fa;
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
                .info strong {{
                    color: #4ade80;
                }}
                
                .bypass-section {{
                    margin-top: 35px;
                    padding-top: 25px;
                    border-top: 1px solid rgba(59, 130, 246, 0.2);
                }}
                
                .bypass-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #fbbf24;
                    margin-bottom: 15px;
                }}
                
                .disclaimer {{
                    background: rgba(239, 68, 68, 0.05);
                    border: 2px solid rgba(239, 68, 68, 0.3);
                    padding: 20px;
                    border-radius: 12px;
                    margin: 20px 0;
                    text-align: left;
                }}
                
                .disclaimer-title {{
                    color: #ef4444;
                    font-weight: 700;
                    margin-bottom: 12px;
                }}
                
                .disclaimer-text {{
                    font-size: 13px;
                    color: #a0a8c0;
                    line-height: 1.7;
                }}
                
                .disclaimer-text strong {{
                    color: #fca5a5;
                }}
                
                .checkbox-container {{
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    margin: 20px 0;
                    text-align: left;
                }}
                
                .checkbox-container input[type="checkbox"] {{
                    width: 20px;
                    height: 20px;
                    margin-top: 2px;
                    cursor: pointer;
                    accent-color: #ef4444;
                }}
                
                .checkbox-label {{
                    font-size: 14px;
                    color: #a0a8c0;
                    cursor: pointer;
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
                .btn-primary:hover:not(:disabled) {{
                    background: #60a5fa;
                    transform: translateY(-2px);
                }}
                .btn-danger {{
                    background: #ef4444;
                    color: white;
                }}
                .btn-danger:hover:not(:disabled) {{
                    background: #f87171;
                    transform: translateY(-2px);
                }}
                .btn:disabled {{
                    opacity: 0.5;
                    cursor: not-allowed;
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
                .whitelisted-count {{
                    display: inline-block;
                    background: rgba(59, 130, 246, 0.1);
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin: 15px 0;
                }}
                .status-message {{
                    font-size: 13px;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 6px;
                    display: none;
                }}
                .status-message.success {{
                    background: rgba(34, 197, 94, 0.2);
                    color: #86efac;
                    display: block;
                }}
                .status-message.error {{
                    background: rgba(239, 68, 68, 0.2);
                    color: #fca5a5;
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="warning-icon">🔒</div>
                <h1>Webbplats blockerad för säkerhet</h1>
                <h2>Denna domän är inte godkänd för din säkerhet</h2>
                
                <p>Du försökte komma åt en webbplats som inte finns på vår säkra domänlista.</p>
                
                <div class="url">{url}</div>
                
                <div class="reason">
                    <strong>Varför är denna webbplats blockerad?</strong><br>
                    {reason}
                </div>
                
                <div class="info">
                    <strong>ℹ️ Om Klar-säkerhet:</strong><br>
                    Klar är designad för att skydda dig och din familj. Vi tillåter endast godkända svenska webbplatser för att undvika nätfiske, malvara och olämpligt innehål. Det är en viktig del av din digitala säkerhet.
                </div>
                
                <div class="whitelisted-count">
                    ✓ 111 godkända svenska domäner tillgängliga
                </div>
                
                <!-- BYPASS SECTION -->
                <div class="bypass-section">
                    <div class="bypass-title">⚠️ Avancerad användare? Åsidosätt säkerhet</div>
                    
                    <div class="disclaimer">
                        <div class="disclaimer-title">⚠️ VIKTIGT ANSVARSBEFRIELSE</div>
                        <div class="disclaimer-text">
                            <p>
                                <strong>Oscyra.solutions är INTE ansvarig</strong> för något som helst som sker när du besöker webbplatser utanför vår säkra domänlista.
                            </p>
                            <p style="margin-top: 12px;">
                                Detta inkluderar men är inte begränsat till:
                            </p>
                            <ul style="margin: 12px 0 0 20px;">
                                <li>Nätfiske, bedrägerier eller identitetsstöld</li>
                                <li>Malvara, virus eller andra skadliga program</li>
                                <li>Datainsamling eller integritetsintrång</li>
                                <li>Olämpligt eller illegalt innehål</li>
                                <li>Ekonomisk förlust eller skada</li>
                                <li>Någon annan form av skada eller förlust</li>
                            </ul>
                            <p style="margin-top: 12px; font-weight: 700;">
                                DU ANVÄNDER DESSA WEBBPLATSER PÅ DIN EGEN RISK.
                            </p>
                        </div>
                    </div>
                    
                    <div class="checkbox-container">
                        <input type="checkbox" id="acknowledgement" onchange="updateBypassButton()">
                        <label for="acknowledgement" class="checkbox-label">
                            Jag förstår och accepterar all risk. Jag vet att Oscyra.solutions inte är ansvarig för något som helst utanför den säkra domänlistan.
                        </label>
                    </div>
                    
                    <div id="statusMessage" class="status-message"></div>
                    
                    <div class="actions">
                        <button class="btn btn-danger" id="bypassBtn" onclick="bypassSecurity()" disabled>
                            Åsidosätt säkerhet och besök webbplatsen
                        </button>
                    </div>
                </div>
                
                <div class="actions" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="history.back()">← Gå tillbaka</button>
                    <button class="btn btn-secondary" onclick="location.href='about:blank'">Hem</button>
                </div>
                
                <div class="footer">
                    <p>Om du tror att denna webbplats bör vara tillgänglig, kontakta oss på oscyra.solutions</p>
                </div>
            </div>
            
            <script>
                const bypassToken = '{bypass_token}';
                
                function updateBypassButton() {{
                    const checkbox = document.getElementById('acknowledgement');
                    const button = document.getElementById('bypassBtn');
                    button.disabled = !checkbox.checked;
                }}
                
                function bypassSecurity() {{
                    const checkbox = document.getElementById('acknowledgement');
                    if (checkbox.checked) {{
                        // Send bypass token back to application
                        localStorage.setItem('klar_bypass_' + '{url}'.replace(/[^a-zA-Z0-9]/g, '_'), bypassToken);
                        
                        const statusMsg = document.getElementById('statusMessage');
                        statusMsg.className = 'status-message success';
                        statusMsg.textContent = '✓ Säkerhetskontroll åsidosatt. Omdirigerar...';
                        
                        // Redirect after brief delay
                        setTimeout(function() {{
                            window.location.href = '{url}';
                        }}, 800);
                    }}
                }}
            </script>
        </body>
        </html>
        """
    
    def get_statistics(self) -> dict:
        """Get whitelist statistics"""
        return {
            "total_whitelisted": len(self.whitelist),
            "allowed_count": self.allowed_count,
            "blocked_count": self.blocked_count,
            "bypass_count": self.bypass_count,
            "block_rate": self.blocked_count / max(1, self.allowed_count + self.blocked_count)
        }
