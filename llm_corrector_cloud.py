"""
Enhanced LLM Text Corrector - Streamlit Cloud Compatible
Works with or without Fireworks API key
Uses advanced local correction as fallback
"""

import requests
import os
import time
from typing import Optional, Dict
import re
from functools import lru_cache

# Try to import spell checker, fall back if not available
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

# Try to import language tool, fall back if not available
try:
    from language_tool_python import LanguageTool
    HAS_LANGUAGE_TOOL = True
except ImportError:
    HAS_LANGUAGE_TOOL = False


class AdvancedLocalCorrector:
    """
    Advanced local text correction using multiple strategies
    No external dependencies required (except optional ones)
    """
    
    def __init__(self):
        """Initialize local corrector"""
        self.common_ocr_errors = {
            # Common OCR character mistakes
            r'\b0\b': 'O',
            r'\b1\b': 'l',
            r'\bl\b': 'I',
            r'\brn\b': 'm',
            r'\bm\b': 'n',
            r'\bO\b': '0',
            r'\bI\b': 'l',
            r'\|': 'I',
            r'\.\.\.': '...',
        }
        
        self.common_typos = {
            'teh': 'the',
            'adn': 'and',
            'hte': 'the',
            'thier': 'their',
            'recieve': 'receive',
            'occured': 'occurred',
            'wich': 'which',
            'woudl': 'would',
            'coulde': 'could',
            'shoudl': 'should',
            'dont': 'don\'t',
            'doesnt': 'doesn\'t',
            'cant': 'can\'t',
            'wont': 'won\'t',
            'isnt': 'isn\'t',
            'arent': 'aren\'t',
            'wasnt': 'wasn\'t',
            'werent': 'weren\'t',
            'havent': 'haven\'t',
            'hasnt': 'hasn\'t',
            'hadnt': 'hadn\'t',
            'shouldnt': 'shouldn\'t',
            'wouldnt': 'wouldn\'t',
            'couldnt': 'couldn\'t',
            'mustnt': 'mustn\'t',
            'maching': 'machine',
            'learnlng': 'learning',
            'artifical': 'artificial',
            'intellgence': 'intelligence',
            'lntelligence': 'intelligence',
            'systmes': 'systems',
            'imprve': 'improve',
            'exprience': 'experience',
            'powrful': 'powerful',
            'comuting': 'computing',
            'algortihm': 'algorithm',
            'datbase': 'database',
        }
        
        # Initialize optional libraries
        self.textblob_available = HAS_TEXTBLOB
        self.language_tool = None
        
        if HAS_LANGUAGE_TOOL:
            try:
                self.language_tool = LanguageTool('en-US')
            except Exception as e:
                print(f"Warning: LanguageTool initialization failed: {e}")
    
    def correct(self, text: str) -> str:
        """
        Apply multiple correction strategies
        """
        if not text or len(text.strip()) == 0:
            return text
        
        # Step 1: Fix OCR-specific errors
        corrected = self._fix_ocr_errors(text)
        
        # Step 2: Fix common typos
        corrected = self._fix_typos(corrected)
        
        # Step 3: Fix spacing issues
        corrected = self._fix_spacing(corrected)
        
        # Step 4: Use TextBlob if available
        if self.textblob_available:
            corrected = self._textblob_correction(corrected)
        
        # Step 5: Use LanguageTool if available
        if self.language_tool:
            corrected = self._language_tool_correction(corrected)
        
        # Step 6: Capitalize sentences
        corrected = self._capitalize_sentences(corrected)
        
        # Step 7: Fix punctuation
        corrected = self._fix_punctuation(corrected)
        
        return corrected.strip()
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR recognition errors"""
        corrected = text
        for pattern, replacement in self.common_ocr_errors.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        return corrected
    
    def _fix_typos(self, text: str) -> str:
        """Fix common typos and misspellings"""
        corrected = text
        for typo, correction in self.common_typos.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(typo) + r'\b'
            corrected = re.sub(pattern, correction, corrected, flags=re.IGNORECASE)
        return corrected
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues"""
        # Multiple spaces to single space
        corrected = re.sub(r' +', ' ', text)
        
        # Fix space before punctuation
        corrected = re.sub(r' +([.,!?;:])', r'\1', corrected)
        
        # Fix space after opening quotes/brackets
        corrected = re.sub(r'([\(\[\{"\']) +', r'\1', corrected)
        
        # Fix space before closing quotes/brackets
        corrected = re.sub(r' +([\)\]\}"\'])', r'\1', corrected)
        
        return corrected
    
    def _textblob_correction(self, text: str) -> str:
        """Use TextBlob for spell correction"""
        try:
            blob = TextBlob(text)
            return str(blob.correct())
        except Exception as e:
            print(f"TextBlob correction error: {e}")
            return text
    
    def _language_tool_correction(self, text: str) -> str:
        """Use LanguageTool for grammar correction"""
        try:
            matches = self.language_tool.check(text)
            
            # Apply corrections in reverse order to maintain positions
            for match in reversed(matches):
                if match.replacements:
                    replacement = match.replacements[0]
                    text = (
                        text[:match.offset] +
                        replacement +
                        text[match.offset + len(match.matchedText):]
                    )
            
            return text
        except Exception as e:
            print(f"LanguageTool correction error: {e}")
            return text
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences"""
        # Split by sentence boundaries
        sentences = re.split(r'([.!?]+)', text)
        
        corrected = []
        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Actual sentence text
                if sentence and len(sentence.strip()) > 0:
                    # Capitalize first letter
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                corrected.append(sentence)
            else:  # Punctuation
                corrected.append(sentence)
        
        return ''.join(corrected)
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix basic punctuation issues"""
        # Add period at end if missing
        if text and text[-1] not in '.!?':
            text += '.'
        
        # Remove multiple punctuation marks
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        # Fix space after punctuation
        text = re.sub(r'([.!?])(?! )', r'\1 ', text)
        
        return text


class FireworksCorrector:
    """
    Corrects OCR text using Fireworks AI API
    Falls back to local correction if API fails or key not available
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Fireworks corrector
        
        Args:
            api_key: Fireworks API key (or set FIREWORKS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("FIREWORKS_API_KEY", "").strip()
        self.base_url = "https://api.fireworks.ai/inference/v1/chat/completions"
        self.model = "accounts/fireworks/models/deepseek-v4-pro"
        self.timeout = 20
        self.max_retries = 2
        
        # Initialize local corrector as fallback
        self.local_corrector = AdvancedLocalCorrector()
        
        self.system_prompt = """You are an expert OCR post-processing engine.
Correct OCR errors while maintaining original meaning.
Output ONLY the corrected text, no explanations."""
    
    def correct_text(self, text: str, language: str = "en", use_api: bool = True) -> Dict:
        """
        Correct OCR text
        
        Args:
            text: Text to correct
            language: Language code
            use_api: Whether to try API (if key available)
        
        Returns:
            Dict with corrected text and metadata
        """
        if not text or len(text.strip()) == 0:
            return {
                'status': 'error',
                'message': 'Empty text',
                'original': text,
                'corrected': text,
                'confidence': 0,
                'method': 'none'
            }
        
        # Try API if key available and use_api is True
        if use_api and self.api_key:
            result = self._try_api_correction(text, language)
            if result:
                return result
        
        # Fallback to local correction
        return self._local_correction(text)
    
    def _try_api_correction(self, text: str, language: str) -> Optional[Dict]:
        """
        Try to correct using Fireworks API
        Returns None if fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Correct this {language} text:\n\n{text}"}
                ],
                "temperature": 0.2,
                "max_tokens": min(len(text) * 2, 2048),
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    corrected = data["choices"][0]["message"]["content"].strip()
                    return {
                        'status': 'success',
                        'original': text,
                        'corrected': corrected,
                        'confidence': 0.95,
                        'method': 'api_fireworks',
                        'model': self.model
                    }
        
        except requests.exceptions.Timeout:
            print("API timeout - using local correction")
        except requests.exceptions.ConnectionError:
            print("API connection error - using local correction")
        except Exception as e:
            print(f"API error: {e} - using local correction")
        
        return None
    
    def _local_correction(self, text: str) -> Dict:
        """
        Fallback local correction
        """
        corrected = self.local_corrector.correct(text)
        
        return {
            'status': 'success',
            'original': text,
            'corrected': corrected,
            'confidence': 0.85,
            'method': 'local_advanced',
            'message': 'Using advanced local correction (no API)'
        }
    
    def correct_batch(self, texts: list, language: str = "en") -> list:
        """Correct multiple texts"""
        results = []
        for text in texts:
            result = self.correct_text(text, language)
            results.append(result)
        return results


# Example usage
if __name__ == "__main__":
    corrector = FireworksCorrector()
    
    test_cases = [
        "Maching Learnlng is powrful",
        "Artifical lntelligence is transforming industy",
        "The algoritm works very wel for complex problms",
    ]
    
    print("=" * 60)
    print("OCR Text Correction Examples")
    print("=" * 60)
    
    for test in test_cases:
        result = corrector.correct_text(test)
        print(f"\nOriginal:  {result['original']}")
        print(f"Corrected: {result['corrected']}")
        print(f"Method:    {result['method']}")
        print(f"Conf:      {result['confidence']:.0%}")
