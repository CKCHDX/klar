// Klar 4.0 - Frontend Application Logic

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
        this.statsContainer = document.getElementById('statsContainer');
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
        this.updateStatus('Searching...', 'searching');

        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayResults(data);
            this.updateStatus('Ready', 'ready');
        } catch (error) {
            console.error('Search error:', error);
            this.showError(error.message);
            this.updateStatus('Error', 'error');
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
            this.instantAnswerSource.textContent = `Source: ${data.instant_answer.source}`;
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

        return `
            <a href="${result.url}" target="_blank" class="result-item">
                <div class="result-header">
                    <div class="result-icon">${initials}</div>
                    <div class="result-info">
                        <div class="result-title">${this.escapeHtml(result.title)}</div>
                        <div class="result-url">${domain}</div>
                    </div>
                </div>
                <div class="result-description">${this.escapeHtml(result.description)}</div>
                <div class="result-meta">
                    ${result.domain_category ? `<span class="meta-badge">${this.escapeHtml(result.domain_category)}</span>` : ''}
                </div>
            </a>
        `;
    }

    createNoResultsMessage() {
        return `
            <div class="empty-state">
                <div class="empty-state-content">
                    <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <h2>No Results Found</h2>
                    <p>Try different search terms or check the spelling</p>
                </div>
            </div>
        `;
    }

    showLoading() {
        this.loadingState.style.display = 'flex';
        this.resultsContainer.innerHTML = '';
        this.instantAnswer.style.display = 'none';
        this.emptyState.style.display = 'none';
    }

    showError(message) {
        this.loadingState.style.display = 'none';
        this.resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-content">
                    <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2M4.458 4.458A9 9 0 0119.542 19.542M4.458 4.458c-1.1 1.1-2.055 2.347-2.788 3.735M4.458 4.458l1.414 1.414M19.542 19.542c1.1-1.1 2.055-2.347 2.788-3.735M19.542 19.542l-1.414-1.414"></path>
                    </svg>
                    <h2>Search Error</h2>
                    <p>${this.escapeHtml(message)}</p>
                </div>
            </div>
        `;
    }

    updateStatus(text, status) {
        this.statusIndicator.textContent = text;
        this.statusIndicator.parentElement.className = 'status-indicator status-' + status;
    }

    async loadStats() {
        try {
            const response = await fetch('/stats');
            const stats = await response.json();

            this.statsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Domains:</span>
                    <span class="stat-value">${stats.domains}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Keywords:</span>
                    <span class="stat-value">${stats.keywords}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Cached:</span>
                    <span class="stat-value">${stats.cached_pages}</span>
                </div>
            `;
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.klarApp = new KlarApp();
    });
} else {
    window.klarApp = new KlarApp();
}