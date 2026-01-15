/**
 * VisioNova Text Result Page
 * Handles dynamic text content loading and mock analysis results
 */

document.addEventListener('DOMContentLoaded', function () {
    const textData = VisioNovaStorage.getFile('text');

    if (textData) {
        updateElement('pageTitle', 'Analysis: ' + textData.fileName);

        // Display the uploaded text
        const placeholder = document.getElementById('noTextPlaceholder');
        const uploadedText = document.getElementById('uploadedText');

        if (uploadedText) {
            const paragraphs = textData.data.split('\n\n').filter(p => p.trim());
            let formattedHtml = paragraphs.map(p =>
                `<p class="mb-4">${p.replace(/\n/g, '<br>')}</p>`
            ).join('');

            if (!formattedHtml) {
                formattedHtml = `<p class="mb-4">${textData.data.replace(/\n/g, '<br>')}</p>`;
            }

            uploadedText.innerHTML = formattedHtml;
            uploadedText.classList.remove('hidden');
        }
        if (placeholder) {
            placeholder.classList.add('hidden');
        }

        // Generate and display mock analysis results
        displayTextAnalysis(textData);
    } else {
        updateElement('pageTitle', 'Text Analysis');
    }
});

function displayTextAnalysis(fileData) {
    const hash = hashString(fileData.fileName);
    const text = fileData.data;

    // Calculate text metrics
    const wordCount = text.split(/\s+/).filter(w => w).length;
    const charCount = text.length;
    const sentenceCount = (text.match(/[.!?]+/g) || []).length || 1;
    const avgWordsPerSentence = Math.round(wordCount / sentenceCount);

    // Generate scores
    const authenticityScore = 45 + (hash % 50);
    const sentimentScore = 40 + (hash % 40);
    const styleScore = 50 + (hash % 45);
    const isAIGenerated = authenticityScore < 60;

    // Update authenticity score
    updateScoreDisplay(authenticityScore, isAIGenerated);

    // Update word count
    updateElement('wordCount', wordCount.toLocaleString());
    updateElement('charCount', charCount.toLocaleString());

    // Update sentiment
    const sentiments = ['Positive', 'Neutral', 'Negative', 'Mixed'];
    const sentiment = sentiments[hash % 4];
    document.querySelectorAll('.text-xl.font-black, .text-2xl.font-black').forEach(el => {
        if (el.closest('[class*="Sentiment"]') || el.textContent.match(/Positive|Neutral|Negative/)) {
            el.textContent = sentiment;
        }
    });

    // Update style analysis
    const styles = ['Formal', 'Casual', 'Academic', 'Journalistic'];
    document.querySelectorAll('.text-xl.font-black').forEach(el => {
        if (el.textContent.match(/Formal|Casual|Academic/)) {
            el.textContent = styles[hash % 4];
        }
    });

    // Update perplexity score (AI detection metric)
    const perplexity = 10 + (hash % 90);
    updateElement('perplexityScore', perplexity.toFixed(1));

    // Animate progress bars
    animateProgressBars(hash);
}

function updateScoreDisplay(score, isAIGenerated) {
    const scoreElement = document.querySelector('.text-5xl.font-black, .text-4xl.font-black');
    if (scoreElement) {
        scoreElement.textContent = score;
    }

    const scoreCircle = document.querySelector('circle[stroke="#00D991"], circle[stroke="#FF4A4A"]');
    if (scoreCircle) {
        const circumference = 251.2;
        const offset = circumference - (score / 100) * circumference;
        scoreCircle.setAttribute('stroke-dashoffset', offset);
        scoreCircle.setAttribute('stroke', isAIGenerated ? '#FF4A4A' : '#00D991');
    }

    const verdictLabel = document.querySelector('[class*="AI-Generated"], [class*="Human"]');
    if (verdictLabel) {
        verdictLabel.textContent = isAIGenerated ? 'LIKELY AI-GENERATED' : 'LIKELY HUMAN-WRITTEN';
    }
}

function animateProgressBars(hash) {
    const bars = document.querySelectorAll('.bg-accent-blue, .bg-primary, .bg-green-500');
    bars.forEach((bar, index) => {
        const width = 30 + ((hash + index * 19) % 60);
        bar.style.transition = 'width 1s ease-out';
        setTimeout(() => { bar.style.width = width + '%'; }, index * 150);
    });
}

function updateElement(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash = hash & hash;
    }
    return Math.abs(hash);
}
