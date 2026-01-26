/**
 * VisioNova Result Page - Image Analysis
 * Handles dynamic content loading from sessionStorage and displays mock analysis results
 */

document.addEventListener('DOMContentLoaded', function () {
    const imageData = VisioNovaStorage.getFile('image');

    if (imageData) {
        // Update page title with filename
        updateElement('pageTitle', 'Analysis: ' + imageData.fileName);

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

        // Generate and display mock analysis results
        displayAnalysisResults(imageData);

        // Load text detection result (if AnalysisDashboard stored it)
        loadTextDetectionResult();
    } else {
        updateElement('analysisTime', 'No analysis performed');
        updateElement('pageTitle', 'Image Analysis');
    }
});

/**
 * Generate mock analysis results based on file data
 */
function displayAnalysisResults(fileData) {
    // Generate random but consistent scores based on filename hash
    const hash = hashString(fileData.fileName);
    const authenticityScore = 40 + (hash % 55); // 40-95
    const fakeScore = 100 - authenticityScore;
    const isFake = fakeScore > 50;

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
        scoreCircle.setAttribute('stroke', isFake ? '#FF4A4A' : '#00D991');
    }

    // Update verdict text
    const verdictElements = document.querySelectorAll('[class*="text-accent-green"], [class*="text-success"]');
    verdictElements.forEach(el => {
        if (el.textContent.includes('Authentic') || el.textContent.includes('LIKELY')) {
            el.textContent = isFake ? 'LIKELY MANIPULATED' : 'LIKELY AUTHENTIC';
            el.className = el.className.replace(/text-(accent-green|success|accent-red|danger)/g,
                isFake ? 'text-accent-red' : 'text-accent-green');
        }
    });

    // Update fake probability
    const probElements = document.querySelectorAll('.font-mono, .text-2xl');
    probElements.forEach(el => {
        if (el.textContent.includes('%') && el.textContent.includes('Fake')) {
            const parent = el.closest('div');
            if (parent) {
                parent.innerHTML = `<span class="text-2xl font-black ${isFake ? 'text-accent-red' : 'text-accent-green'}">${fakeScore}%</span><br><span class="text-xs text-gray-400">Fake Probability</span>`;
            }
        }
    });

    // Update file metadata
    updateElement('fileName', fileData.fileName);
    updateElement('fileType', fileData.mimeType.split('/')[1]?.toUpperCase() || 'IMAGE');
    updateElement('fileSize', formatFileSize(fileData.data.length * 0.75)); // Approximate base64 decoded size

    // Animate bars and metrics
    animateProgressBars(hash);
}

/**
 * Animate progress bars with random values
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
