/**
 * VisioNova Result Page - Image Analysis
 * Handles image analysis using the backend API and displays real results
 */

// API Configuration
const API_BASE_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', async function () {
    const imageData = VisioNovaStorage.getFile('image');

    if (imageData) {
        // Update page title with filename
        updateElement('pageTitle', 'Analyzing: ' + imageData.fileName);

        // Update timestamp
        const date = new Date(imageData.timestamp);
        updateElement('analysisTime', date.toLocaleDateString() + ' at ' + date.toLocaleTimeString());

        // Display the uploaded image
        const uploadedImage = document.getElementById('uploadedImage');
        const placeholder = document.getElementById('noImagePlaceholder');

        if (uploadedImage) {
            uploadedImage.src = imageData.data;
            uploadedImage.classList.remove('hidden');
        }
        if (placeholder) {
            placeholder.classList.add('hidden');
        }

        // Show loading state
        showLoadingState();

        // Call the backend API for analysis
        try {
            const analysisResult = await analyzeImage(imageData);
            displayAnalysisResults(analysisResult, imageData);
        } catch (error) {
            console.error('Analysis failed:', error);
            displayError(error.message || 'Analysis failed. Please try again.');
            // Fall back to mock results
            displayMockResults(imageData);
        }

        // Load text detection result (if AnalysisDashboard stored it)
        loadTextDetectionResult();
    } else {
        updateElement('analysisTime', 'No analysis performed');
        updateElement('pageTitle', 'Image Analysis');
    }
});

/**
 * Call the backend API to analyze the image
 */
async function analyzeImage(imageData) {
    const response = await fetch(`${API_BASE_URL}/api/detect-image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageData.data,
            filename: imageData.fileName,
            include_ela: true,
            include_metadata: true
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API error: ${response.status}`);
    }

    return await response.json();
}

/**
 * Show loading state while analyzing
 */
function showLoadingState() {
    const scoreElement = document.querySelector('.text-5xl.font-black, .text-4xl.font-black');
    if (scoreElement) {
        scoreElement.textContent = '...';
    }
    
    // Add loading spinner or pulse animation
    const verdictElements = document.querySelectorAll('[class*="text-accent-green"], [class*="text-success"]');
    verdictElements.forEach(el => {
        if (el.textContent.includes('Authentic') || el.textContent.includes('LIKELY')) {
            el.textContent = 'ANALYZING...';
            el.className = el.className.replace(/text-(accent-green|success|accent-red|danger)/g, 'text-gray-400');
        }
    });
}

/**
 * Display real analysis results from the API
 */
function displayAnalysisResults(result, fileData) {
    if (!result.success) {
        displayError(result.error || 'Analysis failed');
        return;
    }

    const aiProbability = result.ai_probability || 50;
    const authenticityScore = Math.round(100 - aiProbability);
    const isLikelyAI = aiProbability > 50;
    const verdict = result.verdict || (isLikelyAI ? 'LIKELY_AI' : 'LIKELY_REAL');

    // Update page title
    updateElement('pageTitle', 'Analysis: ' + fileData.fileName);

    // Update overall score display
    const scoreElement = document.querySelector('.text-5xl.font-black, .text-4xl.font-black');
    if (scoreElement) {
        scoreElement.textContent = authenticityScore;
    }

    // Update score circle
    const scoreCircle = document.querySelector('circle[stroke="#00D991"], circle[stroke="#FF4A4A"]');
    if (scoreCircle) {
        const circumference = 251.2;
        const offset = circumference - (authenticityScore / 100) * circumference;
        scoreCircle.setAttribute('stroke-dashoffset', offset);
        scoreCircle.setAttribute('stroke', isLikelyAI ? '#FF4A4A' : '#00D991');
    }

    // Update verdict text
    const verdictElements = document.querySelectorAll('[class*="text-accent-green"], [class*="text-success"], [class*="text-gray-400"]');
    verdictElements.forEach(el => {
        if (el.textContent.includes('Authentic') || el.textContent.includes('LIKELY') || el.textContent.includes('ANALYZING')) {
            el.textContent = getVerdictText(verdict);
            el.className = el.className.replace(/text-(accent-green|success|accent-red|danger|gray-400)/g,
                isLikelyAI ? 'text-accent-red' : 'text-accent-green');
        }
    });

    // Update AI probability display
    const probElements = document.querySelectorAll('.font-mono, .text-2xl');
    probElements.forEach(el => {
        if (el.textContent.includes('%') || el.parentElement?.textContent.includes('Fake')) {
            const parent = el.closest('div');
            if (parent && parent.innerHTML.includes('Probability')) {
                parent.innerHTML = `<span class="text-2xl font-black ${isLikelyAI ? 'text-accent-red' : 'text-accent-green'}">${aiProbability.toFixed(1)}%</span><br><span class="text-xs text-gray-400">AI Probability</span>`;
            }
        }
    });

    // Update file metadata
    updateElement('fileName', fileData.fileName);
    updateElement('fileType', fileData.mimeType.split('/')[1]?.toUpperCase() || 'IMAGE');
    updateElement('fileSize', formatFileSize(fileData.data.length * 0.75));

    // Update analysis scores from API
    if (result.analysis_scores) {
        updateAnalysisScores(result.analysis_scores);
    }

    // Update metadata analysis
    if (result.metadata) {
        updateMetadataDisplay(result.metadata);
    }

    // Update ELA display
    if (result.ela) {
        updateELADisplay(result.ela);
    }

    // Animate progress bars based on actual scores
    animateProgressBarsWithScores(result.analysis_scores || {});

    // Store result for potential export
    sessionStorage.setItem('visioNova_image_result', JSON.stringify(result));
}

/**
 * Get human-readable verdict text
 */
function getVerdictText(verdict) {
    const verdictMap = {
        'AI_GENERATED': 'AI GENERATED',
        'LIKELY_AI': 'LIKELY AI GENERATED',
        'UNCERTAIN': 'UNCERTAIN',
        'LIKELY_REAL': 'LIKELY AUTHENTIC',
        'REAL': 'AUTHENTIC',
        'ERROR': 'ANALYSIS ERROR'
    };
    return verdictMap[verdict] || verdict;
}

/**
 * Update analysis score displays
 */
function updateAnalysisScores(scores) {
    // Map score names to display elements
    const scoreMapping = {
        'noise_consistency': 'noiseScore',
        'frequency_anomaly': 'frequencyScore',
        'color_uniformity': 'colorScore',
        'edge_naturalness': 'edgeScore',
        'texture_quality': 'textureScore'
    };

    for (const [apiKey, elementId] of Object.entries(scoreMapping)) {
        if (scores[apiKey] !== undefined) {
            const value = Math.round(scores[apiKey]);
            updateElement(elementId, `${value}%`);
            
            // Update progress bar if exists
            const bar = document.getElementById(`${elementId}Bar`);
            if (bar) {
                bar.style.width = `${value}%`;
                bar.style.backgroundColor = value > 60 ? '#FF4A4A' : value > 30 ? '#FFC107' : '#00D991';
            }
        }
    }
}

/**
 * Update metadata display section
 */
function updateMetadataDisplay(metadata) {
    const metadataSection = document.getElementById('metadataSection');
    if (!metadataSection) return;

    // Update EXIF status
    const exifStatus = document.getElementById('exifStatus');
    if (exifStatus) {
        if (metadata.has_exif) {
            exifStatus.textContent = 'EXIF Data Present';
            exifStatus.className = exifStatus.className.replace(/text-\w+-\d+/g, 'text-green-400');
        } else {
            exifStatus.textContent = 'No EXIF Data (Suspicious)';
            exifStatus.className = exifStatus.className.replace(/text-\w+-\d+/g, 'text-red-400');
        }
    }

    // Update camera info
    if (metadata.camera_make || metadata.camera_model) {
        updateElement('cameraInfo', `${metadata.camera_make || ''} ${metadata.camera_model || ''}`.trim());
    } else {
        updateElement('cameraInfo', 'No camera information');
    }

    // Update software detection
    if (metadata.ai_software_detected) {
        updateElement('softwareInfo', `AI Software Detected: ${metadata.software_detected}`);
        const softwareEl = document.getElementById('softwareInfo');
        if (softwareEl) softwareEl.className = softwareEl.className.replace(/text-\w+-\d+/g, 'text-red-400');
    } else if (metadata.software_detected) {
        updateElement('softwareInfo', `Software: ${metadata.software_detected}`);
    }

    // Display anomalies
    if (metadata.anomalies && metadata.anomalies.length > 0) {
        const anomaliesList = document.getElementById('anomaliesList');
        if (anomaliesList) {
            anomaliesList.innerHTML = metadata.anomalies
                .map(a => `<li class="text-yellow-400 text-sm">⚠️ ${a}</li>`)
                .join('');
        }
    }
}

/**
 * Update ELA display section
 */
function updateELADisplay(ela) {
    if (!ela.success) return;

    // Update ELA image if element exists
    const elaImage = document.getElementById('elaImage');
    if (elaImage && ela.ela_image) {
        elaImage.src = `data:image/png;base64,${ela.ela_image}`;
        elaImage.classList.remove('hidden');
    }

    // Update manipulation likelihood
    updateElement('manipulationScore', `${Math.round(ela.manipulation_likelihood || 0)}%`);

    // Update suspicious regions count
    if (ela.suspicious_regions) {
        updateElement('suspiciousRegions', `${ela.suspicious_regions.length} region(s) detected`);
    }
}

/**
 * Animate progress bars with actual API scores
 */
function animateProgressBarsWithScores(scores) {
    const bars = document.querySelectorAll('.bg-accent-blue, .bg-primary, [data-score-bar]');
    
    const scoreValues = Object.values(scores);
    bars.forEach((bar, index) => {
        const width = scoreValues[index % scoreValues.length] || 50;
        bar.style.transition = 'width 1s ease-out';
        bar.style.width = width + '%';
        
        // Color based on score (higher = more AI-like = red)
        if (width > 60) {
            bar.style.backgroundColor = '#FF4A4A';
        } else if (width > 30) {
            bar.style.backgroundColor = '#FFC107';
        } else {
            bar.style.backgroundColor = '#00D991';
        }
    });
}

/**
 * Display error message
 */
function displayError(message) {
    console.error('Analysis error:', message);
    
    const verdictElements = document.querySelectorAll('[class*="text-accent-green"], [class*="text-success"]');
    verdictElements.forEach(el => {
        if (el.textContent.includes('Authentic') || el.textContent.includes('LIKELY') || el.textContent.includes('ANALYZING')) {
            el.textContent = 'ANALYSIS FAILED';
            el.className = el.className.replace(/text-(accent-green|success|gray-400)/g, 'text-yellow-500');
        }
    });
}

/**
 * Fall back to mock results if API fails
 */
function displayMockResults(fileData) {
    const hash = hashString(fileData.fileName);
    const authenticityScore = 40 + (hash % 55);
    const fakeScore = 100 - authenticityScore;
    const isFake = fakeScore > 50;

    const scoreElement = document.querySelector('.text-5xl.font-black, .text-4xl.font-black');
    if (scoreElement) {
        scoreElement.textContent = authenticityScore;
    }

    const scoreCircle = document.querySelector('circle[stroke="#00D991"], circle[stroke="#FF4A4A"]');
    if (scoreCircle) {
        const circumference = 251.2;
        const offset = circumference - (authenticityScore / 100) * circumference;
        scoreCircle.setAttribute('stroke-dashoffset', offset);
        scoreCircle.setAttribute('stroke', isFake ? '#FF4A4A' : '#00D991');
    }

    animateProgressBars(hash);
}

/**
 * Animate progress bars with random values (fallback)
 */
function animateProgressBars(hash) {
    const bars = document.querySelectorAll('.bg-accent-blue, .bg-primary');
    bars.forEach((bar, index) => {
        const width = 30 + ((hash + index * 17) % 60);
        bar.style.transition = 'width 1s ease-out';
        bar.style.width = width + '%';
    });
}

/**
 * Helper to update element text content
 */
function updateElement(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

/**
 * Simple string hash function
 */
function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash);
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

/**
 * Load text detection result stored by AnalysisDashboard and display it
 */
function loadTextDetectionResult() {
    const raw = sessionStorage.getItem('visioNova_text_result');
    if (!raw) return;
    try {
        const res = JSON.parse(raw);
        const prediction = res.prediction || 'N/A';
        const confidence = res.confidence != null ? (Number(res.confidence).toFixed(2) + '%') : 'N/A';

        const predEl = document.getElementById('td_prediction');
        const confEl = document.getElementById('td_confidence');
        const decEl = document.getElementById('td_decision');

        if (predEl) predEl.querySelector('span') ? predEl.querySelector('span').textContent = prediction : predEl.textContent = 'Prediction: ' + prediction;
        if (confEl) confEl.querySelector('span') ? confEl.querySelector('span').textContent = confidence : confEl.textContent = 'Confidence: ' + confidence;

        let decisionText = 'N/A';
        if (res.prediction === 'uncertain' && res.decision) {
            const leaning = res.decision.leaning || res.decision.reason || 'unknown';
            const margin = res.decision.margin != null ? Number(res.decision.margin).toFixed(3) : 'n/a';
            decisionText = `Uncertain — leaning: ${leaning} (margin ${margin})`;
        } else if (res.decision) {
            try { decisionText = typeof res.decision === 'string' ? res.decision : JSON.stringify(res.decision); } catch(e) { decisionText = String(res.decision); }
        }

        if (decEl) decEl.querySelector('span') ? decEl.querySelector('span').textContent = decisionText : decEl.textContent = 'Decision: ' + decisionText;
    } catch (e) {
        console.error('Failed to parse visioNova_text_result:', e);
    }
}
