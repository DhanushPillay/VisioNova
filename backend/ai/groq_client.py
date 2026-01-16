"""
AI Analyzer - Uses Groq LLM for intelligent fact-check analysis.
Provides better verdict determination and explanations.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class AIAnalyzer:
    """Uses LLM to analyze claims and sources for fact-checking."""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        
        if not api_key:
            print("Warning: GROQ_API_KEY not found. AI analysis disabled.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
    
    def analyze_claim(self, claim: str, sources: list) -> dict:
        """
        Use AI to analyze a claim against found sources.
        
        Args:
            claim: The claim being fact-checked
            sources: List of source dictionaries with title, snippet, trust_level
            
        Returns:
            dict with verdict, confidence, and explanation
        """
        if not self.client:
            return self._fallback_analysis(sources)
        
        try:
            # Build context from sources
            source_context = self._build_source_context(sources)
            
            # Create prompt for analysis
            prompt = f"""You are a fact-checker. Analyze the following claim based on the provided sources.

CLAIM TO VERIFY:
"{claim}"

SOURCES FOUND:
{source_context}

Based on these sources, provide your analysis in the following JSON format:
{{
    "verdict": "TRUE" | "FALSE" | "PARTIALLY TRUE" | "MISLEADING" | "UNVERIFIABLE",
    "confidence": <number 0-100>,
    "explanation": "<2-3 sentence explanation of your verdict>",
    "key_finding": "<most important finding from sources>"
}}

Rules:
- If sources directly confirm the claim, verdict is TRUE
- If sources directly contradict the claim, verdict is FALSE  
- If claim has some truth but is exaggerated/missing context, verdict is PARTIALLY TRUE or MISLEADING
- If sources don't provide enough information, verdict is UNVERIFIABLE
- Confidence should reflect how certain you are (high trust sources = higher confidence)

Respond ONLY with valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert fact-checker. You analyze claims objectively and base verdicts only on provided evidence. Always respond in valid JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            import json
            
            # Handle potential markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            
            return {
                'verdict': result.get('verdict', 'UNVERIFIABLE'),
                'confidence': min(100, max(0, int(result.get('confidence', 50)))),
                'explanation': result.get('explanation', 'Analysis completed.'),
                'key_finding': result.get('key_finding', ''),
                'ai_analyzed': True
            }
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(sources)
    
    def _build_source_context(self, sources: list) -> str:
        """Build a text context from sources for the AI prompt."""
        if not sources:
            return "No sources found."
        
        context_parts = []
        for i, source in enumerate(sources[:8], 1):  # Limit to 8 sources
            trust = source.get('trust_level', 'unknown')
            is_factcheck = source.get('is_factcheck_site', False)
            
            source_type = "[FACT-CHECK SITE]" if is_factcheck else f"[{trust.upper()}]"
            
            context_parts.append(
                f"{i}. {source_type} {source.get('title', 'Untitled')}\n"
                f"   Domain: {source.get('domain', 'unknown')}\n"
                f"   Content: {source.get('snippet', '')[:250]}"
            )
        
        return "\n\n".join(context_parts)
    
    def _fallback_analysis(self, sources: list) -> dict:
        """Fallback when AI is unavailable - use simple heuristics."""
        factcheck_count = sum(1 for s in sources if s.get('is_factcheck_site'))
        high_trust = sum(1 for s in sources if s.get('trust_level') == 'high')
        
        if factcheck_count > 0:
            confidence = min(85, 60 + factcheck_count * 10)
            verdict = 'UNVERIFIABLE'  # Can't determine without AI
            explanation = f"Found {factcheck_count} fact-check sources. AI analysis unavailable."
        elif high_trust > 0:
            confidence = min(70, 40 + high_trust * 10)
            verdict = 'UNVERIFIABLE'
            explanation = f"Found {high_trust} trusted sources. AI analysis unavailable."
        else:
            confidence = 30
            verdict = 'UNVERIFIABLE'
            explanation = "Could not find trusted sources. AI analysis unavailable."
        
        return {
            'verdict': verdict,
            'confidence': confidence,
            'explanation': explanation,
            'key_finding': '',
            'ai_analyzed': False
        }


# Quick test
if __name__ == '__main__':
    analyzer = AIAnalyzer()
    
    test_claim = "The moon landing happened in 1969"
    test_sources = [
        {
            'title': 'Apollo 11 - Wikipedia',
            'domain': 'wikipedia.org',
            'snippet': 'Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969.',
            'trust_level': 'medium-high',
            'is_factcheck_site': False
        },
        {
            'title': 'NASA Apollo 11 Mission Overview',
            'domain': 'nasa.gov',
            'snippet': 'Apollo 11 was the first mission to land humans on the Moon. On July 20, 1969, American astronauts Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon.',
            'trust_level': 'high',
            'is_factcheck_site': False
        }
    ]
    
    result = analyzer.analyze_claim(test_claim, test_sources)
    
    print(f"Claim: {test_claim}")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Explanation: {result['explanation']}")
    print(f"AI Analyzed: {result['ai_analyzed']}")
