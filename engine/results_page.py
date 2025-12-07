"""
Generate HTML for search results page with modern design
"""

class ResultsPage:
    @staticmethod
    def generate_html(query: str, results: dict) -> str:
        """Generate search results HTML"""
        
        results_list = results.get('results', [])
        total = results.get('total', 0)
        
        results_html = ""
        for i, result in enumerate(results_list, 1):
            # Image preview if available
            image_html = ""
            if result.get('images'):
                img_url = result['images'][0]
                image_html = f"""
                <div class="result-image">
                    <img src="{img_url}" alt="Preview" onerror="this.style.display='none'">
                </div>
                """
            
            results_html += f"""
            <div class="result-item" onclick="window.location.href='{result['url']}'">
                <div class="result-main">
                    <div class="result-header">
                        <span class="result-number">{i}</span>
                        <div class="result-info">
                            <div class="result-domain">{result['domain']}</div>
                            <a href="{result['url']}" class="result-title">{result['title']}</a>
                            <div class="result-description">{result['description']}</div>
                        </div>
                    </div>
                    <div class="result-footer">
                        <span class="relevance-badge">Relevans: {int(result['relevance'] * 100)}%</span>
                        {'<span class="image-badge">📷 ' + str(len(result.get('images', []))) + ' bilder</span>' if result.get('images') else ''}
                        {'<span class="verified-badge">✓ Verifierad</span>' if result.get('verified') else ''}
                    </div>
                </div>
                {image_html}
            </div>
            """
        
        if not results_list:
            results_html = """
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h2>Inga resultat hittades</h2>
                <p>Försök med andra sökord eller kontrollera stavningen</p>
            </div>
            """
        
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
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #0a0e1a;
                    color: #e8eaf0;
                    padding: 30px 20px;
                    max-width: 900px;
                    margin: 0 auto;
                }}
                
                .header {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid rgba(59, 130, 246, 0.2);
                }}
                
                .query {{
                    font-size: 28px;
                    font-weight: 600;
                    color: #3b82f6;
                    margin-bottom: 8px;
                }}
                
                .stats {{
                    font-size: 14px;
                    color: #6b7390;
                }}
                
                .result-item {{
                    display: flex;
                    gap: 20px;
                    background: linear-gradient(135deg, #1e2538 0%, #1a2032 100%);
                    padding: 24px;
                    margin-bottom: 16px;
                    border-radius: 16px;
                    border: 2px solid rgba(59, 130, 246, 0.15);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    cursor: pointer;
                }}
                
                .result-item:hover {{
                    border-color: #3b82f6;
                    transform: translateX(6px);
                    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
                }}
                
                .result-main {{
                    flex: 1;
                    min-width: 0;
                }}
                
                .result-header {{
                    display: flex;
                    gap: 16px;
                    margin-bottom: 16px;
                }}
                
                .result-number {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #3b82f6;
                    line-height: 1;
                    min-width: 40px;
                }}
                
                .result-info {{
                    flex: 1;
                    min-width: 0;
                }}
                
                .result-domain {{
                    font-size: 13px;
                    color: #10b981;
                    margin-bottom: 6px;
                    font-weight: 500;
                }}
                
                .result-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #60a5fa;
                    text-decoration: none;
                    display: block;
                    margin-bottom: 10px;
                    line-height: 1.3;
                }}
                
                .result-title:hover {{
                    text-decoration: underline;
                }}
                
                .result-description {{
                    font-size: 15px;
                    color: #a0a8c0;
                    line-height: 1.6;
                }}
                
                .result-footer {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 12px;
                }}
                
                .relevance-badge, .image-badge, .verified-badge {{
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                
                .relevance-badge {{
                    background: rgba(59, 130, 246, 0.2);
                    color: #60a5fa;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                }}
                
                .image-badge {{
                    background: rgba(245, 158, 11, 0.2);
                    color: #fbbf24;
                    border: 1px solid rgba(245, 158, 11, 0.3);
                }}
                
                .verified-badge {{
                    background: rgba(16, 185, 129, 0.2);
                    color: #10b981;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }}
                
                .result-image {{
                    width: 140px;
                    height: 140px;
                    border-radius: 12px;
                    overflow: hidden;
                    background: #131824;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                
                .result-image img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }}
                
                .no-results {{
                    text-align: center;
                    padding: 100px 20px;
                }}
                
                .no-results-icon {{
                    font-size: 72px;
                    margin-bottom: 20px;
                    opacity: 0.5;
                }}
                
                .no-results h2 {{
                    font-size: 32px;
                    margin-bottom: 12px;
                    color: #e8eaf0;
                }}
                
                .no-results p {{
                    font-size: 16px;
                    color: #6b7390;
                }}
                
                @media (max-width: 768px) {{
                    .result-item {{
                        flex-direction: column;
                    }}
                    
                    .result-image {{
                        width: 100%;
                        height: 200px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="query">"{query}"</div>
                <div class="stats">Hittade {total} resultat</div>
            </div>
            
            {results_html}
        </body>
        </html>
        """