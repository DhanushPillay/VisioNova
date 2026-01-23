"""
ML-based AI text prediction
Uses pre-trained Random Forest model with TF-IDF features
"""
import os
import joblib
import numpy as np
from scipy.sparse import hstack
from utils_ml import preprocess, extra_features


class MLTextPredictor:
    """ML-based predictor for AI-generated text detection"""
    
    def __init__(self, model_path=None, tfidf_path=None):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: Path to trained model (default: 'models/ai_text_model.pkl')
            tfidf_path: Path to TF-IDF vectorizer (default: 'models/tfidf_vectorizer.pkl')
        """
        # Default paths
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'ai_text_model.pkl')
        if tfidf_path is None:
            tfidf_path = os.path.join(os.path.dirname(__file__), 'models', 'tfidf_vectorizer.pkl')
        
        self.model_path = model_path
        self.tfidf_path = tfidf_path
        self.model = None
        self.tfidf = None
        
        self._load_model()
    
    def _load_model(self):
        """Load model and vectorizer from disk"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        if not os.path.exists(self.tfidf_path):
            raise FileNotFoundError(f"TF-IDF vectorizer not found: {self.tfidf_path}")
        
        print(f"[INFO] Loading model from {self.model_path}...")
        self.model = joblib.load(self.model_path)
        
        print(f"[INFO] Loading TF-IDF vectorizer from {self.tfidf_path}...")
        self.tfidf = joblib.load(self.tfidf_path)
        
        print("[INFO] ML model loaded successfully")
    
    def predict(self, text):
        """
        Predict if text is AI-generated or human-written
        
        Args:
            text: Input text to analyze
        
        Returns:
            dict: {
                'prediction': 'ai_generated' or 'human',
                'confidence': float (0-100),
                'human_prob': float (0-1),
                'ai_prob': float (0-1),
                'text_length': int,
                'unique_ratio': float
            }
        """
        if self.model is None or self.tfidf is None:
            raise RuntimeError("Model not loaded")
        
        # Validate text length
        words = text.split()
        if len(words) < 2:
            return {
                'prediction': 'human',
                'confidence': 0.0,
                'human_prob': 0.5,
                'ai_prob': 0.5,
                'warning': 'Text too short for reliable analysis (min 2 words)',
                'text_length': len(words),
                'unique_ratio': 0.0
            }
        
        # Preprocess text
        preprocessed = preprocess(text)
        
        # Create features
        tfidf_vec = self.tfidf.transform([preprocessed])
        extra = np.array([extra_features(preprocessed)])
        
        # Combine features
        final_vec = hstack([tfidf_vec, extra])
        
        # Get prediction
        probabilities = self.model.predict_proba(final_vec)[0]
        prediction = self.model.predict(final_vec)[0]
        
        # Parse results
        human_prob = probabilities[0]
        ai_prob = probabilities[1]
        
        pred_label = 'ai_generated' if prediction == 1 else 'human'
        confidence = max(human_prob, ai_prob) * 100
        
        return {
            'prediction': pred_label,
            'confidence': round(confidence, 2),
            'human_prob': round(human_prob, 4),
            'ai_prob': round(ai_prob, 4),
            'text_length': len(words),
            'unique_ratio': round(len(set(words)) / len(words), 4),
            'model': 'Random Forest with TF-IDF'
        }
    
    def predict_batch(self, texts):
        """
        Predict multiple texts at once
        
        Args:
            texts: List of text strings
        
        Returns:
            list: List of prediction dictionaries
        """
        return [self.predict(text) for text in texts]


def test_predictor():
    """Test the ML predictor with sample texts"""
    try:
        predictor = MLTextPredictor()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("[INFO] Train a model first using: python train_ml.py dataset.csv")
        return
    
    test_texts = [
        "hey whats up buddy",
        "In conclusion, the multifaceted implications of this phenomenon warrant comprehensive examination.",
        "The implementation of advanced algorithms necessitates careful consideration of computational efficiency.",
        "just checking if this works",
        "As an artificial intelligence language model, I must emphasize the utmost importance of thorough analysis.",
    ]
    
    print("\n" + "="*70)
    print("ML TEXT PREDICTOR - TEST RESULTS")
    print("="*70 + "\n")
    
    for i, text in enumerate(test_texts, 1):
        result = predictor.predict(text)
        
        print(f"Test {i}: {text[:60]}{'...' if len(text) > 60 else ''}")
        print(f"  Prediction: {result['prediction'].upper()}")
        print(f"  Confidence: {result['confidence']:.2f}%")
        print(f"  Probabilities: Human={result['human_prob']:.4f}, AI={result['ai_prob']:.4f}")
        print(f"  Text Length: {result['text_length']} words")
        print()


if __name__ == '__main__':
    test_predictor()
