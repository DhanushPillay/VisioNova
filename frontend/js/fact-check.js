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

    updateTrustScore(result.confidence, result.verdict);

    if (resultsContainer) {
        resultsContainer.classList.remove('hidden');
        resultsContainer.innerHTML = buildResultsHTML(result);
    }
}

/**
 * Update the trust score display
 */
function updateTrustScore(confidence, verdict) {
    const scoreDisplay = document.querySelector('.text-4xl.font-black');
    if (scoreDisplay) {
        scoreDisplay.textContent = confidence;
    }

    const circle = document.querySelector('circle[stroke="#00D991"], circle[stroke="#FF4A4A"], circle[stroke="#FFB74A"], circle[stroke="#94A3B8"]');
    if (circle) {
        const circumference = 251.2;
        const offset = circumference - (confidence / 100) * circumference;
        circle.setAttribute('stroke-dashoffset', offset);

        const colors = {
            'TRUE': '#00D991',
            'FALSE': '#FF4A4A',
            'PARTIALLY TRUE': '#FFB74A',
            'MISLEADING': '#FF4A4A',
            'UNVERIFIABLE': '#94A3B8'
        };
        circle.setAttribute('stroke', colors[verdict] || '#94A3B8');
    }

    const verdictLabel = document.querySelector('.rounded-full.text-sm.font-bold');
    if (verdictLabel) {
        verdictLabel.textContent = verdict;
    }
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
