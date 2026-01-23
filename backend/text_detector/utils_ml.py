"""
ML utilities for text preprocessing and feature extraction
"""
import re
import numpy as np


def preprocess(text):
    """
    Preprocess text for ML model:
    - Convert to lowercase
    - Remove non-alphabetic characters (keep spaces)
    - Remove extra whitespace
    """
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extra_features(text):
    """
    Extract additional features beyond TF-IDF:
    - Length: number of words
    - Unique ratio: proportion of unique words (vocabulary diversity)
    
    Returns:
        list: [length, unique_ratio]
    """
    words = text.split()
    length = len(words)
    unique_ratio = len(set(words)) / (length + 1)  # +1 to avoid division by zero
    return [length, unique_ratio]


def get_feature_names():
    """Get names of extra features for debugging/logging"""
    return ['text_length', 'unique_word_ratio']
