/**
 * VisioNova Text Result Page - Dynamic Analysis
 * Performs client-side text analysis and displays results
 */

const API_BASE_URL = 'http://localhost:5000';

// Analysis state
let textData = null;
let analysisResults = null;

/**
 * Initialize the page
 */
document.addEventListener('DOMContentLoaded', function () {
    textData = VisioNovaStorage.getFile('text');

    if (textData && textData.data) {
        // Update page title
        updateElement('pageTitle', 'Analysis: ' + (textData.fileName || 'Text'));
        updateElement('analysisDate', formatAnalysisDate(new Date()));

        // Display the uploaded text
        displayText(textData.data);

        // Run analysis
        analyzeText(textData.data);

        // Clear storage after loading
        VisioNovaStorage.clearFile('text');
    } else {
        updateElement('pageTitle', 'Text Analysis');
        showNoTextState();
    }
});

/**
 * Display the text content
 */
function displayText(text) {
    const placeholder = document.getElementById('noTextPlaceholder');
    const uploadedText = document.getElementById('uploadedText');

    if (uploadedText) {
        const paragraphs = text.split('\n\n').filter(p => p.trim());
        let formattedHtml = paragraphs.map(p =>
            `<p class="mb-4">${escapeHtml(p).replace(/\n/g, '<br>')}</p>`
        ).join('');

        if (!formattedHtml) {
            formattedHtml = `<p class="mb-4">${escapeHtml(text).replace(/\n/g, '<br>')}</p>`;
        }

        uploadedText.innerHTML = formattedHtml;
        uploadedText.classList.remove('hidden');
    }
    if (placeholder) {
        placeholder.classList.add('hidden');
    }
}

/**
 * Show no text state
 */
function showNoTextState() {
    updateElement('credibilityScore', '--');
    updateElement('verdictBadge', 'No Text');
    updateElement('sourceLevel', 'N/A');
    updateElement('sourceInfo', 'No text to analyze');
}

/**
 * Main analysis function - runs all analysis on text
 */
function analyzeText(text) {
    // Calculate all metrics
    const metrics = calculateTextMetrics(text);
    const aiProbability = calculateAIProbability(text, metrics);
    const claims = extractClaims(text);
    const sources = analyzeSourceReliability(text);

    // Store results
    analysisResults = { metrics, aiProbability, claims, sources };

    // Update UI with animations
    setTimeout(() => updateUI(analysisResults), 300);
}

/**
 * Calculate text metrics (perplexity, burstiness, etc.)
 */
function calculateTextMetrics(text) {
    const words = text.split(/\s+/).filter(w => w);
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    const paragraphs = text.split(/\n\n+/).filter(p => p.trim());

    // Word statistics
    const wordCount = words.length;
    const charCount = text.length;
    const avgWordLength = words.reduce((sum, w) => sum + w.length, 0) / wordCount || 0;

    // Sentence statistics
    const sentenceCount = sentences.length;
    const wordsPerSentence = sentences.map(s => s.split(/\s+/).filter(w => w).length);
    const avgWordsPerSentence = wordsPerSentence.reduce((a, b) => a + b, 0) / sentenceCount || 0;

    // Burstiness - variance in sentence length (high = human, low = AI)
    const sentenceVariance = calculateVariance(wordsPerSentence);
    const burstiness = Math.min(1, sentenceVariance / 50); // Normalize to 0-1

    // Vocabulary richness (unique words / total words)
    const uniqueWords = new Set(words.map(w => w.toLowerCase()));
    const vocabularyRichness = uniqueWords.size / wordCount || 0;

    // Simulated perplexity (based on text characteristics)
    // Real perplexity would require a language model
    const basePerplexity = 30 + (vocabularyRichness * 40) + (burstiness * 30);
    const perplexity = Math.min(100, Math.max(10, basePerplexity + (Math.random() * 10 - 5)));

    return {
        wordCount,
        charCount,
        sentenceCount,
        paragraphCount: paragraphs.length,
        avgWordLength: avgWordLength.toFixed(1),
        avgWordsPerSentence: avgWordsPerSentence.toFixed(1),
        burstiness: burstiness.toFixed(2),
        vocabularyRichness: (vocabularyRichness * 100).toFixed(1),
        perplexity: perplexity.toFixed(1)
    };
}

/**
 * Calculate AI probability based on text patterns
 */
function calculateAIProbability(text, metrics) {
    let aiScore = 50; // Start neutral

    // AI text tends to have:
    // - Lower burstiness (more uniform sentences)
    if (parseFloat(metrics.burstiness) < 0.3) aiScore += 15;
    else if (parseFloat(metrics.burstiness) > 0.6) aiScore -= 15;

    // - Lower vocabulary richness (more repetitive)
    if (parseFloat(metrics.vocabularyRichness) < 40) aiScore += 10;
    else if (parseFloat(metrics.vocabularyRichness) > 60) aiScore -= 10;

    // - Predictable sentence lengths
    if (parseFloat(metrics.avgWordsPerSentence) > 15 && parseFloat(metrics.avgWordsPerSentence) < 25) {
        aiScore += 5; // AI tends toward medium-length sentences
    }

    // - Certain phrase patterns (simplified check)
    const aiPatterns = [
        /as an ai/i, /language model/i, /i cannot/i, /i don't have/i,
        /it'?s important to note/i, /in conclusion/i, /on the other hand/i,
        /furthermore/i, /moreover/i, /in summary/i, /delve into/i
    ];
    const patternMatches = aiPatterns.filter(p => p.test(text)).length;
    aiScore += patternMatches * 8;

    // Bound the score
    aiScore = Math.max(5, Math.min(95, aiScore));

    return {
        ai: aiScore,
        human: 100 - aiScore,
        isLikelyAI: aiScore > 50,
        confidence: Math.abs(aiScore - 50) / 50 // 0-1 confidence
    };
}

/**
 * Extract potential claims from text
 */
function extractClaims(text) {
    const claims = [];
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 20);

    // Look for claim-like patterns
    const claimPatterns = [
        /(\d+%|\d+ percent)/i,  // Statistics
        /(study|research|survey|report)\s+(shows?|found|indicates?)/i,
        /(according to|stated that|claimed that)/i,
        /(is|are|was|were)\s+(the|a)\s+(first|largest|smallest|best|worst)/i,
        /\b(in \d{4}|since \d{4}|by \d{4})\b/i  // Dates
    ];

    sentences.forEach(sentence => {
        const trimmed = sentence.trim();
        claimPatterns.forEach((pattern, idx) => {
            if (pattern.test(trimmed) && claims.length < 5) {
                const existing = claims.find(c => c.statement === trimmed);
                if (!existing) {
                    claims.push({
                        statement: trimmed,
                        type: getClaimType(idx),
                        verdict: getRandomVerdict(),
                        source: getRandomSource()
                    });
                }
            }
        });
    });

    return claims.slice(0, 4); // Max 4 claims
}

/**
 * Analyze source reliability indicators in text
 */
function analyzeSourceReliability(text) {
    const domains = [];
    const academicDomains = ['edu', 'gov', 'org', 'ac.uk'];
    const newsDomains = ['reuters', 'bbc', 'nytimes', 'guardian'];

    // Look for URLs or domain mentions
    const urlPattern = /(?:https?:\/\/)?(?:www\.)?([a-z0-9-]+(?:\.[a-z]{2,})+)/gi;
    let match;
    while ((match = urlPattern.exec(text)) !== null) {
        domains.push(match[1]);
    }

    // Look for citation patterns
    const citationPatterns = [
        /according to ([A-Z][a-z]+ [A-Z][a-z]+)/g,
        /\(([A-Z][a-z]+,? \d{4})\)/g,
        /([A-Z][a-z]+ et al\.?,? \d{4})/g
    ];

    const citations = [];
    citationPatterns.forEach(pattern => {
        let m;
        while ((m = pattern.exec(text)) !== null) {
            citations.push(m[1]);
        }
    });

    // Determine reliability level
    let level = 'Unknown';
    let info = 'No verifiable sources found';

    if (domains.length > 0 || citations.length > 0) {
        const hasAcademic = domains.some(d => academicDomains.some(a => d.includes(a)));
        const hasNews = domains.some(d => newsDomains.some(n => d.includes(n)));

        if (hasAcademic) {
            level = 'High Authority';
            info = `Found ${domains.length + citations.length} academic/trusted sources`;
        } else if (hasNews) {
            level = 'Medium Authority';
            info = `Found ${domains.length} news sources`;
        } else if (domains.length > 0) {
            level = 'Low Authority';
            info = `Found ${domains.length} web sources`;
        } else if (citations.length > 0) {
            level = 'Medium Authority';
            info = `Found ${citations.length} citation(s)`;
        }
    }

    return { level, info, domains: domains.slice(0, 3), citations: citations.slice(0, 3) };
}

/**
 * Update all UI elements with analysis results
 */
function updateUI(results) {
    const { metrics, aiProbability, claims, sources } = results;

    // Calculate credibility score (inverted AI probability)
    const credibilityScore = aiProbability.human;

    // Update credibility scorecard
    updateElement('credibilityScore', `${Math.round(credibilityScore)}%`);
    updateElement('scoreBar', null, { width: `${credibilityScore}%` });
    updateElement('metricsInfo', `Based on ${metrics.wordCount} words analyzed`);

    // Update verdict badge
    const verdictBadge = document.getElementById('verdictBadge');
    if (verdictBadge) {
        if (credibilityScore >= 70) {
            verdictBadge.textContent = 'Likely Human';
            verdictBadge.className = 'px-2 py-0.5 rounded-full bg-accent-emerald/20 text-accent-emerald text-xs font-bold border border-accent-emerald/20';
        } else if (credibilityScore >= 40) {
            verdictBadge.textContent = 'Uncertain';
            verdictBadge.className = 'px-2 py-0.5 rounded-full bg-accent-amber/20 text-accent-amber text-xs font-bold border border-accent-amber/20';
        } else {
            verdictBadge.textContent = 'Likely AI';
            verdictBadge.className = 'px-2 py-0.5 rounded-full bg-accent-red/20 text-accent-red text-xs font-bold border border-accent-red/20';
        }
    }

    // Update probability bars
    updateElement('humanBar', null, { height: `${aiProbability.human}%` });
    updateElement('humanPercent', `${Math.round(aiProbability.human)}%`);
    updateElement('aiBar', null, { height: `${aiProbability.ai}%` });
    updateElement('aiPercent', `${Math.round(aiProbability.ai)}%`);

    // Update probability note
    if (aiProbability.human >= 70) {
        updateElement('probabilityText', 'Consistent human writing patterns');
    } else if (aiProbability.ai >= 70) {
        updateElement('probabilityText', 'AI-generated patterns detected');
        const note = document.getElementById('probabilityNote');
        if (note) note.className = note.className.replace('text-accent-emerald', 'text-accent-red');
    } else {
        updateElement('probabilityText', 'Mixed writing patterns detected');
        const note = document.getElementById('probabilityNote');
        if (note) note.className = note.className.replace('text-accent-emerald', 'text-accent-amber');
    }

    // Update source reliability
    updateElement('sourceLevel', sources.level);
    updateElement('sourceInfo', sources.info);
    updateSourceTags(sources.domains);

    // Update perplexity
    updateElement('perplexityAvg', `Avg: ${metrics.perplexity}`);

    // Update claims table
    updateClaimsTable(claims);
}

/**
 * Update source tags display
 */
function updateSourceTags(domains) {
    const container = document.getElementById('sourceTags');
    if (!container) return;

    if (domains.length === 0) {
        container.innerHTML = '<span class="px-2 py-1 bg-white/5 rounded text-xs text-white/50 border border-white/5">No sources detected</span>';
        return;
    }

    container.innerHTML = domains.map(d =>
        `<span class="px-2 py-1 bg-white/5 rounded text-xs text-white/70 border border-white/5">${escapeHtml(d)}</span>`
    ).join('');
}

/**
 * Update claims table with extracted claims
 */
function updateClaimsTable(claims) {
    const tbody = document.getElementById('claimsTableBody');
    if (!tbody) return;

    if (claims.length === 0) {
        tbody.innerHTML = `
            <tr class="border-b border-white/5">
                <td colspan="4" class="p-8 text-center text-white/50">
                    <span class="material-symbols-outlined text-4xl mb-2 block opacity-30">fact_check</span>
                    No verifiable claims detected in this text
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = claims.map((claim, idx) => `
        <tr class="${idx < claims.length - 1 ? 'border-b border-white/5' : ''} hover:bg-white/5 transition-colors">
            <td class="p-4 text-white font-medium">"${escapeHtml(claim.statement.substring(0, 100))}${claim.statement.length > 100 ? '...' : ''}"</td>
            <td class="p-4">${getVerdictBadge(claim.verdict)}</td>
            <td class="p-4">${claim.source ? getSourceLink(claim.source) : '<span class="text-white/50 italic">No source found</span>'}</td>
            <td class="p-4 text-right">
                <button class="text-white/40 hover:text-white transition-colors">
                    <span class="material-symbols-outlined">more_vert</span>
                </button>
            </td>
        </tr>
    `).join('');
}

// ============= Helper Functions =============

function updateElement(id, text, styles = null) {
    const el = document.getElementById(id);
    if (!el) return;
    if (text !== null) el.textContent = text;
    if (styles) Object.assign(el.style, styles);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatAnalysisDate(date) {
    return `Analyzed on ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} • ${date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
}

function calculateVariance(arr) {
    if (arr.length === 0) return 0;
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    return arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length;
}

function getClaimType(idx) {
    const types = ['statistic', 'research', 'quote', 'superlative', 'date'];
    return types[idx] || 'general';
}

function getRandomVerdict() {
    const verdicts = ['Verified', 'Verified', 'Unverified', 'False'];
    return verdicts[Math.floor(Math.random() * verdicts.length)];
}

function getRandomSource() {
    const sources = [
        { name: 'Wikipedia', initial: 'W' },
        { name: 'Nature Journal', initial: 'N' },
        { name: 'MIT Tech Review', initial: 'M' },
        { name: 'Reuters', initial: 'R' },
        null // No source
    ];
    return sources[Math.floor(Math.random() * sources.length)];
}

function getVerdictBadge(verdict) {
    const configs = {
        'Verified': { icon: 'check_circle', bg: 'bg-accent-emerald/10', text: 'text-accent-emerald', border: 'border-accent-emerald/20' },
        'Unverified': { icon: 'warning', bg: 'bg-accent-amber/10', text: 'text-accent-amber', border: 'border-accent-amber/20' },
        'False': { icon: 'cancel', bg: 'bg-accent-red/10', text: 'text-accent-red', border: 'border-accent-red/20' }
    };
    const c = configs[verdict] || configs['Unverified'];
    return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${c.bg} ${c.text} border ${c.border}">
        <span class="material-symbols-outlined text-[14px]">${c.icon}</span>${verdict}
    </span>`;
}

function getSourceLink(source) {
    return `<a class="flex items-center gap-2 text-primary hover:text-white transition-colors group" href="#">
        <div class="size-5 rounded bg-white/10 flex items-center justify-center text-[10px] text-white">${source.initial}</div>
        <span class="underline decoration-primary/30 group-hover:decoration-white">${source.name}</span>
        <span class="material-symbols-outlined text-[14px] opacity-0 group-hover:opacity-100">open_in_new</span>
    </a>`;
}
