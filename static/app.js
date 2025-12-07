// Klar 3.0 - Frontend Application Logic

class KlarApp {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchButton = document.getElementById('searchButton');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.instantAnswer = document.getElementById('instantAnswer');
        this.instantAnswerContent = document.getElementById('instantAnswerContent');
        this.instantAnswerSource = document.getElementById('instantAnswerSource');
        this.statusIndicator = document.getElementById('statusIndicator');
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.searchButton.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        // Load stats
        this.loadStats();
        
        // Focus search input
        this.searchInput.focus();
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            return;
        }
        
        // Show loading state
        this.showLoading();
        this.updateStatus('Söker...', 'searching');
        
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displayResults(data);
            this.updateStatus('Redo', 'ready');
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError(error.message);
            this.updateStatus('Fel', 'error');
        }
    }
    
    displayResults(data) {
        // Hide loading and empty states
        this.loadingState.style.display = 'none';
        this.emptyState.style.display = 'none';
        
        // Display instant answer if available
        if (data.instant_answer) {
            this.instantAnswer.style.display = 'block';
            this.instantAnswerContent.textContent = data.instant_answer.answer;
            this.instantAnswerSource.textContent = `Källa: ${data.instant_answer.source}`;
        } else {
            this.instantAnswer.style.display = 'none';
        }
        
        // Display results
        if (data.results && data.results.length > 0) {
            this.resultsContainer.innerHTML = data.results.map((result, index) => 
                this.createResultCard(result, index)
            ).join('');
        } else {
            this.resultsContainer.innerHTML = this.createNoResultsMessage();
        }
    }
    
    createResultCard(result, index) {
        const domain = new URL(result.url).hostname;
        const initials = domain.split('.')[0].substring(0, 2).toUpperCase();
        
        const imageBadge = result.images && result.images.length > 0 
            ? `<div class="meta-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
                ${result.images.length} bilder
            </div>`
            : '';
        
        const videoBadge = result.videos && result.videos.length > 0
            ? `<div class="meta-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polygon points="23 7 16 12 23 17 23 7"/>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
                ${result.videos.length} videor
            </div>`
            : '';
        
        return `
            <div class="result-item" onclick="window.open('${result.url}', '_blank')">
                <div class="result-header">
                    <div class="result-icon">${initials}</div>
                    <div class="result-info">
                        <div class="result-title">${this.escapeHtml(result.title || 'Ingen titel')}</div>
                        <div class="result-url">${domain}</div>
                    </div>
                </div>
                <div class="result-description">
                    ${this.escapeHtml(result.description || 'Ingen beskrivning tillgänglig.')}
                </div>
                <div class="result-meta">
                    ${imageBadge}
                    ${videoBadge}
                    <div class="meta-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                        </svg>
                        Relevans: ${Math.round((result.relevance_score || 0) * 100)}%
                    </div>
                </div>
            </div>
        `;
    }
    
    createNoResultsMessage() {
        return `
            <div class="empty-state">
                <div class="empty-state-content">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 8v4m0 4h.01"/>
                    </svg>
                    <h2>Inga resultat hittades</h2>
                    <p>Försök med andra sökord eller kontrollera stavningen</p>
                </div>
            </div>
        `;
    }
    
    showLoading() {
        this.emptyState.style.display = 'none';
        this.resultsContainer.innerHTML = '';
        this.instantAnswer.style.display = 'none';
        this.loadingState.style.display = 'flex';
    }
    
    showError(message) {
        this.loadingState.style.display = 'none';
        this.resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-content">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                    <h2>Ett fel uppstod</h2>
                    <p>${this.escapeHtml(message)}</p>
                </div>
            </div>
        `;
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            document.getElementById('domainCount').textContent = stats.domains || '-';
            document.getElementById('pageCount').textContent = stats.indexed_pages || '0';
            document.getElementById('modeStatus').textContent = stats.offline_mode ? 'Offline' : 'Online';
            
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    updateStatus(text, state) {
        const statusText = this.statusIndicator.querySelector('.status-text');
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        
        statusText.textContent = text;
        
        // Update dot color based on state
        const colors = {
            'ready': '#10b981',
            'searching': '#f59e0b',
            'error': '#ef4444'
        };
        
        statusDot.style.background = colors[state] || colors.ready;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new KlarApp();
});
