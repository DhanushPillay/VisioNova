"""
VisioNova Error Level Analysis (ELA) Module
Detects image manipulation by analyzing JPEG compression artifacts.

ELA works by re-compressing an image at a known quality level and comparing
the error levels. Manipulated regions show different compression characteristics.
"""

import io
import base64
import logging
from typing import Optional, Tuple
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ELAAnalyzer:
    """
    Error Level Analysis (ELA) for image manipulation detection.
    
    ELA highlights regions with different compression levels, which can
    indicate:
    - Image splicing (regions copied from other images)
    - AI-generated content inserted into real photos
    - Areas that have been edited or retouched
    """
    
    def __init__(self, quality: int = 90, scale: int = 15):
        """
        Initialize ELA analyzer.
        
        Args:
            quality: JPEG quality for re-compression (default 90)
            scale: Amplification factor for error visualization (default 15)
        """
        self.quality = quality
        self.scale = scale
    
    def analyze(self, image_data: bytes) -> dict:
        """
        Perform Error Level Analysis on an image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            dict with ELA results including heatmap
        """
        try:
            # Load original image
            original = Image.open(io.BytesIO(image_data))
            if original.mode != 'RGB':
                original = original.convert('RGB')
            
            # Generate ELA
            ela_image, error_stats = self._compute_ela(original)
            
            # Analyze the ELA result
            analysis = self._analyze_ela(ela_image, error_stats)
            
            # Generate visualization
            ela_base64 = self._image_to_base64(ela_image)
            
            return {
                'success': True,
                'ela_image': ela_base64,
                'error_stats': error_stats,
                'analysis': analysis,
                'manipulation_likelihood': analysis['manipulation_score'],
                'suspicious_regions': analysis['suspicious_regions']
            }
            
        except Exception as e:
            logger.error(f"ELA analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'manipulation_likelihood': 0
            }
    
    def _compute_ela(self, image: Image.Image) -> Tuple[Image.Image, dict]:
        """
        Compute Error Level Analysis.
        
        Re-compresses the image and calculates the difference from original.
        """
        # Re-compress at specified quality
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=self.quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)
        
        # Convert to numpy arrays
        original_arr = np.array(image, dtype=np.float32)
        recompressed_arr = np.array(recompressed, dtype=np.float32)
        
        # Calculate absolute difference
        diff = np.abs(original_arr - recompressed_arr)
        
        # Amplify the difference for visualization
        ela_arr = np.clip(diff * self.scale, 0, 255).astype(np.uint8)
        
        # Calculate statistics
        error_stats = {
            'mean_error': float(np.mean(diff)),
            'max_error': float(np.max(diff)),
            'std_error': float(np.std(diff)),
            'error_distribution': self._calculate_error_distribution(diff)
        }
        
        # Create ELA image
        ela_image = Image.fromarray(ela_arr)
        
        return ela_image, error_stats
    
    def _calculate_error_distribution(self, diff: np.ndarray) -> dict:
        """Calculate error level distribution across the image."""
        # Flatten and analyze
        flat_diff = diff.flatten()
        
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        distribution = {
            f'p{p}': float(np.percentile(flat_diff, p)) for p in percentiles
        }
        
        return distribution
    
    def _analyze_ela(self, ela_image: Image.Image, error_stats: dict) -> dict:
        """
        Analyze ELA result to detect manipulation.
        
        Looks for:
        - Inconsistent error levels across regions
        - High contrast areas in ELA (indicating manipulation)
        - Unusual patterns
        """
        ela_arr = np.array(ela_image, dtype=np.float32)
        
        # Convert to grayscale for analysis
        if len(ela_arr.shape) == 3:
            ela_gray = np.mean(ela_arr, axis=2)
        else:
            ela_gray = ela_arr
        
        # Analyze in patches
        patch_size = 64
        h, w = ela_gray.shape
        patch_stats = []
        
        for i in range(0, h - patch_size, patch_size // 2):
            for j in range(0, w - patch_size, patch_size // 2):
                patch = ela_gray[i:i+patch_size, j:j+patch_size]
                patch_stats.append({
                    'x': j,
                    'y': i,
                    'mean': float(np.mean(patch)),
                    'std': float(np.std(patch))
                })
        
        if not patch_stats:
            return {
                'manipulation_score': 0,
                'suspicious_regions': [],
                'analysis_notes': ['Image too small for detailed analysis']
            }
        
        # Calculate overall statistics
        means = [p['mean'] for p in patch_stats]
        overall_mean = np.mean(means)
        overall_std = np.std(means)
        
        # Find suspicious regions (outliers)
        threshold = overall_mean + 2 * overall_std
        suspicious_regions = []
        
        for patch in patch_stats:
            if patch['mean'] > threshold:
                suspicious_regions.append({
                    'x': patch['x'],
                    'y': patch['y'],
                    'width': patch_size,
                    'height': patch_size,
                    'severity': 'high' if patch['mean'] > threshold * 1.5 else 'medium'
                })
        
        # Calculate manipulation score (0-100)
        manipulation_score = self._calculate_manipulation_score(
            error_stats, overall_std, len(suspicious_regions), len(patch_stats)
        )
        
        # Generate analysis notes
        notes = []
        if manipulation_score > 70:
            notes.append('High likelihood of image manipulation detected')
        elif manipulation_score > 40:
            notes.append('Some inconsistencies detected in compression levels')
        else:
            notes.append('Error levels appear consistent across the image')
        
        if len(suspicious_regions) > 0:
            notes.append(f'Found {len(suspicious_regions)} suspicious region(s)')
        
        if error_stats['std_error'] > 20:
            notes.append('High variance in error levels')
        
        return {
            'manipulation_score': manipulation_score,
            'suspicious_regions': suspicious_regions[:10],  # Limit to top 10
            'analysis_notes': notes,
            'patch_variance': float(overall_std)
        }
    
    def _calculate_manipulation_score(self, error_stats: dict, patch_variance: float,
                                       num_suspicious: int, total_patches: int) -> float:
        """
        Calculate overall manipulation likelihood score.
        
        Returns:
            float: Score from 0 to 100
        """
        score = 0
        
        # Factor 1: Overall error standard deviation
        # Higher std indicates inconsistent compression = manipulation
        std_error = error_stats['std_error']
        if std_error > 30:
            score += 30
        elif std_error > 20:
            score += 20
        elif std_error > 10:
            score += 10
        
        # Factor 2: Patch-level variance
        # High variance between patches indicates splicing
        if patch_variance > 50:
            score += 30
        elif patch_variance > 30:
            score += 20
        elif patch_variance > 15:
            score += 10
        
        # Factor 3: Proportion of suspicious regions
        if total_patches > 0:
            suspicious_ratio = num_suspicious / total_patches
            score += min(40, suspicious_ratio * 200)
        
        return min(100, score)
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def generate_heatmap(self, image_data: bytes, colormap: str = 'hot') -> str:
        """
        Generate a colored heatmap visualization of ELA.
        
        Args:
            image_data: Raw image bytes
            colormap: Color scheme ('hot', 'jet', 'viridis')
            
        Returns:
            Base64 encoded heatmap image
        """
        try:
            # Load and compute ELA
            original = Image.open(io.BytesIO(image_data))
            if original.mode != 'RGB':
                original = original.convert('RGB')
            
            ela_image, _ = self._compute_ela(original)
            ela_arr = np.array(ela_image)
            
            # Convert to grayscale intensity
            if len(ela_arr.shape) == 3:
                intensity = np.mean(ela_arr, axis=2)
            else:
                intensity = ela_arr
            
            # Normalize to 0-255
            intensity = ((intensity - intensity.min()) / 
                        (intensity.max() - intensity.min() + 1e-6) * 255).astype(np.uint8)
            
            # Apply colormap
            if colormap == 'hot':
                heatmap = self._apply_hot_colormap(intensity)
            elif colormap == 'jet':
                heatmap = self._apply_jet_colormap(intensity)
            else:
                heatmap = self._apply_viridis_colormap(intensity)
            
            # Create overlay with original
            original_arr = np.array(original.resize(heatmap.shape[1::-1]))
            overlay = (original_arr * 0.5 + heatmap * 0.5).astype(np.uint8)
            
            overlay_image = Image.fromarray(overlay)
            return self._image_to_base64(overlay_image)
            
        except Exception as e:
            logger.error(f"Heatmap generation failed: {e}")
            return ""
    
    def _apply_hot_colormap(self, intensity: np.ndarray) -> np.ndarray:
        """Apply 'hot' colormap (black -> red -> yellow -> white)."""
        h, w = intensity.shape
        result = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Red channel
        result[:, :, 0] = np.clip(intensity * 3, 0, 255)
        # Green channel
        result[:, :, 1] = np.clip((intensity - 85) * 3, 0, 255)
        # Blue channel
        result[:, :, 2] = np.clip((intensity - 170) * 3, 0, 255)
        
        return result
    
    def _apply_jet_colormap(self, intensity: np.ndarray) -> np.ndarray:
        """Apply 'jet' colormap (blue -> cyan -> yellow -> red)."""
        h, w = intensity.shape
        result = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Simplified jet colormap
        normalized = intensity / 255.0
        
        result[:, :, 0] = np.clip(255 * (1.5 - np.abs(normalized - 0.75) * 4), 0, 255).astype(np.uint8)
        result[:, :, 1] = np.clip(255 * (1.5 - np.abs(normalized - 0.5) * 4), 0, 255).astype(np.uint8)
        result[:, :, 2] = np.clip(255 * (1.5 - np.abs(normalized - 0.25) * 4), 0, 255).astype(np.uint8)
        
        return result
    
    def _apply_viridis_colormap(self, intensity: np.ndarray) -> np.ndarray:
        """Apply 'viridis' colormap (purple -> blue -> green -> yellow)."""
        h, w = intensity.shape
        result = np.zeros((h, w, 3), dtype=np.uint8)
        
        normalized = intensity / 255.0
        
        # Simplified viridis approximation
        result[:, :, 0] = (68 + normalized * 187).astype(np.uint8)
        result[:, :, 1] = (1 + normalized * 180).astype(np.uint8)
        result[:, :, 2] = (84 + normalized * (253 - 84) * (1 - normalized)).astype(np.uint8)
        
        return result
