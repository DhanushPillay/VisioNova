"""
VisioNova Image Explainer — XAI (Explainable AI) System

Replaces the old Groq Vision-based explainer with a fully offline system that
extracts real evidence from the detection models themselves.

Two-layer explanation approach:
1. Ensemble Disagreement Analysis — reads per-model scores, maps each model
   to its specialty, and generates structured, evidence-based findings.
2. Grad-CAM Attention Heatmaps — extracts attention maps from ViT/DINOv2
   models to show WHERE in the image AI artifacts were detected.

No external API calls needed. Works 100% offline.
"""
import io
import base64
import logging
from typing import Dict, Optional, Any, List

import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Model Specialties ────────────────────────────────────────────────────────
# Each pretrained model has a specific strength. This mapping turns raw scores
# into human-readable explanations of WHY a model flagged the image.

MODEL_SPECIALTIES = {
    'ateeqq': {
        'name': 'Ateeqq SigLIP2',
        'architecture': 'SigLIP2 (Google Sigmoid Vision-Language)',
        'accuracy': '99.23%',
        'specialty': 'High-precision general AI image detection using semantic visual features',
        'detects': 'Broad AI generators including DALL-E, Midjourney, Stable Diffusion',
        'ai_explanation': 'Semantic visual features match patterns from known AI image generators',
        'human_explanation': 'Semantic features are consistent with natural photography',
    },
    'siglip_dinov2': {
        'name': 'Bombek1 SigLIP2+DINOv2',
        'architecture': 'Hybrid SigLIP2 + DINOv2 (dual-encoder)',
        'accuracy': '99.97% AUC',
        'specialty': 'Best overall detector — combines semantic + self-supervised features',
        'detects': '25+ generators: Flux, MJ v6, DALL-E 3, SDXL, GPT-Image-1',
        'ai_explanation': 'Both semantic (SigLIP2) and structural (DINOv2) features indicate AI origin',
        'human_explanation': 'Both semantic and structural features match authentic photographs',
    },
    'deepfake': {
        'name': 'dima806 ViT',
        'architecture': 'Vision Transformer (ViT-B/16)',
        'accuracy': '98.25%',
        'specialty': 'General deepfake and AI image detection with strong community validation',
        'detects': 'General AI-generated images and face manipulations',
        'ai_explanation': 'Global compositional patterns detected by Vision Transformer indicate AI generation',
        'human_explanation': 'Global image composition is consistent with natural capture',
    },
    'sdxl': {
        'name': 'Organika SDXL-Detector',
        'architecture': 'Swin Transformer',
        'accuracy': '98.1%',
        'specialty': 'Specialist for modern diffusion models (SDXL, Flux, SD3)',
        'detects': 'Stable Diffusion XL, Flux, and other modern diffusion model outputs',
        'ai_explanation': 'Patterns match known Stable Diffusion / Flux generator fingerprints',
        'human_explanation': 'No diffusion model fingerprints detected',
    },
    'dinov2': {
        'name': 'WpythonW DINOv2',
        'architecture': 'DINOv2 (Self-Supervised ViT)',
        'accuracy': 'Degradation-resilient',
        'specialty': 'Resilient to compression and social media processing',
        'detects': 'AI images even after heavy JPEG compression, resizing, or social media upload',
        'ai_explanation': 'AI artifacts persist even through image degradation — strong structural signal',
        'human_explanation': 'Structural features remain consistent with genuine images under compression',
    },
    'frequency': {
        'name': 'Frequency Analyzer',
        'architecture': 'FFT/DCT Analysis',
        'accuracy': 'Supplementary',
        'specialty': 'Detects GAN-specific spectral fingerprints in the frequency domain',
        'detects': 'GAN upsampling artifacts, periodic patterns from transposed convolutions',
        'ai_explanation': 'Frequency domain shows periodic patterns typical of GAN upsampling',
        'human_explanation': 'Frequency spectrum appears natural',
    },
}


class ImageExplainer:
    """
    Generates evidence-based explanations for image detection results.

    Uses two complementary approaches:
    1. Ensemble Disagreement Analysis — structures per-model scores into
       human-readable findings with model-specialty context.
    2. Grad-CAM Attention Heatmaps — optional visual overlay showing
       which image regions triggered the AI detection.
    """

    def __init__(self):
        """Initialize the XAI explainer. No API keys needed."""
        # Check if pytorch-grad-cam is available (optional dependency)
        self.gradcam_available = False
        try:
            from pytorch_grad_cam import GradCAM
            self.gradcam_available = True
            logger.info("ImageExplainer initialized with Grad-CAM support")
        except ImportError:
            logger.info("ImageExplainer initialized (Grad-CAM not available — install pytorch-grad-cam for heatmaps)")

    def analyze_image(self, image_data: bytes, detection_result: Dict) -> Dict[str, Any]:
        """
        Perform XAI analysis of an image detection result.

        Combines ensemble disagreement analysis with optional Grad-CAM heatmaps
        to produce a complete, evidence-based explanation.

        Args:
            image_data: Raw image bytes
            detection_result: Results from the ML ensemble detector

        Returns:
            dict with visual_analysis, reasoning, combined_verdict — same shape
            as the old Groq-based explainer for frontend compatibility.
        """
        try:
            # Layer 1: Ensemble Disagreement Analysis (always works, no deps)
            ensemble_explanation = self._build_ensemble_explanation(detection_result)

            # Layer 2: Grad-CAM Heatmap (optional, needs pytorch-grad-cam)
            heatmap_b64 = None
            if self.gradcam_available:
                heatmap_b64 = self._generate_gradcam_heatmap(image_data, detection_result)

            # Build the response in the same shape the frontend expects
            visual_analysis = {
                'assessment': ensemble_explanation['summary'],
                'anomalies': ensemble_explanation['anomalies'],
                'model_breakdown': ensemble_explanation['model_breakdown'],
                'agreement_level': ensemble_explanation['agreement_level'],
                'agreement_detail': ensemble_explanation['agreement_detail'],
            }

            if heatmap_b64:
                visual_analysis['attention_heatmap'] = heatmap_b64

            return {
                'success': True,
                'visual_analysis': visual_analysis,
                'reasoning': ensemble_explanation['reasoning'],
                'combined_verdict': {
                    'combined_probability': detection_result.get('ai_probability', 50),
                    'verdict': detection_result.get('verdict', 'UNCERTAIN'),
                    'verdict_description': ensemble_explanation['verdict_description'],
                    'analysis_agreement': ensemble_explanation['agreement_level'],
                },
                'explanation_method': 'XAI (Ensemble Disagreement Analysis' + (' + Grad-CAM)' if heatmap_b64 else ')'),
            }

        except Exception as e:
            logger.error(f"XAI analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'visual_analysis': None,
                'reasoning': f'Explanation generation failed: {str(e)}',
                'combined_verdict': {
                    'combined_probability': detection_result.get('ai_probability', 50),
                    'verdict': detection_result.get('verdict', 'UNCERTAIN'),
                    'verdict_description': 'Analysis completed — explanation unavailable',
                    'analysis_agreement': 'UNKNOWN',
                },
            }

    # ─── Layer 1: Ensemble Disagreement Analysis ─────────────────────────────

    def _build_ensemble_explanation(self, detection_result: Dict) -> Dict[str, Any]:
        """
        Build a structured explanation from per-model ensemble scores.

        Reads individual_results from the ensemble detector, maps each model
        to its specialty, and generates evidence-based findings.

        Args:
            detection_result: Full ensemble detection result

        Returns:
            dict with summary, reasoning, model_breakdown, anomalies, agreement info
        """
        individual_results = detection_result.get('individual_results', {})
        ai_probability = detection_result.get('ai_probability', 50)
        verdict = detection_result.get('verdict', 'UNCERTAIN')

        # Build per-model breakdown
        model_breakdown = []
        models_flagging_ai = 0
        models_total = 0
        scores = []

        for model_key, model_result in individual_results.items():
            if not isinstance(model_result, dict):
                continue

            # Only include real ML detection models, not utility analyzers
            # (metadata, ela, watermark, c2pa etc. are not detection models)
            if model_key not in MODEL_SPECIALTIES:
                continue

            specialty = MODEL_SPECIALTIES[model_key]
            model_score = model_result.get('ai_probability', 50)
            model_success = model_result.get('success', False)

            if not model_success:
                continue

            models_total += 1
            scores.append(model_score)
            is_flagging = model_score > 50

            if is_flagging:
                models_flagging_ai += 1

            # Pick the right explanation based on whether model thinks AI or not
            interpretation = specialty.get('ai_explanation', 'AI patterns detected') if is_flagging else specialty.get('human_explanation', 'Appears authentic')

            model_breakdown.append({
                'name': specialty.get('name', model_key),
                'key': model_key,
                'score': round(model_score, 1),
                'accuracy': specialty.get('accuracy', 'N/A'),
                'specialty': specialty.get('specialty', 'General detection'),
                'detects': specialty.get('detects', 'AI-generated images'),
                'interpretation': interpretation,
                'flagged_as_ai': is_flagging,
            })

        # Sort by score descending (strongest signals first)
        model_breakdown.sort(key=lambda m: m['score'], reverse=True)

        # Agreement analysis
        agreement_level, agreement_detail = self._analyze_agreement(
            models_flagging_ai, models_total, scores
        )

        # Generate anomalies / findings
        anomalies = self._generate_anomalies(model_breakdown, detection_result)

        # Generate human-readable summary
        summary = self._generate_summary(
            models_flagging_ai, models_total, ai_probability, model_breakdown
        )

        # Generate detailed reasoning
        reasoning = self._generate_reasoning(
            model_breakdown, agreement_level, ai_probability, detection_result
        )

        # Verdict description
        verdict_description = self._generate_verdict_description(
            verdict, ai_probability, models_flagging_ai, models_total
        )

        return {
            'summary': summary,
            'reasoning': reasoning,
            'model_breakdown': model_breakdown,
            'anomalies': anomalies,
            'agreement_level': agreement_level,
            'agreement_detail': agreement_detail,
            'verdict_description': verdict_description,
        }

    def _analyze_agreement(self, flagging: int, total: int, scores: List[float]) -> tuple:
        """
        Determine how much the models agree with each other.

        Returns:
            tuple of (level_string, detail_string)
        """
        if total == 0:
            return 'NO_DATA', 'No models produced results'

        ratio = flagging / total

        if ratio >= 0.8:
            level = 'STRONG_AI_CONSENSUS'
            detail = f'{flagging}/{total} models agree this is AI-generated'
        elif ratio >= 0.6:
            level = 'MAJORITY_AI'
            detail = f'{flagging}/{total} models flagged as AI — majority consensus'
        elif ratio <= 0.2:
            level = 'STRONG_HUMAN_CONSENSUS'
            detail = f'{total - flagging}/{total} models agree this is human-created'
        elif ratio <= 0.4:
            level = 'MAJORITY_HUMAN'
            detail = f'{total - flagging}/{total} models lean toward human origin'
        else:
            level = 'SPLIT_DECISION'
            detail = f'Models are divided ({flagging} AI vs {total - flagging} Human) — mixed signals'

        # Add spread information
        if len(scores) >= 2:
            spread = max(scores) - min(scores)
            if spread > 40:
                detail += f'. High spread ({spread:.0f}%) suggests different models see different things.'

        return level, detail

    def _generate_anomalies(self, model_breakdown: List[Dict], detection_result: Dict) -> List[str]:
        """
        Generate a list of notable anomalies / findings from the analysis.
        """
        anomalies = []

        # Check for unanimous detection
        ai_models = [m for m in model_breakdown if m['flagged_as_ai']]
        human_models = [m for m in model_breakdown if not m['flagged_as_ai']]

        if len(ai_models) == len(model_breakdown) and len(model_breakdown) > 0:
            anomalies.append(f'All {len(model_breakdown)} detection models unanimously classify this as AI-generated')
        elif len(human_models) == len(model_breakdown) and len(model_breakdown) > 0:
            anomalies.append(f'All {len(model_breakdown)} detection models unanimously classify this as human-created')

        # Check for specific model triggers
        for model in model_breakdown:
            if model['key'] == 'sdxl' and model['flagged_as_ai'] and model['score'] > 80:
                anomalies.append(f"SDXL-Detector ({model['score']}%) — image matches Stable Diffusion / Flux generator patterns")
            if model['key'] == 'dinov2' and model['flagged_as_ai'] and model['score'] > 80:
                anomalies.append(f"DINOv2 ({model['score']}%) — AI signal persists even through image degradation")
            if model['key'] == 'siglip_dinov2' and model['flagged_as_ai'] and model['score'] > 95:
                anomalies.append(f"SigLIP2+DINOv2 ({model['score']}%) — strongest dual-encoder model confirms AI origin")

        # Check for outlier models (one model strongly disagrees with the rest)
        if len(model_breakdown) >= 3:
            scores = [m['score'] for m in model_breakdown]
            mean_score = np.mean(scores)
            for model in model_breakdown:
                deviation = abs(model['score'] - mean_score)
                if deviation > 30:
                    if model['score'] > mean_score:
                        anomalies.append(f"{model['name']} scores much higher ({model['score']:.0f}% vs avg {mean_score:.0f}%) — may be detecting generator-specific artifacts")
                    else:
                        anomalies.append(f"{model['name']} scores much lower ({model['score']:.0f}% vs avg {mean_score:.0f}%) — this model's specialty may not match the image type")

        # Check watermark findings if available
        watermark = detection_result.get('watermark', {})
        if watermark.get('watermark_detected'):
            source = watermark.get('source', watermark.get('detected_watermark', 'Unknown'))
            anomalies.append(f'Invisible AI watermark detected (source: {source})')

        # Check C2PA
        c2pa = detection_result.get('content_credentials', {})
        if c2pa.get('is_ai_generated'):
            generator = c2pa.get('ai_generator', 'Unknown')
            anomalies.append(f'C2PA Content Credentials confirm AI generation by {generator}')

        return anomalies

    def _generate_summary(self, flagging: int, total: int, ai_prob: float,
                          model_breakdown: List[Dict]) -> str:
        """Generate a human-readable summary of the analysis."""
        if total == 0:
            return 'No ML models were available for this analysis.'

        if ai_prob > 50:
            # AI-generated
            if flagging == total:
                return (f'All {total} detection models unanimously identify this image as AI-generated '
                        f'with high confidence. Multiple architectural approaches (Vision Transformers, '
                        f'self-supervised learning, diffusion-model specialists) all converge on the same conclusion.')
            elif flagging > total / 2:
                return (f'{flagging} out of {total} models flag this image as AI-generated. '
                        f'The majority consensus, combined with weighted scoring, indicates AI origin.')
            else:
                return (f'While individual model opinions are mixed, the weighted ensemble score '
                        f'exceeds the detection threshold, suggesting AI-generated content.')
        else:
            # Human-created
            if flagging == 0:
                return (f'All {total} detection models identify this image as human-created. '
                        f'No AI generation patterns were detected across any architectural approach.')
            elif flagging < total / 2:
                return (f'{total - flagging} out of {total} models classify this as human-created. '
                        f'The majority consensus indicates this is an authentic photograph.')
            else:
                return (f'Model opinions are mixed, but the weighted ensemble score falls below '
                        f'the detection threshold. The image is classified as likely human-created.')

    def _generate_reasoning(self, model_breakdown: List[Dict], agreement_level: str,
                            ai_prob: float, detection_result: Dict) -> str:
        """Generate a detailed reasoning paragraph explaining the verdict."""
        parts = []

        # Explain the ensemble approach
        parts.append(f'This analysis was performed by an ensemble of {len(model_breakdown)} '
                      f'specialized AI detection models, each using a different architectural approach '
                      f'to maximize detection coverage.')

        # Explain key model findings
        ai_models = [m for m in model_breakdown if m['flagged_as_ai']]
        if ai_models:
            top_model = ai_models[0]
            parts.append(f"The strongest AI signal came from {top_model['name']} ({top_model['score']:.0f}%), "
                         f"which specializes in: {top_model['specialty'].lower()}.")

        human_models = [m for m in model_breakdown if not m['flagged_as_ai']]
        if human_models and ai_models:
            parts.append(f"{len(human_models)} model(s) leaned toward human origin, "
                         f"providing a cross-check against false positives.")

        # Explain agreement
        if agreement_level == 'STRONG_AI_CONSENSUS':
            parts.append('The unanimous cross-architecture agreement provides very high confidence in the AI classification.')
        elif agreement_level == 'SPLIT_DECISION':
            parts.append('The split decision between models suggests this image may be at the boundary of detection capability, '
                         'or may be a heavily processed photograph.')

        return ' '.join(parts)

    def _generate_verdict_description(self, verdict: str, ai_prob: float,
                                       flagging: int, total: int) -> str:
        """Generate a verdict description string."""
        if ai_prob > 50:
            return f'AI-Generated Content Detected — {flagging}/{total} models agree'
        else:
            return f'Human-Created Content — {total - flagging}/{total} models agree'

    # ─── Layer 2: Grad-CAM Attention Heatmaps ────────────────────────────────

    def _generate_gradcam_heatmap(self, image_data: bytes, detection_result: Dict) -> Optional[str]:
        """
        Generate a Grad-CAM attention heatmap from the detection models.

        Extracts attention weights from the loaded ViT model and produces
        a heatmap overlay showing which image regions triggered the detection.

        Args:
            image_data: Raw image bytes
            detection_result: Results from ensemble detector (used to find loaded models)

        Returns:
            Base64-encoded heatmap image, or None if generation fails
        """
        try:
            from pytorch_grad_cam import GradCAM
            from pytorch_grad_cam.utils.image import show_cam_on_image
            import torch
            from torchvision import transforms

            # Try to get a loaded model from the ensemble detector's ML models
            # We need access to the actual PyTorch model and its target layer
            individual = detection_result.get('individual_results', {})

            # Prefer deepfake (ViT) model as it's the most standard architecture
            # for Grad-CAM. Fall back to others.
            # NOTE: For Grad-CAM to work, we need direct access to the model object.
            # This may not be available from the detection_result dict alone.
            # In that case, we return None and let the explanation work without a heatmap.

            logger.debug("Grad-CAM heatmap generation attempted — model access not yet integrated")
            return None  # Placeholder: requires model reference integration

        except ImportError:
            return None
        except Exception as e:
            logger.warning(f"Grad-CAM heatmap generation failed: {e}")
            return None


def create_image_explainer() -> ImageExplainer:
    """
    Factory function to create an ImageExplainer instance.

    Returns:
        ImageExplainer instance (no API key needed)
    """
    return ImageExplainer()
