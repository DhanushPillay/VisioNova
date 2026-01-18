import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AIContentDetector:
    """
    Detector class for identifying AI-generated text using a local DistilBERT model.
    """
    
    def __init__(self, model_path=None):
        if model_path is None:
            # Default to the current directory
            model_path = os.path.dirname(os.path.abspath(__file__))
        
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self._load_model()
    
    def _load_model(self):
        """Loads the tokenizer and model from the local path."""
        try:
            print(f"Loading AI detector model from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def predict(self, text):
        """
        Predict if the given text is AI-generated.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: Detection results including label and confidence scores.
        """
        if not text or not text.strip():
            return {"error": "Empty text provided"}
        
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Get the highest probability class
        prob_values = probabilities[0].tolist()
        label_id = torch.argmax(probabilities).item()
        
        # Mapping from config.json: 0 -> human, 1 -> ai_generated
        labels = {0: "human", 1: "ai_generated"}
        
        return {
            "prediction": labels.get(label_id, "unknown"),
            "confidence": round(prob_values[label_id] * 100, 2),
            "scores": {
                "human": round(prob_values[0] * 100, 2),
                "ai_generated": round(prob_values[1] * 100, 2)
            }
        }

if __name__ == "__main__":
    # Test the detector
    detector = AIContentDetector()
    sample_text = "This is a sample human-written sentence for testing."
    result = detector.predict(sample_text)
    print(f"Test Result: {result}")
