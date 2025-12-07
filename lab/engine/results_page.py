"""
Klar 3.0 - Results Page Generator
Modern dark design with enhanced UX
"""

from typing import List, Dict
import html as html_module


class ResultsPage:
    def __init__(self):
        pass

    def generate_html(self, results: Dict) -> str:
        """Generate modern results page HTML"""
        query = results.get('query', 'Sökning')
        search_results = results.get('results', [])
        total = len(search_results)

        if not search_results:
            return self._generate_no_results_page(query)

        results_html = self._render_results(search_results)

        html = f"""
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Klar - Sökresultat för {self._escape(query)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --color-bg-primary: #0a0e27;
            --color-bg-secondary: #0f1419;
            --color-bg-tertiary: #1a1f3a;
            --color-text-primary: #ffffff;
            --color-text-secondary: #cbd5e1;
            --color-text-tertiary: #64748b;
            --color-accent: #3b82f6;
            --color-accent-hover: #2563eb;
            --color-border: #1e293b;
            --color-border-light: #334155;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            line-height: 1.6;
        }}

        /* Header */
        .header {{
            background-color: var(--color-bg-secondary);
            border-bottom: 1px solid var(--color-border);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(8px);
            background-color: rgba(15, 20, 25, 0.95);
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .header-logo {{
            font-size: 24px;
            font-weight: 700;
            color: var(--color-accent);
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }}

        .search-container {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .search-bar {{
            flex: 1;
            display: flex;
            gap: 8px;
        }}

        .search-input {{
            flex: 1;
            background-color: var(--color-bg-tertiary);
            color: var(--color-text-primary);
            border: 1px solid var(--color-border-light);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 15px;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--color-accent);
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background-color: rgba(26, 31, 58, 0.8);
        }}

        .search-input::placeholder {{
            color: var(--color-text-tertiary);
        }}

        .search-btn {{
            background-color: var(--color-accent);
            color: var(--color-text-primary);
            border: none;
            border-radius: 8px;
            padding: 12px 28px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}

        .search-btn:hover {{
            background-color: var(--color-accent-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }}

        .search-btn:active {{
            transform: translateY(0);
        }}

        /* Main Container */
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 32px 20px;
        }}

        /* Results Info */
        .results-info {{
            margin-bottom: 28px;
            display: flex;
            align-items: baseline;
            gap: 8px;
        }}

        .results-count {{
            font-size: 15px;
            color: var(--color-text-secondary);
        }}

        .results-count strong {{
            color: var(--color-accent);
            font-weight: 600;
        }}

        .results-query {{
            font-weight: 500;
            color: var(--color-text-primary);
        }}

        /* Results List */
        .results-list {{
            display: grid;
            gap: 16px;
        }}

        .result-item {{
            background-color: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}

        .result-item::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 3px;
            height: 100%;
            background: linear-gradient(180deg, var(--color-accent), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .result-item:hover {{
            border-color: var(--color-accent);
            background-color: rgba(26, 31, 58, 0.5);
            transform: translateX(4px);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
        }}

        .result-item:hover::before {{
            opacity: 1;
        }}

        .result-domain {{
            color: var(--color-accent);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            display: inline-block;
        }}

        .result-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--color-text-primary);
            margin-bottom: 8px;
            line-height: 1.4;
            word-break: break-word;
        }}

        .result-title a {{
            color: inherit;
            text-decoration: none;
            transition: color 0.2s ease;
        }}

        .result-title a:hover {{
            color: var(--color-accent);
        }}

        .result-description {{
            color: var(--color-text-secondary);
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .result-url {{
            color: var(--color-text-tertiary);
            font-size: 12px;
            word-break: break-all;
            margin-bottom: 12px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }}

        .result-meta {{
            display: flex;
            gap: 16px;
            align-items: center;
            font-size: 12px;
            color: var(--color-text-tertiary);
        }}

        .result-relevance {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .relevance-bar {{
            width: 40px;
            height: 4px;
            background-color: var(--color-border-light);
            border-radius: 2px;
            overflow: hidden;
        }}

        .relevance-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--color-accent), #10b981);
            border-radius: 2px;
        }}

        /* No Results */
        .no-results {{
            text-align: center;
            padding: 60px 20px;
        }}

        .no-results-icon {{
            font-size: 64px;
            margin-bottom: 24px;
            opacity: 0.6;
        }}

        .no-results-title {{
            font-size: 28px;
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: 12px;
        }}

        .no-results-message {{
            color: var(--color-text-secondary);
            font-size: 15px;
            margin-bottom: 24px;
        }}

        .no-results-suggestion {{
            color: var(--color-text-tertiary);
            font-size: 13px;
            line-height: 1.8;
        }}

        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--color-border);
            text-align: center;
            color: var(--color-text-tertiary);
            font-size: 12px;
        }}

        /* Responsive */
        @media (max-width: 640px) {{
            .container {{
                padding: 16px 12px;
            }}

            .header-content {{
                padding: 0 12px;
            }}

            .search-bar {{
                flex-direction: column;
            }}

            .search-input, .search-btn {{
                width: 100%;
            }}

            .result-item {{
                padding: 16px;
            }}

            .result-title {{
                font-size: 16px;
            }}

            .result-description {{
                font-size: 13px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-logo">Klar</div>
            <div class="search-container">
                <div class="search-bar">
                    <input type="text" class="search-input" value="{self._escape(query)}" placeholder="Sök..." id="queryInput" onkeypress="if(event.key==='Enter')document.querySelector('.search-btn').click()">
                    <button class="search-btn" onclick="if(document.getElementById('queryInput').value){{window.location.href='search?q='+encodeURIComponent(document.getElementById('queryInput').value)}}">Sök</button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="results-info">
            <span class="results-count"><strong>{total}</strong> resultat hittade</span>
            <span class="results-query">för "<strong>{self._escape(query)}</strong>"</span>
        </div>

        <div class="results-list">
            {results_html}
        </div>
    </div>
</body>
</html>
        """
        return html

    def _generate_no_results_page(self, query: str) -> str:
        """Generate 'no results found' page"""
        html = f"""
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Klar - Inga resultat</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --color-bg-primary: #0a0e27;
            --color-bg-secondary: #0f1419;
            --color-text-primary: #ffffff;
            --color-text-secondary: #cbd5e1;
            --color-text-tertiary: #64748b;
            --color-accent: #3b82f6;
            --color-border: #1e293b;
            --color-border-light: #334155;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        .header {{
            background-color: var(--color-bg-secondary);
            border-bottom: 1px solid var(--color-border);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .header-logo {{
            font-size: 24px;
            font-weight: 700;
            color: var(--color-accent);
            margin-bottom: 16px;
        }}

        .search-container {{
            display: flex;
            gap: 8px;
        }}

        .search-input {{
            flex: 1;
            background-color: #1a1f3a;
            color: var(--color-text-primary);
            border: 1px solid var(--color-border-light);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 15px;
        }}

        .search-input:focus {{
            border-color: var(--color-accent);
            outline: none;
        }}

        .search-btn {{
            background-color: var(--color-accent);
            color: var(--color-text-primary);
            border: none;
            border-radius: 8px;
            padding: 12px 28px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .search-btn:hover {{
            background-color: #2563eb;
        }}

        .main {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }}

        .no-results {{
            text-align: center;
            max-width: 500px;
        }}

        .no-results-icon {{
            font-size: 80px;
            margin-bottom: 32px;
            opacity: 0.5;
            animation: float 3s ease-in-out infinite;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}

        .no-results-title {{
            font-size: 32px;
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}

        .no-results-message {{
            color: var(--color-text-secondary);
            font-size: 16px;
            margin-bottom: 20px;
            line-height: 1.6;
        }}

        .suggestions {{
            color: var(--color-text-tertiary);
            font-size: 13px;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid var(--color-border);
        }}

        .suggestions strong {{
            color: var(--color-text-secondary);
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-logo">Klar</div>
            <div class="search-container">
                <input type="text" class="search-input" value="{self._escape(query)}" placeholder="Sök..." id="queryInput" onkeypress="if(event.key==='Enter')document.querySelector('.search-btn').click()">
                <button class="search-btn" onclick="if(document.getElementById('queryInput').value){{window.location.href='search?q='+encodeURIComponent(document.getElementById('queryInput').value)}}">Sök</button>
            </div>
        </div>
    </div>

    <div class="main">
        <div class="no-results">
            <div class="no-results-icon">😔</div>
            <h1 class="no-results-title">Inga resultat hittades</h1>
            <p class="no-results-message">Försök med andra sökord eller kontrollera stavningen</p>
            <div class="suggestions">
                <strong>Tips:</strong><br>
                • Försök med kortare eller annat sökord<br>
                • Kontrollera stavningen<br>
                • Använd färre eller andra nyckelord
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html

    def _render_results(self, results: List[Dict]) -> str:
        """Render individual results"""
        html_parts = []

        for result in results:
            url = result.get('url', '#')
            title = result.get('title', 'Ingen titel')
            description = result.get('description', '')
            domain = result.get('domain', '')
            relevance = result.get('relevance', 0)

            # Clamp relevance to 0-1
            relevance = max(0, min(1, relevance))
            relevance_percent = int(relevance * 100)

            # Escape HTML
            title_escaped = self._escape(title)
            description_escaped = self._escape(description)
            domain_escaped = self._escape(domain)
            url_escaped = self._escape(url)

            html_parts.append(f"""
        <div class="result-item">
            <div class="result-domain">{domain_escaped}</div>
            <h3 class="result-title"><a href="{url_escaped}" target="_blank" rel="noopener noreferrer">{title_escaped}</a></h3>
            <p class="result-description">{description_escaped}</p>
            <div class="result-url">{url_escaped}</div>
            <div class="result-meta">
                <div class="result-relevance">
                    <span>Relevans:</span>
                    <div class="relevance-bar">
                        <div class="relevance-fill" style="width: {relevance_percent}%"></div>
                    </div>
                    <span>{relevance_percent}%</span>
                </div>
            </div>
        </div>
            """)

        return ''.join(html_parts)

    def _escape(self, text: str) -> str:
        """Escape HTML characters safely"""
        return html_module.escape(str(text), quote=True)
