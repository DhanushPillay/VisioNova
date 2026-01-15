"""
Content Extractor
Extracts main text content from URLs (articles, web pages).
"""
import requests
from bs4 import BeautifulSoup
from .config import USER_AGENT, REQUEST_TIMEOUT


class ContentExtractor:
    """Extracts text content from web pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def extract_from_url(self, url: str) -> dict:
        """
        Extract main content from a URL.
        
        Args:
            url: Web page URL to extract content from
            
        Returns:
            dict with 'success', 'title', 'content', 'error'
        """
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract claims/key statements from content
            claims = self._extract_key_claims(content)
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'content': content[:2000],  # Limit content length
                'claims': claims,
                'error': None
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'url': url,
                'title': None,
                'content': None,
                'claims': [],
                'error': str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try regular title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page."""
        # Remove script, style, nav, footer elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                            'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Try to find article content
        article = soup.find('article')
        if article:
            return self._clean_text(article.get_text())
        
        # Try main content area
        main = soup.find('main')
        if main:
            return self._clean_text(main.get_text())
        
        # Try common content class names
        for class_name in ['content', 'article-body', 'post-content', 
                          'entry-content', 'story-body']:
            content_div = soup.find(class_=class_name)
            if content_div:
                return self._clean_text(content_div.get_text())
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        lines = text.split('\n')
        cleaned_lines = [' '.join(line.split()) for line in lines]
        cleaned_lines = [line for line in cleaned_lines if len(line) > 20]
        return '\n'.join(cleaned_lines)
    
    def _extract_key_claims(self, content: str) -> list:
        """Extract key claims/statements from content for verification."""
        if not content:
            return []
        
        # Split into sentences
        sentences = content.replace('\n', ' ').split('.')
        
        # Filter to sentences that look like verifiable claims
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences that are statement-like (not too short/long)
            if 30 < len(sentence) < 300:
                # Avoid questions, exclamations, and conversational text
                if not sentence.endswith('?') and not sentence.endswith('!'):
                    claims.append(sentence)
        
        return claims[:5]  # Return top 5 claims


# Quick test
if __name__ == '__main__':
    extractor = ContentExtractor()
    
    test_url = "https://en.wikipedia.org/wiki/Moon_landing"
    result = extractor.extract_from_url(test_url)
    
    if result['success']:
        print(f"Title: {result['title']}")
        print(f"\nContent preview: {result['content'][:500]}...")
        print(f"\nKey claims: {result['claims']}")
    else:
        print(f"Error: {result['error']}")
