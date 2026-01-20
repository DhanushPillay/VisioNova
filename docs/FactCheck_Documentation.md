# Fact Check Module

## What It Does

The Fact Check module verifies whether claims are true or false by:
1. Extracting text from web pages
2. Understanding when events happened (past vs. present)
3. Checking if sources are trustworthy

---

## Components

### 1. Content Extractor

**File:** `content_extractor.py`

Fetches and cleans web page content.

**How it works:**
- Downloads a web page from a URL
- Removes irrelevant parts (ads, menus, scripts)
- Extracts the main article text
- Identifies key claims that can be fact-checked

**Example:**
```python
from fact_check.content_extractor import ContentExtractor

extractor = ContentExtractor()
result = extractor.extract_from_url("https://example.com/news-article")

print(result['title'])    # Article title
print(result['content'])  # Main text
print(result['claims'])   # List of verifiable statements
```

---

### 2. Temporal Analyzer

**File:** `temporal_analyzer.py`

Detects dates and time periods in text.

**Why this matters:**
- A claim about "1969" needs historical sources
- A claim about "today" needs recent news

**How it works:**
- Finds years (e.g., 1969, 2024) and full dates (e.g., January 15, 2020)
- Categorizes as "historical" or "recent"
- Guides search APIs to look in the right time period

**Example:**
```python
from fact_check.temporal_analyzer import TemporalAnalyzer

analyzer = TemporalAnalyzer()
result = analyzer.extract_temporal_context("The moon landing happened in 1969")

print(result['search_year_from'])  # 1969
print(result['is_historical'])     # True
print(result['time_period'])       # 'historical'
```

---

### 3. Credibility Manager

**File:** `credibility_manager.py`

Rates how trustworthy a website is.

**How it works:**
- Looks up the domain in a database of 70+ rated sources
- Returns a trust score (0-100)
- Identifies if it's a fact-checking site or known unreliable source

**Trust Levels:**
| Score | Level |
|-------|-------|
| 85-100 | High (Reuters, AP, Snopes) |
| 70-84 | Medium-High |
| 50-69 | Medium |
| 30-49 | Low |
| 0-29 | Unreliable |

**Example:**
```python
from fact_check.credibility_manager import CredibilityManager

manager = CredibilityManager()

print(manager.get_trust_score("reuters.com"))  # 95
print(manager.get_trust_score("snopes.com"))   # 95
print(manager.is_factcheck_site("snopes.com")) # True
```

---

## How It All Works Together

```
User Input (URL or Claim)
         |
         v
+-------------------+
| Content Extractor |  --> Extracts text & claims
+-------------------+
         |
         v
+-------------------+
| Temporal Analyzer |  --> Determines time context
+-------------------+
         |
         v
+---------------------+
| Credibility Manager |  --> Rates source trust
+---------------------+
         |
         v
    Final Verdict
```
