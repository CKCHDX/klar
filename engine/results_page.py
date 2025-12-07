"""
Results Page Generator
Generate HTML results pages with domain attribution and styling
"""

from typing import List, Dict
import json
from datetime import datetime


class ResultsPageGenerator:
    """Generate HTML results page with styling and domain info"""
    
    def __init__(self):
        self.base_style = """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .search-info {
                color: #666;
                margin-top: 10px;
            }
            .results {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .result {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                border-left: 4px solid #667eea;
            }
            .result:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            }
            .result-title {
                font-size: 1.3em;
                color: #667eea;
                margin-bottom: 8px;
                text-decoration: none;
                display: block;
            }
            .result-title:hover {
                text-decoration: underline;
            }
            .result-url {
                color: #08a335;
                font-size: 0.9em;
                margin-bottom: 10px;
                word-break: break-all;
            }
            .result-domain {
                display: inline-block;
                background: #f0f0f0;
                color: #667eea;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.85em;
                font-weight: bold;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .result-trusted {
                color: #08a335;
                font-weight: bold;
            }
            .result-snippet {
                color: #555;
                margin-top: 10px;
                line-height: 1.6;
            }
            .result-meta {
                color: #999;
                font-size: 0.85em;
                margin-top: 10px;
            }
            .no-results {
                background: white;
                padding: 40px;
                border-radius: 8px;
                text-align: center;
                color: #666;
            }
        </style>
        """
    
    def generate(self, results: Dict, query: str) -> str:
        """
        Generate complete HTML results page
        Returns: HTML string ready to display
        """
        result_items = results.get('results', [])
        total = results.get('total_results', 0)
        domains_used = results.get('domains_used', [])
        category = results.get('category', 'Generell')
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="sv">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KLAR - {query}</title>
            {self.base_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 KLAR - Sökresultat</h1>
                    <p class="search-info">
                        <strong>Sökning:</strong> "{query}"<br>
                        <strong>Kategori:</strong> {category}<br>
                        <strong>Resultat:</strong> {total} från {len(domains_used)} källor<br>
                        <strong>Tid:</strong> {datetime.now().strftime('%H:%M:%S')}
                    </p>
                </div>
        """
        
        if result_items:
            html += '<div class="results">'
            
            for idx, result in enumerate(result_items, 1):
                domain = result.get('domain', 'Okänd')
                title = result.get('title', 'Ingen titel')
                url = result.get('url', '#')
                snippet = result.get('snippet', 'Ingen beskrivning')
                date_str = result.get('date', '')
                trusted = result.get('trusted', False)
                subpage = result.get('subpage', '')
                
                trusted_badge = '<span class="result-trusted">✓ Godkänd källa</span>' if trusted else ''
                date_info = f'<div class="result-meta">Publicerad: {date_str}</div>' if date_str else ''
                
                html += f"""
                <div class="result">
                    <a href="{url}" class="result-title">{title}</a>
                    <div class="result-url">{url}</div>
                    <span class="result-domain">{domain}{' /' + subpage if subpage else ''}</span>
                    {trusted_badge}
                    <div class="result-snippet">{snippet}</div>
                    {date_info}
                </div>
                """
            
            html += '</div>'
        else:
            html += '<div class="no-results">Inga resultat hittades för denna sökning.</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_minimal(self, results: Dict) -> str:
        """
        Generate minimal JSON response for API
        Returns: JSON string
        """
        return json.dumps({
            'query': results.get('query', ''),
            'category': results.get('category', ''),
            'total_results': results.get('total_results', 0),
            'results': results.get('results', []),
            'domains_used': results.get('domains_used', [])
        }, ensure_ascii=False, indent=2)
    
    def generate_search_suggestions(self, query: str, suggestions: List[str]) -> str:
        """
        Generate HTML for search suggestions
        Returns: HTML string
        """
        html = '<div class="suggestions">'
        html += f'<p>Menade du:</p><ul>'
        
        for suggestion in suggestions:
            html += f'<li><a href="?q={suggestion}">{suggestion}</a></li>'
        
        html += '</ul></div>'
        return html
    
    def add_analytics(self, html: str, tracking_id: str = '') -> str:
        """
        Add analytics tracking to HTML (if enabled)
        Returns: HTML with analytics added
        """
        if not tracking_id:
            return html
        
        analytics = f"""
        <!-- Analytics disabled for privacy -->
        """
        
        return html.replace('</body>', analytics + '</body>')
