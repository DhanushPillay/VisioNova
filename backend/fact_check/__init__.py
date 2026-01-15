"""
VisioNova Fact Check Module
Verify claims by searching multiple websites and analyzing results.
"""

from .fact_checker import FactChecker
from .input_classifier import InputClassifier
from .web_searcher import WebSearcher
from .content_extractor import ContentExtractor

__all__ = ['FactChecker', 'InputClassifier', 'WebSearcher', 'ContentExtractor']
__version__ = '1.0.0'
