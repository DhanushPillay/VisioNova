# ML Model Integration Guide

## Overview
This document explains how to train and use the ML-based AI text detection model.

## Components

### 1. `utils_ml.py`
Utility functions for text preprocessing and feature extraction:
- `preprocess(text)` - Lowercase, remove non-alpha chars, clean whitespace
- `extra_features(text)` - Extract text length and vocabulary diversity ratio
- `get_feature_names()` - Get feature names for debugging

### 2. `train_ml.py`
Training script for Random Forest classifier:
- Requires CSV dataset with 'text' and 'label' columns
- Label: 0 = human, 1 = AI-generated
- Creates TF-IDF features (3000 features, 1-2 grams) + extra features
- Outputs trained model and vectorizer to `models/` directory

### 3. `predict_ml.py`
Inference module with `MLTextPredictor` class:
- Loads pre-trained model and vectorizer
- Provides `predict(text)` method
- Returns prediction, confidence, probabilities, and features

## Setup & Training

### 1. Prepare Dataset
Create a CSV file with columns:
```
text,label
"Sample human text",0
"Sample AI-generated text",1
...
```

### 2. Install Dependencies
```bash
pip install pandas numpy scikit-learn scipy joblib
```

### 3. Train Model
```bash
cd backend/text_detector

# Train with default settings (saves to models/)
python train_ml.py dataset.csv

# Specify custom output directory
python train_ml.py dataset.csv custom_models/
```

### 4. Test Model
```bash
python predict_ml.py
```

## Usage in Application

### Direct Usage
```python
from predict_ml import MLTextPredictor

# Load model
predictor = MLTextPredictor()

# Make prediction
result = predictor.predict("Your text here")
print(result['prediction'])  # 'human' or 'ai_generated'
print(result['confidence'])  # 0-100
```

### Integration with Detector
The existing `detector.py` can be modified to use the ML model:
```python
from text_detector.predict_ml import MLTextPredictor

detector = AIContentDetector(use_ml_model=True)  # Uses ML model instead of statistical
```

## Model Performance
After training, you'll see metrics like:
- Train Accuracy
- Test Accuracy  
- Precision
- Recall
- F1-Score

## Files Structure
```
backend/text_detector/
├── utils_ml.py              # Utility functions
├── train_ml.py              # Training script
├── predict_ml.py            # Inference module
├── ML_INTEGRATION.md         # This file
└── models/                  # (Auto-created after training)
    ├── ai_text_model.pkl
    └── tfidf_vectorizer.pkl
```

## Dataset Format Example
```csv
text,label
"I love this movie!",0
"The cinematography was exceptional and the narrative arc demonstrated remarkable sophistication.",1
"hey what's up",0
"The multifaceted implications warrant comprehensive analysis.",1
```

## Notes
- Minimum text length for prediction: 2 words
- Model works best with texts > 20 words
- Training typically takes 1-5 minutes depending on dataset size
- Recommend 1000+ samples for good model performance
