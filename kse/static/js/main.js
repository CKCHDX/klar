/**
 * Klar Search Engine - Main JavaScript
 */

// API endpoints
const API = {
    search: '/api/search',
    stats: '/api/stats',
    autocomplete: '/api/autocomplete',
    similar: '/api/similar'
};

/**
 * Execute search via API
 */
async function apiSearch(query, limit = 10, offset = 0) {
    try {
        const params = new URLSearchParams({
            q: query,
            limit: limit,
            offset: offset
        });
        
        const response = await fetch(`${API.search}?${params}`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Search error:', error);
        return null;
    }
}

/**
 * Get autocomplete suggestions
 */
async function getAutocompleteSuggestions(query) {
    try {
        const response = await fetch(`${API.autocomplete}?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            return [];
        }
        
        const data = await response.json();
        return data.suggestions || [];
    } catch (error) {
        console.error('Autocomplete error:', error);
        return [];
    }
}

/**
 * Display autocomplete dropdown
 */
function showAutocompleteSuggestions(suggestions, inputElement) {
    // Remove existing dropdown
    const existing = document.querySelector('.autocomplete-dropdown');
    if (existing) {
        existing.remove();
    }
    
    if (!suggestions || suggestions.length === 0) {
        return;
    }
    
    // Create dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown';
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.textContent = suggestion;
        item.onclick = () => {
            inputElement.value = suggestion;
            dropdown.remove();
        };
        
        item.onmouseover = () => {
            document.querySelectorAll('.autocomplete-item').forEach(el => {
                el.classList.remove('active');
            });
            item.classList.add('active');
        };
        
        dropdown.appendChild(item);
    });
    
    // Position dropdown
    const rect = inputElement.getBoundingClientRect();
    dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
    dropdown.style.left = rect.left + 'px';
    dropdown.style.width = rect.width + 'px';
    
    document.body.appendChild(dropdown);
}

/**
 * Format large numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Setup search input autocomplete
 */
function setupAutocomplete() {
    const searchInputs = document.querySelectorAll('.search-input, .search-input-small');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                return;
            }
            
            // Debounce
            clearTimeout(input.autocompleteTimeout);
            input.autocompleteTimeout = setTimeout(async () => {
                const suggestions = await getAutocompleteSuggestions(query);
                showAutocompleteSuggestions(suggestions, input);
            }, 300);
        });
        
        // Hide dropdown when clicking away
        input.addEventListener('blur', () => {
            setTimeout(() => {
                const dropdown = document.querySelector('.autocomplete-dropdown');
                if (dropdown) {
                    dropdown.remove();
                }
            }, 100);
        });
    });
}

/**
 * Setup result item interactions
 */
function setupResultInteractions() {
    document.querySelectorAll('.result-item').forEach(item => {
        // Hover effect
        item.addEventListener('mouseover', () => {
            item.classList.add('hover');
        });
        
        item.addEventListener('mouseout', () => {
            item.classList.remove('hover');
        });
        
        // Similar results link
        const url = item.querySelector('.result-url')?.textContent;
        if (url) {
            const similarBtn = document.createElement('a');
            similarBtn.className = 'similar-btn';
            similarBtn.href = '#';
            similarBtn.textContent = 'Liknande sidor';
            similarBtn.onclick = (e) => {
                e.preventDefault();
                showSimilarPages(url);
            };
            item.appendChild(similarBtn);
        }
    });
}

/**
 * Show similar pages
 */
async function showSimilarPages(url) {
    try {
        const response = await fetch(`${API.similar}/${encodeURIComponent(url)}`);
        const data = await response.json();
        
        if (data.similar_pages && data.similar_pages.length > 0) {
            // Display similar pages modal or sidebar
            console.log('Similar pages:', data.similar_pages);
        }
    } catch (error) {
        console.error('Similar pages error:', error);
    }
}

/**
 * Get and display statistics
 */
async function loadStatistics() {
    try {
        const response = await fetch(API.stats);
        const stats = await response.json();
        
        // Update stat cards
        document.querySelectorAll('.stat-value').forEach((card, index) => {
            const values = [
                stats.total_pages,
                stats.total_terms,
                stats.total_domains,
                stats.avg_search_time
            ];
            
            if (index < values.length) {
                card.textContent = formatNumber(values[index]);
            }
        });
    } catch (error) {
        console.error('Statistics error:', error);
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+/ to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input, .search-input-small');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}

/**
 * Setup infinite scroll for pagination
 */
function setupInfiniteScroll() {
    // TODO: Implement infinite scroll for search results
}

/**
 * Dark mode toggle
 */
function setupDarkMode() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (prefersDark) {
        document.documentElement.style.setProperty('--background', '#121212');
        document.documentElement.style.setProperty('--surface', '#1e1e1e');
        document.documentElement.style.setProperty('--text-primary', '#e0e0e0');
        document.documentElement.style.setProperty('--text-secondary', '#bdbdbd');
        document.documentElement.style.setProperty('--border', '#333333');
    }
}

/**
 * Send analytics event
 */
function trackEvent(eventName, data = {}) {
    // TODO: Implement analytics tracking
    console.log(`Event: ${eventName}`, data);
}

/**
 * Track search
 */
function trackSearch(query, resultCount, searchTime) {
    trackEvent('search', {
        query: query,
        result_count: resultCount,
        search_time: searchTime
    });
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Setup autocomplete
    setupAutocomplete();
    
    // Setup result interactions
    if (document.querySelector('.results-list')) {
        setupResultInteractions();
    }
    
    // Load statistics on homepage
    if (document.querySelector('.stats-grid')) {
        loadStatistics();
        // Refresh stats every 30 seconds
        setInterval(loadStatistics, 30000);
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup dark mode
    setupDarkMode();
    
    // Setup infinite scroll
    setupInfiniteScroll();
});

// Export functions for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiSearch,
        getAutocompleteSuggestions,
        formatNumber,
        trackSearch
    };
}
