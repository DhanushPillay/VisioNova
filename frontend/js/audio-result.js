/**
 * VisioNova Audio Result Page
 * Handles dynamic audio content loading and mock analysis results
 */

document.addEventListener('DOMContentLoaded', function () {
    const audioData = VisioNovaStorage.getFile('audio');

    if (audioData) {
        updateElement('pageTitle', audioData.fileName);

        // Display the uploaded audio
        const placeholder = document.getElementById('noAudioPlaceholder');
        const uploadedAudio = document.getElementById('uploadedAudio');
        const spectrogramBg = document.getElementById('spectrogramBg');

        if (uploadedAudio) {
            uploadedAudio.src = audioData.data;
            uploadedAudio.classList.remove('hidden');
        }
        if (placeholder) {
            placeholder.classList.add('hidden');
        }
        if (spectrogramBg) {
            spectrogramBg.classList.remove('hidden');
        }

        // Generate and display mock analysis results
        displayAudioAnalysis(audioData);
    } else {
        updateElement('pageTitle', 'Audio Analysis');
    }
});

function displayAudioAnalysis(fileData) {
    const hash = hashString(fileData.fileName);
    const authenticityScore = 30 + (hash % 65);
    const fakeScore = 100 - authenticityScore;
    const isFake = fakeScore > 50;

    // Update overall score
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

    // Update verdict
    const verdictLabel = document.querySelector('[class*="SUSPICIOUS"], [class*="AUTHENTIC"]');
    if (verdictLabel) {
        verdictLabel.textContent = isFake ? 'HIGHLY SUSPICIOUS' : 'LIKELY AUTHENTIC';
    }

    // Update fake probability
    const probLabel = document.querySelector('.text-accent-red, .text-danger');
    if (probLabel && probLabel.textContent.includes('%')) {
        probLabel.textContent = fakeScore + '% FAKE';
    }

    // Update duration display
    const mins = Math.floor((hash % 300) / 60);
    const secs = (hash % 300) % 60;
    updateElement('audioDuration', `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`);

    // Update sample rate
    const rates = ['44.1 kHz', '48 kHz', '96 kHz'];
    updateElement('sampleRate', rates[hash % 3]);

    // Update analysis metrics
    const pitchStability = ['Stable', 'Unstable', 'Variable'][hash % 3];
    const bgNoise = ['-60dB', '-45dB', '-30dB'][hash % 3];
    const formant = ['Natural', 'Synthetic', 'Modified'][hash % 3];

    document.querySelectorAll('.text-xl.font-black').forEach((el, i) => {
        if (el.textContent.includes('Stable') || el.textContent.includes('Unstable')) {
            el.textContent = pitchStability;
        } else if (el.textContent.includes('dB')) {
            el.textContent = bgNoise;
        } else if (el.textContent.includes('Synthetic') || el.textContent.includes('Natural')) {
            el.textContent = formant;
        }
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
