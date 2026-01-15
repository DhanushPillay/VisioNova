"""
Configuration for the Fact Check module.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
GOOGLE_SEARCH_RESULTS = 10  # Number of search results to fetch
REQUEST_TIMEOUT = 10  # Seconds to wait for HTTP requests

# Trusted fact-check domains (higher weight in scoring)
TRUSTED_FACTCHECK_DOMAINS = [
    'snopes.com',
    'politifact.com',
    'factcheck.org',
    'fullfact.org',
    'apnews.com',
    'reuters.com',
    'bbc.com',
    'afp.com',
]

# Trusted news/reference domains
TRUSTED_DOMAINS = [
    'wikipedia.org',
    'britannica.com',
    'nytimes.com',
    'washingtonpost.com',
    'theguardian.com',
    'bbc.com',
    'reuters.com',
    'apnews.com',
    'nasa.gov',
    'who.int',
    'cdc.gov',
    'nih.gov',
]

# User agent for web requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Verdict types
class Verdict:
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIALLY_TRUE = "PARTIALLY TRUE"
    MISLEADING = "MISLEADING"
    UNVERIFIABLE = "UNVERIFIABLE"
