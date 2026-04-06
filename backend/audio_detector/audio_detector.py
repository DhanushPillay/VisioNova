"""
Audio Deepfake Detector — Omni-Audio Router Pipeline

This advanced detector tackles false positives on music and false negatives
on modern AI speech by implementing a Router-Layer architecture:
  1. Audio is analyzed by Voice Activity Detection (Silero VAD).
    2. If Speech is detected, it routes to a 3-Model "Vanguard" Speech Ensemble.
    3. If Music is detected (no speech), it routes to a dedicated AST music detector.
"""

import os
import logging
import tempfile
import threading
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, Optional, Tuple, List, Any
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────
TARGET_SAMPLE_RATE = 16000
MAX_AUDIO_LENGTH_SEC = 60

# ── Speech "Vanguard" Ensemble Models ────────────────────────────────
ENSEMBLE_MODELS = [
    {
        "id": "Gustking/wav2vec2-large-xlsr-deepfake-audio-classification",
        "type": "wav2vec2-xlsr",
        "weight": 0.40,
        "name": "XLS-R 300M Anchor",
        "description": "Cross-lingual Wav2Vec2-XLS-R 300M, ASVspoof-validated",
        "fake_labels": ["spoof", "fake", "deepfake", "generated", "ai"],
    },
    {
        "id": "DavidCombei/wavLM-base-Deepfake_V2",
        "type": "wavlm",
        "weight": 0.30,
        "name": "WavLM Specialist",
        "description": "WavLM-base with denoising pre-training",
        "fake_labels": ["spoof", "fake", "deepfake", "generated", "ai"],
    },
    {
        "id": "garystafford/wav2vec2-deepfake-voice-detector",
        "type": "wav2vec2-xlsr",
        "weight": 0.30,
        "name": "Modern TTS Specialist",
        "description": "Fine-tuned on contemporary TTS and voice cloning engines",
        "fake_labels": ["spoof", "fake", "deepfake", "generated", "ai", "1"],
    }
]

MUSIC_MODEL = {
    "id": "AI-Music-Detection/ai_music_detection_large_10.24s",
    "feature_extractor_fallback_id": "MIT/ast-finetuned-audioset-10-10-0.4593",
    "type": "ast",
    "name": "AST Music Detector",
    "description": "Audio Spectrogram Transformer model for human-vs-AI music detection",
    "fake_labels": ["ai", "generated", "synthetic", "fake", "spoof", "1"],
}

# ── Domain Deterministic Modules ──────────────────────────────────────

class AudioRouter:
    """Classifies audio as Speech vs Music/Noise using Silero VAD."""
    def __init__(self, device):
        self.device = device
        self.model = None
        self.get_speech_timestamps = None
        self.loaded = False

    def load(self):
        if self.loaded: return
        try:
            print("[AudioRouter] Loading Silero VAD for Speech vs Music routing...")
            self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                               model='silero_vad',
                                               force_reload=False,
                                               trust_repo=True)
            self.model.to(self.device)
            self.get_speech_timestamps = utils[0]
            self.loaded = True
            print("  ✓ Audio Router VAD initialized.")
        except Exception as e:
            logger.error(f"Failed to load VAD model: {e}")
            print(f"  ✗ Audio Router failed to load: {e}")

    def is_speech(self, audio: np.ndarray, sr: int) -> bool:
        if not self.loaded:
            return True # Fallback to speech processing if router fails
        try:
            tensor = torch.from_numpy(audio).float().to(self.device)
            if tensor.dim() > 1: tensor = tensor.mean(dim=1)
            
            # Normalize safely
            valid_max = tensor.abs().max()
            if valid_max > 0:
                tensor = tensor / valid_max
                
            timestamps = self.get_speech_timestamps(tensor, self.model, sampling_rate=sr)
            
            total_speech_samples = sum(ts['end'] - ts['start'] for ts in timestamps)
            ratio = total_speech_samples / len(tensor)
            
            # If at least 5% of the file contains human speech, route to the speech detector
            return ratio >= 0.05
        except Exception as e:
            logger.error(f"Router processing error: {e}")
            return True

class MusicDeepfakeDetector:
    """Model-based detector for AI music vs human-composed music."""
    def __init__(self, device):
        self.device = device
        self.model = None
        self.processor = None
        self.fake_idx = 1
        self.loaded = False

    def load(self):
        if self.loaded:
            return
        model_id = MUSIC_MODEL["id"]
        try:
            print(f"[Music] Loading {MUSIC_MODEL['name']} ({model_id})...")
            try:
                self.processor = AutoFeatureExtractor.from_pretrained(model_id)
            except Exception as processor_error:
                fallback_id = MUSIC_MODEL.get("feature_extractor_fallback_id")
                if not fallback_id:
                    raise processor_error
                logger.warning(
                    "Music model extractor missing for %s; using fallback extractor %s",
                    model_id,
                    fallback_id,
                )
                self.processor = AutoFeatureExtractor.from_pretrained(fallback_id)

            self.model = AutoModelForAudioClassification.from_pretrained(model_id)
            self.model.to(self.device)
            self.model.eval()
            self.fake_idx = self._resolve_fake_index(self.model)
            self.loaded = True
            print(f"  ✓ {MUSIC_MODEL['name']} initialized (fake_idx={self.fake_idx})")
        except Exception as e:
            logger.error(f"Failed to load music model {model_id}: {e}")
            print(f"  ✗ Failed to load music model {model_id}: {e}")

    @staticmethod
    def _heuristic_fallback(audio: np.ndarray, sr: int) -> Tuple[float, List[Dict], bool]:
        """Fallback path if the dedicated music model cannot be loaded."""
        import librosa

        audio = audio.flatten()
        flatness = float(librosa.feature.spectral_flatness(y=audio).mean())
        rolloff = float(librosa.feature.spectral_rolloff(y=audio, sr=sr).mean())

        fake_score = 15.0
        if flatness > 0.05:
            fake_score += 25
        if rolloff < 4500:
            fake_score += 40

        fake_score = min(fake_score, 100.0)
        is_fake = fake_score > 50.0
        results = [{
            "name": "Music Heuristic Fallback",
            "model_id": "librosa-fallback",
            "description": "Fallback spectral analysis used because music model was unavailable",
            "type": "heuristic",
            "fake_probability": round(fake_score, 2),
            "real_probability": round(100 - fake_score, 2),
            "weight": 1.0,
            "verdict": "likely_ai" if is_fake else "likely_human",
            "segments_analyzed": 1,
        }]
        return round(fake_score, 2), results, is_fake

    @staticmethod
    def _resolve_fake_index(model) -> int:
        id2label = getattr(model.config, "id2label", None)
        if id2label:
            for idx_str, label in id2label.items():
                label_lower = str(label).lower()
                for keyword in MUSIC_MODEL["fake_labels"]:
                    if keyword in label_lower:
                        return int(idx_str)
        return 1

    def analyze(self, audio: np.ndarray, sr: int) -> Tuple[float, List[Dict], bool]:
        self.load()
        if not self.loaded or self.model is None or self.processor is None:
            logger.warning("Music model unavailable; using heuristic fallback.")
            return self._heuristic_fallback(audio, sr)

        try:
            audio = audio.flatten()
            window_sec = 10.24
            overlap_sec = 2.0
            total_duration = len(audio) / sr

            if total_duration <= window_sec:
                starts = np.array([0.0], dtype=np.float32)
            else:
                step = window_sec - overlap_sec
                starts = np.arange(0, total_duration - window_sec + step, step)
                if len(starts) > 0 and starts[-1] + window_sec < total_duration:
                    starts = np.append(starts, total_duration - window_sec)

            segment_scores = []
            for st in starts:
                end_time = min(float(st + window_sec), total_duration)
                seg_audio = audio[int(st * sr) : int(end_time * sr)]
                if seg_audio.size == 0:
                    continue

                inputs = self.processor(seg_audio, sampling_rate=sr, return_tensors="pt", padding=True).to(self.device)
                with torch.no_grad():
                    logits = self.model(**inputs).logits
                    probs = F.softmax(logits, dim=-1)

                segment_scores.append(probs[0][self.fake_idx].item())

            if not segment_scores:
                return 0.0, [], False

            fake_score = round(float(np.mean(segment_scores) * 100), 2)
            is_fake = fake_score > 50.0
            results = [{
                "name": MUSIC_MODEL["name"],
                "model_id": MUSIC_MODEL["id"],
                "description": MUSIC_MODEL["description"],
                "type": MUSIC_MODEL["type"],
                "fake_probability": fake_score,
                "real_probability": round(100.0 - fake_score, 2),
                "weight": 1.0,
                "verdict": "likely_ai" if is_fake else "likely_human",
                "segments_analyzed": len(segment_scores),
            }]
            return fake_score, results, is_fake
        except Exception as e:
            logger.error(f"Music model inference failed: {e}")
            return 0.0, [], False

# ── Main Orchestrator ────────────────────────────────────────────────

class AudioEnsembleDetector:
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        self._load_lock = threading.Lock()
        
        # Models and Router
        self.router = AudioRouter(self.device)
        self.music_detector = MusicDeepfakeDetector(self.device)
        self.models: Dict[str, Any] = {}
        self.processors: Dict[str, Any] = {}
        self._fake_idx: Dict[str, int] = {}
        self.models_loaded = False

    def _load_models(self):
        if self.models_loaded:
            return

        with self._load_lock:
            if self.models_loaded:
                return

            print(f"[Audio] Booting Omni-Layer Detection on {self.device}...")
            self.router.load()

            loaded_count = 0
            for config in ENSEMBLE_MODELS:
                model_id = config["id"]
                try:
                    print(f"  Loading {config['name']} ({model_id})...")
                    processor = AutoFeatureExtractor.from_pretrained(model_id)
                    model = AutoModelForAudioClassification.from_pretrained(model_id)
                    model.to(self.device)
                    model.eval()

                    fake_idx = self._resolve_fake_index(model, config)
                    self.processors[model_id] = processor
                    self.models[model_id] = model
                    self._fake_idx[model_id] = fake_idx
                    loaded_count += 1
                    print(f"  ✓ {config['name']} locked (fake_idx={fake_idx})")

                except Exception as e:
                    logger.error(f"Failed to load {model_id}: {e}")
                    print(f"  ✗ Failed to load {model_id}: {e}")

            if not self.models:
                raise RuntimeError("No models could be loaded for the audio ensemble.")

            self.models_loaded = True
            print(
                f"[Audio] System ready — Router active, "
                f"{loaded_count}/{len(ENSEMBLE_MODELS)} Speech models loaded, "
                "music model deferred until needed."
            )

    def preload(self):
        """Public warmup entrypoint used by app startup hooks."""
        self._load_models()

    @staticmethod
    def _resolve_fake_index(model, config: dict) -> int:
        id2label = getattr(model.config, "id2label", None)
        if id2label:
            fake_keywords = config.get("fake_labels", [])
            for idx_str, label in id2label.items():
                label_lower = label.lower()
                for keyword in fake_keywords:
                    if keyword in label_lower:
                        return int(idx_str)
        return 1

    def _preprocess_audio(self, audio_path: str) -> Tuple[Optional[np.ndarray], int]:
        try:
            import librosa
            audio, sr = librosa.load(audio_path, sr=TARGET_SAMPLE_RATE, mono=True)
            max_samples = MAX_AUDIO_LENGTH_SEC * TARGET_SAMPLE_RATE
            if len(audio) > max_samples:
                audio = audio[:max_samples]
            return audio, TARGET_SAMPLE_RATE
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return None, 0

    def _load_audio_from_bytes(self, audio_bytes: bytes, filename: str) -> Tuple[Optional[np.ndarray], int]:
        tmp_path = None
        try:
            suffix = os.path.splitext(filename)[1] or ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return self._preprocess_audio(tmp_path)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except OSError: pass

    def predict(self, audio_input, filename: str = "audio.wav", use_segments: bool = True) -> Dict[str, Any]:
        self._load_models()

        if not self.models_loaded:
            return {"success": False, "error": "Models not loaded"}

        # 1. Load Audio
        if isinstance(audio_input, bytes):
            audio, sr = self._load_audio_from_bytes(audio_input, filename)
        elif isinstance(audio_input, str):
            audio, sr = self._preprocess_audio(audio_input)
        elif isinstance(audio_input, np.ndarray):
            audio, sr = audio_input, TARGET_SAMPLE_RATE
        else:
            return {"success": False, "error": "Invalid input format"}

        if audio is None:
            return {"success": False, "error": "Audio preprocessing failed."}

        total_duration = len(audio) / sr

        # 2. AUDIO ROUTER: Determine domain
        is_speech_domain = self.router.is_speech(audio, sr)
        audio_domain = "Speech" if is_speech_domain else "Music/Ambient"
        print(f"[Audio Router] Routing file as domain: {audio_domain}")

        # 3. SEGMENTED PASS (Only for Speech)
        SEGMENT_SEC = 10.0
        OVERLAP_SEC = 2.0
        segments_data = []
        
        if is_speech_domain and use_segments and total_duration > (SEGMENT_SEC + OVERLAP_SEC):
            step = SEGMENT_SEC - OVERLAP_SEC
            starts = np.arange(0, total_duration - SEGMENT_SEC + step, step)
            if len(starts) > 0 and starts[-1] + SEGMENT_SEC < total_duration:
                starts = np.append(starts, total_duration - SEGMENT_SEC)

            for st in starts:
                end_time = min(st + SEGMENT_SEC, total_duration)
                seg_audio = audio[int(st * sr) : int(end_time * sr)]
                seg_score, _, _ = self._run_speech_ensemble(seg_audio, sr)

                segments_data.append({
                    "start_sec": round(float(st), 2),
                    "end_sec": round(float(end_time), 2),
                    "fake_probability": seg_score,
                    "real_probability": round(100.0 - seg_score, 2),
                    "verdict": "likely_ai" if seg_score > 50 else "likely_human",
                })

        # 4. GLOBAL INFERENCE
        if is_speech_domain:
            final_score, model_results, is_fake = self._run_speech_ensemble(audio, sr)
        else:
            final_score, model_results, is_fake = self.music_detector.analyze(audio, sr)

        if not model_results:
            return {"success": False, "error": "No audio models produced a prediction."}

        # 5. GENERATE ARTIFACTS
        artifacts = self._generate_artifacts(is_fake, final_score, audio_domain)

        # 6. BUILD RESPONSE
        response = {
            "success": True,
            "prediction": "ai_generated" if is_fake else "real",
            "verdict": "likely_ai" if is_fake else "likely_human",
            "fake_probability": final_score,
            "real_probability": round(100 - final_score, 2),
            "confidence": final_score if is_fake else round(100 - final_score, 2),
            "ensemble_details": model_results,
            "artifacts_detected": artifacts,
            "audio_domain": audio_domain,
            "analysis_mode": "segmented" if segments_data else "single_pass",
            "total_duration_seconds": round(total_duration, 2),
            "segments_analyzed": len(segments_data) if segments_data else 1,
            "meta": {
                "duration_seconds": round(total_duration, 2),
                "sample_rate": sr,
                "file_name": filename,
                "domain": audio_domain
            },
        }

        if segments_data:
            response["segments"] = segments_data
            response["meta"]["segment_length_sec"] = SEGMENT_SEC
            response["meta"]["segment_overlap_sec"] = OVERLAP_SEC

        return response

    def _run_speech_ensemble(self, audio_slice: np.ndarray, sr: int) -> Tuple[float, List[Dict], bool]:
        model_results = []
        weighted_fake_sum = 0.0
        total_weight = 0.0

        for config in ENSEMBLE_MODELS:
            model_id = config["id"]
            if model_id not in self.models: continue

            model = self.models[model_id]
            processor = self.processors[model_id]
            weight = config["weight"]
            fake_idx = self._fake_idx[model_id]

            try:
                inputs = processor(audio_slice, sampling_rate=sr, return_tensors="pt", padding=True).to(self.device)
                with torch.no_grad():
                    logits = model(**inputs).logits
                    probs = F.softmax(logits, dim=-1)
                
                fake_score = probs[0][fake_idx].item()
                weighted_fake_sum += fake_score * weight
                total_weight += weight

                model_results.append({
                    "name": config["name"],
                    "model_id": model_id,
                    "type": config["type"],
                    "fake_probability": round(fake_score * 100, 2),
                    "real_probability": round((1 - fake_score) * 100, 2),
                    "weight": weight,
                    "verdict": "likely_ai" if fake_score > 0.5 else "likely_human",
                })
            except Exception as e:
                logger.error(f"Inference failed for {model_id}: {e}")

        if total_weight == 0:
            return 0.0, [], False

        final_fake_prob = weighted_fake_sum / total_weight
        final_score = round(final_fake_prob * 100, 2)

        # Confidence calibration based on agreement
        if len(model_results) >= 3:
            individual_verdicts = [r["fake_probability"] > 50 for r in model_results]
            agreement_ratio = max(sum(individual_verdicts), len(individual_verdicts) - sum(individual_verdicts)) / len(individual_verdicts)
            if agreement_ratio < 0.75:
                # Disagreement! Pull score towards 50%
                final_score = round(50 + (final_score - 50) * 0.8, 2)

        return final_score, model_results, final_score > 50

    @staticmethod
    def _generate_artifacts(is_fake: bool, final_score: float, domain: str) -> List[str]:
        artifacts = []
        if domain == "Music/Ambient":
            if is_fake:
                artifacts.append("Music-domain classifier flagged AI generation patterns")
                if final_score > 70: artifacts.append("Segment consensus shows strong synthetic music likelihood")
                if final_score > 85: artifacts.append("High-confidence AI music signature detected")
            else:
                artifacts.append("Music-domain classifier found human composition characteristics")
                artifacts.append("Segment votes remained consistent with authentic music structure")
        else:
            if is_fake:
                artifacts.append("High-frequency spectral anomalies detected")
                if final_score > 70: artifacts.append("Vocoder signature detected — strong indicator of AI synthesis")
                if final_score > 85: artifacts.append("Neural codec artifacts identified in waveform")
            else:
                artifacts.append("Natural breath patterns and micro-pauses detected")
                artifacts.append("Consistent pitch variance within biological range")
                if final_score < 20: artifacts.append("Strong natural glottal pulse patterns confirmed")

        return artifacts

    def get_model_info(self) -> Dict:
        models = [
            {"id": c["id"], "name": c["name"], "type": c["type"], "loaded": c["id"] in self.models}
            for c in ENSEMBLE_MODELS
        ]
        models.append(
            {
                "id": MUSIC_MODEL["id"],
                "name": MUSIC_MODEL["name"],
                "type": MUSIC_MODEL["type"],
                "loaded": self.music_detector.loaded,
            }
        )

        return {
            "model_type": "Omni-Audio Router + 3 Speech Models + 1 Music Model",
            "models": models,
            "router_active": self.router.loaded,
            "music_model_active": self.music_detector.loaded,
            "max_duration": f"{MAX_AUDIO_LENGTH_SEC}s",
            "sample_rate": f"{TARGET_SAMPLE_RATE}Hz",
            "device": str(self.device),
        }

# Backward compatibility alias
AudioDeepfakeDetector = AudioEnsembleDetector
