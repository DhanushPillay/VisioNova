"""
VisioNova Audio Detector Module
Detects AI-generated and deepfake audio using a domain-aware stack.

Speech Ensemble Members:
- Gustking/wav2vec2-large-xlsr-deepfake-audio-classification (XLS-R 300M, EER 4.01%)
- DavidCombei/wavLM-base-Deepfake_V2 (WavLM-base, 99.62% accuracy)
- garystafford/wav2vec2-deepfake-voice-detector (Wav2Vec2-XLS-R, modern TTS focus)

Music Model:
- AI-Music-Detection/ai_music_detection_large_10.24s (AST-based AI music classifier)

Supports 16kHz mono audio input up to 60 seconds.
"""

from .audio_detector import AudioDeepfakeDetector, AudioEnsembleDetector

__all__ = [
    'AudioDeepfakeDetector',
    'AudioEnsembleDetector',
]
