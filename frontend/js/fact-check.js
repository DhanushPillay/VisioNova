/**
 * VisioNova Fact-Check Frontend
 * Connects to the backend API for claim verification.
 */

const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
let urlInput = null;
let resultsContainer = null;

/**
 * Initialize the fact-check page
 */
function initFactCheck() {
    urlInput = document.getElementById('urlInput');

    // Load any stored URL data
    if (typeof VisioNovaStorage !== 'undefined') {
        const urlData = VisioNovaStorage.getFile('url');
        if (urlData && urlInput) {
            urlInput.value = urlData.data;
        }
    }

    // Find the verify button
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        if (btn.textContent.includes('Verify Credibility')) {
            btn.addEventListener('click', handleVerifyClick);
        }
    });

    // Allow Enter key to submit
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleVerifyClick();
            }
        });
    }

    // Create results container
    createResultsContainer();
}

/**
 * Create a container for displaying results
 */
function createResultsContainer() {
    const dashboardGrid = document.querySelector('.grid.grid-cols-1.lg\\:grid-cols-12');
    if (!dashboardGrid) return;

    resultsContainer = document.getElementById('factCheckResults');
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'factCheckResults';
        resultsContainer.className = 'hidden mb-6 max-w-[1400px] mx-auto';
        dashboardGrid.parentNode.insertBefore(resultsContainer, dashboardGrid);
    }
}

/**
 * Handle verify button click
 */
async function handleVerifyClick() {
    const input = urlInput ? urlInput.value.trim() : '';

    if (!input) {
        showNotification('Please enter a claim, question, or URL to verify.', 'warning');
        return;
    }

    showLoading(true);

    try {
        const result = await checkFact(input);
        displayResults(result);
    } catch (error) {
        console.error('Fact-check error:', error);
        showNotification('Failed to connect to the fact-check service. Make sure the backend is running on port 5000.', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Call the fact-check API
 */
async function checkFact(input) {
    const response = await fetch(`${API_BASE_URL}/api/fact-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Display fact-check results
 */
function displayResults(result) {
    if (!result.success) {
        showNotification(result.explanation || 'Could not verify this claim.', 'error');
        return;
    }

    // Update trust score display
    updateTrustScore(result.confidence, result.verdict);

    // Update source count and input type
    const sourceCountEl = document.getElementById('sourceCount');
    const inputTypeEl = document.getElementById('inputType');
    if (sourceCountEl) sourceCountEl.textContent = result.source_count;
    if (inputTypeEl) inputTypeEl.textContent = formatInputType(result.input_type);

    // Update explanation box
    const explanationBox = document.getElementById('explanationBox');
    if (explanationBox) {
        explanationBox.innerHTML = `<p class="text-white text-sm">${result.explanation}</p>`;
    }

    // Update claim title and summary
    const claimTitle = document.getElementById('claimTitle');
    const claimSummary = document.getElementById('claimSummary');
    if (claimTitle) claimTitle.textContent = `"${result.claim}"`;
    if (claimSummary) claimSummary.textContent = `Analyzing claim from ${result.input_type} input. Found ${result.source_count} sources for verification.`;

    // Update sources container
    const sourcesContainer = document.getElementById('sourcesContainer');
    if (sourcesContainer) {
        sourcesContainer.innerHTML = buildSourcesListHTML(result);
    }

    // Also update the legacy results container if it exists
    if (resultsContainer) {
        resultsContainer.classList.remove('hidden');
        resultsContainer.innerHTML = buildResultsHTML(result);
    }
}

/**
 * Format input type for display
 */
function formatInputType(type) {
    const types = {
        'claim': 'Claim',
        'question': 'Question',
        'url': 'URL'
    };
    return types[type] || type.charAt(0).toUpperCase() + type.slice(1);
}

/**
 * Update the trust score display
 */
function updateTrustScore(confidence, verdict) {
    // Update score number
    const scoreDisplay = document.getElementById('trustScore');
    if (scoreDisplay) {
        scoreDisplay.textContent = confidence;
    }

    // Update the SVG circle
    const circle = document.querySelector('circle[stroke-dasharray="251.2"]');
    if (circle) {
        const circumference = 251.2;
        const offset = circumference - (confidence / 100) * circumference;
        circle.setAttribute('stroke-dashoffset', offset);

        const colors = {
            'TRUE': '#00D991',
            'FALSE': '#FF4A4A',
            'PARTIALLY TRUE': '#FFB74A',
            'MISLEADING': '#FFB74A',
            'UNVERIFIABLE': '#94A3B8'
        };
        circle.setAttribute('stroke', colors[verdict] || '#94A3B8');
    }

    // Update verdict label
    const verdictLabel = document.getElementById('verdictLabel');
    if (verdictLabel) {
        const verdictStyles = {
            'TRUE': { text: 'VERIFIED TRUE', bg: 'bg-success/10', border: 'border-success/20', color: 'text-success' },
            'FALSE': { text: 'FALSE CLAIM', bg: 'bg-danger/10', border: 'border-danger/20', color: 'text-danger' },
            'PARTIALLY TRUE': { text: 'PARTIALLY TRUE', bg: 'bg-warning/10', border: 'border-warning/20', color: 'text-warning' },
            'MISLEADING': { text: 'MISLEADING', bg: 'bg-warning/10', border: 'border-warning/20', color: 'text-warning' },
            'UNVERIFIABLE': { text: 'UNVERIFIABLE', bg: 'bg-slate-500/10', border: 'border-slate-500/20', color: 'text-slate-400' }
        };
        const style = verdictStyles[verdict] || verdictStyles['UNVERIFIABLE'];
        verdictLabel.textContent = style.text;
        verdictLabel.className = `mt-4 px-3 py-1 rounded-full ${style.bg} border ${style.border} ${style.color} text-sm font-bold tracking-wide`;
    }
}

/**
 * Build the sources list HTML for the main dashboard
 */
function buildSourcesListHTML(result) {
    if (!result.sources || result.sources.length === 0) {
        return `
            <div class="flex flex-col items-center justify-center py-8 text-center">
                <div class="size-12 rounded-full bg-slate-500/10 flex items-center justify-center mb-3">
                    <span class="material-symbols-outlined text-2xl text-slate-400">search_off</span>
                </div>
                <h4 class="text-white font-medium mb-1">No Sources Found</h4>
                <p class="text-slate-400 text-sm">We couldn't find any sources to verify this claim.</p>
            </div>
        `;
    }

    // Generate source cards in timeline format
    const sourcesHTML = result.sources.map((source, index) => {
        const isLast = index === result.sources.length - 1;
        const trustConfig = getSourceTrustConfig(source.trust_level, source.is_factcheck);

        return `
            <div class="flex gap-4 group">
                <div class="flex flex-col items-center">
                    <div class="size-8 rounded-full ${trustConfig.bgClass} flex items-center justify-center ${trustConfig.textClass} border ${trustConfig.borderClass} shrink-0">
                        <span class="material-symbols-outlined text-sm font-bold">${trustConfig.icon}</span>
                    </div>
                    ${!isLast ? '<div class="w-0.5 h-full bg-white/5 mt-2"></div>' : ''}
                </div>
                <div class="flex-1 pb-4">
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <h4 class="text-white font-medium text-lg line-clamp-1">${escapeHTML(source.title)}</h4>
                        <span class="px-2.5 py-1 rounded-md ${trustConfig.bgClass} ${trustConfig.textClass} text-xs font-bold border ${trustConfig.borderClass} uppercase">${trustConfig.label}</span>
                    </div>
                    <p class="text-slate-400 text-sm mb-3">${escapeHTML(source.snippet)}</p>
                    <!-- Source Evidence Card -->
                    <div class="bg-background-dark/80 rounded-xl p-4 border border-white/5 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer">
                        <div class="flex items-start gap-3">
                            <div class="mt-1 ${trustConfig.textClass}">
                                <span class="material-symbols-outlined text-[20px]">${source.is_factcheck ? 'verified' : 'language'}</span>
                            </div>
                            <div class="flex-1">
                                <p class="text-white text-sm font-medium mb-1">${escapeHTML(source.domain)}</p>
                                <div class="flex items-center gap-4 mt-2">
                                    <a href="${escapeHTML(source.url)}" target="_blank" class="text-xs text-primary font-medium hover:underline flex items-center gap-1">
                                        Visit Source <span class="material-symbols-outlined text-[12px]">open_in_new</span>
                                    </a>
                                    <span class="text-xs text-slate-500">Trust: ${source.trust_level}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    return sourcesHTML;
}

/**
 * Get styling config based on source trust level
 */
function getSourceTrustConfig(trustLevel, isFactCheck) {
    if (isFactCheck) {
        return {
            bgClass: 'bg-success/20',
            textClass: 'text-success',
            borderClass: 'border-success/30',
            icon: 'verified',
            label: 'Fact-Check'
        };
    }

    switch (trustLevel) {
        case 'high':
            return {
                bgClass: 'bg-success/20',
                textClass: 'text-success',
                borderClass: 'border-success/30',
                icon: 'check',
                label: 'High Trust'
            };
        case 'medium-high':
            return {
                bgClass: 'bg-primary/20',
                textClass: 'text-primary',
                borderClass: 'border-primary/30',
                icon: 'thumb_up',
                label: 'Trusted'
            };
        case 'medium':
            return {
                bgClass: 'bg-warning/20',
                textClass: 'text-warning',
                borderClass: 'border-warning/30',
                icon: 'info',
                label: 'Medium'
            };
        default:
            return {
                bgClass: 'bg-slate-500/20',
                textClass: 'text-slate-400',
                borderClass: 'border-slate-500/30',
                icon: 'help',
                label: 'Unknown'
            };
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHTML(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}


/**
 * Build HTML for results display
 */
function buildResultsHTML(result) {
    const sourcesHTML = result.sources.map(source => `
        <div class="flex items-start gap-3 p-3 rounded-lg bg-background-dark/50 border border-white/5 hover:border-white/10 transition-colors">
            <div class="flex-shrink-0 size-8 rounded-lg ${source.is_factcheck ? 'bg-success/20' : 'bg-primary/20'} flex items-center justify-center">
                <span class="material-symbols-outlined text-[16px] ${source.is_factcheck ? 'text-success' : 'text-primary'}">${source.is_factcheck ? 'verified' : 'language'}</span>
            </div>
            <div class="flex-1 min-w-0">
                <a href="${source.url}" target="_blank" class="text-white font-medium text-sm hover:text-primary transition-colors line-clamp-1">${source.title}</a>
                <p class="text-slate-400 text-xs mt-1 line-clamp-2">${source.snippet}</p>
                <div class="flex items-center gap-2 mt-2">
                    <span class="text-[10px] text-slate-500">${source.domain}</span>
                    <span class="px-1.5 py-0.5 rounded text-[10px] font-medium ${getTrustClass(source.trust_level)}">${source.trust_level.toUpperCase()}</span>
                </div>
            </div>
        </div>
    `).join('');

    return `
        <div class="bg-card-dark rounded-2xl p-6 border border-white/5 shadow-xl">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-white font-semibold text-lg flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">fact_check</span>
                    Verification Results
                </h3>
                <span class="text-xs text-slate-400">${result.source_count} sources analyzed</span>
            </div>
            <div class="mb-4 p-3 rounded-lg bg-background-dark/50 border border-white/5">
                <p class="text-xs text-slate-400 mb-1">Analyzed claim:</p>
                <p class="text-white text-sm font-medium">"${result.claim}"</p>
            </div>
            <div class="mb-4 p-3 rounded-lg bg-primary/10 border border-primary/20">
                <p class="text-primary text-sm">${result.explanation}</p>
            </div>
            <h4 class="text-white font-medium text-sm mb-3">Sources Found:</h4>
            <div class="space-y-2 max-h-[300px] overflow-y-auto pr-2">
                ${sourcesHTML || '<p class="text-slate-400 text-sm">No sources found.</p>'}
            </div>
        </div>
    `;
}

function getTrustClass(level) {
    return {
        'high': 'bg-success/20 text-success',
        'medium-high': 'bg-primary/20 text-primary',
        'unknown': 'bg-slate-500/20 text-slate-400'
    }[level] || 'bg-slate-500/20 text-slate-400';
}

/**
 * Show/hide loading state
 */
function showLoading(loading) {
    document.querySelectorAll('button').forEach(btn => {
        if (btn.textContent.includes('Verify') || btn.textContent.includes('Analyzing')) {
            btn.disabled = loading;
            btn.innerHTML = loading
                ? '<span class="material-symbols-outlined text-[20px] animate-spin">progress_activity</span> Analyzing...'
                : '<span class="material-symbols-outlined text-[20px]">verified</span> Verify Credibility';
        }
    });
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    let notification = document.getElementById('factCheckNotification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'factCheckNotification';
        document.body.appendChild(notification);
    }

    const colors = {
        'info': 'bg-primary',
        'warning': 'bg-warning',
        'error': 'bg-danger',
        'success': 'bg-success'
    };

    notification.className = `fixed top-20 right-4 z-50 px-4 py-3 rounded-lg text-white text-sm font-medium ${colors[type]} shadow-lg`;
    notification.textContent = message;

    setTimeout(() => notification.remove(), 5000);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initFactCheck);
