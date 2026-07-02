"""
Lightweight Translation Engine - Streamlit Cloud Compatible
No heavy dependencies like ctranslate2
Uses simple dictionary-based translation as fallback
"""

from typing import List, Dict, Optional
import re

class SimpleTranslationEngine:
    """
    Lightweight translation engine using dictionary approach
    Perfect for Streamlit Cloud deployment
    No heavy dependencies required
    """
    
    def __init__(self):
        """Initialize translation engine"""
        print("Initializing Simple Translation Engine...")
        
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'ka': 'Kannada (ಕನ್ನಡ)',
            'mr': 'Marathi (मराठी)',
        }
        
        # Hindi translation dictionary
        self.english_to_hindi = {
            # Common words
            'the': 'द',
            'a': 'एक',
            'and': 'और',
            'is': 'है',
            'are': 'हैं',
            'was': 'था',
            'were': 'थे',
            'be': 'होना',
            'been': 'रहा है',
            'being': 'होना',
            
            # Common verbs
            'have': 'रखना',
            'has': 'है',
            'had': 'था',
            'do': 'करना',
            'does': 'करता है',
            'did': 'किया',
            'will': 'होगा',
            'would': 'होता',
            'could': 'सकता',
            'should': 'चाहिए',
            'may': 'सकता है',
            'might': 'हो सकता है',
            'must': 'जरूर',
            'can': 'सकता है',
            'make': 'बनाना',
            'made': 'बनाया',
            'go': 'जाना',
            'went': 'गया',
            'come': 'आना',
            'came': 'आया',
            'take': 'लेना',
            'took': 'लिया',
            'give': 'देना',
            'gave': 'दिया',
            'know': 'जानना',
            'knew': 'जानता था',
            
            # Common nouns
            'machine': 'मशीन',
            'learning': 'सीखना',
            'intelligence': 'बुद्धिमत्ता',
            'artificial': 'कृत्रिम',
            'system': 'प्रणाली',
            'data': 'डेटा',
            'computer': 'कंप्यूटर',
            'software': 'सॉफ्टवेयर',
            'hardware': 'हार्डवेयर',
            'network': 'नेटवर्क',
            'internet': 'इंटरनेट',
            'website': 'वेबसाइट',
            'application': 'एप्लिकेशन',
            'program': 'प्रोग्राम',
            'code': 'कोड',
            'algorithm': 'एल्गोरिदम',
            'database': 'डेटाबेस',
            'server': 'सर्वर',
            'client': 'क्लाइंट',
            'user': 'उपयोगकर्ता',
            'password': 'पासवर्ड',
            'security': 'सुरक्षा',
            'error': 'त्रुटि',
            'warning': 'चेतावनी',
            'message': 'संदेश',
            'information': 'जानकारी',
            'technology': 'तकनीक',
            'innovation': 'नवाचार',
            'development': 'विकास',
            'process': 'प्रक्रिया',
            'result': 'परिणाम',
            'success': 'सफलता',
            'failure': 'विफलता',
            'time': 'समय',
            'date': 'तारीख',
            'number': 'संख्या',
            'amount': 'राशि',
            'price': 'कीमत',
            'cost': 'लागत',
            'value': 'मूल्य',
            
            # Adjectives
            'good': 'अच्छा',
            'bad': 'बुरा',
            'big': 'बड़ा',
            'small': 'छोटा',
            'fast': 'तेज',
            'slow': 'धीमा',
            'new': 'नया',
            'old': 'पुराना',
            'high': 'ऊंचा',
            'low': 'कम',
            'easy': 'आसान',
            'difficult': 'मुश्किल',
            'simple': 'सरल',
            'complex': 'जटिल',
            'important': 'महत्वपूर्ण',
            'urgent': 'तुरंत',
            'special': 'विशेष',
            'normal': 'सामान्य',
            'different': 'अलग',
            'same': 'समान',
            'better': 'बेहतर',
            'worse': 'बदतर',
            'best': 'सर्वश्रेष्ठ',
            'worst': 'सबसे बुरा',
        }
        
        # Tamil translation dictionary (basic)
        self.english_to_tamil = {
            'machine': 'மशین',
            'learning': 'கற்றல்',
            'artificial': 'கృத्రिம',
            'intelligence': 'உணர்வு',
            'data': 'தரவு',
            'computer': 'கணினி',
            'software': 'மென்பொருள்',
            'network': 'வலையமைப்பு',
            'internet': 'இணையம்',
            'technology': 'தொழில்நுட்பம்',
            'system': 'முறைமை',
            'program': 'நிரல்',
            'code': 'குறியீடு',
            'error': 'பிழை',
            'success': 'வெற்றி',
            'good': 'நல்ல',
            'bad': 'கெட்ட',
            'time': 'நேரம்',
            'number': 'எண்',
            'and': 'மற்றும்',
            'the': 'தி',
            'is': 'ஆகும்',
        }
        
        # Telugu translation dictionary (basic)
        self.english_to_telugu = {
            'machine': 'యంత్రం',
            'learning': 'నేర్చుకోవడం',
            'artificial': 'కృత్రిమ',
            'intelligence': 'తెలివిత',
            'data': 'డేటా',
            'computer': 'కంప్యూటర్',
            'technology': 'సాంకేతికత',
            'system': 'వ్యవస్థ',
            'program': 'కార్యక్రమం',
            'good': 'మంచి',
            'bad': 'చెడు',
            'time': 'సమయం',
            'and': 'మరియు',
            'is': 'ఉంది',
        }
        
        # Kannada translation dictionary (basic)
        self.english_to_kannada = {
            'machine': 'ಯಂತ್ರ',
            'learning': 'ಕಲಿಕೆ',
            'artificial': 'ಕೃತ್ರಿಮ',
            'intelligence': 'ಬುದ್ಧಿಮತ್ತೆ',
            'data': 'ಡೇಟಾ',
            'computer': 'ಕಂಪ್ಯೂಟರ್',
            'technology': 'ತಂತ್ರಜ್ಞಾನ',
            'system': 'ವ್ಯವಸ್ಥೆ',
            'good': 'ಚೆನ್ನ',
            'bad': 'ಕೆಟ್ಟ',
            'time': 'ಸಮಯ',
            'and': 'ಮತ್ತು',
            'is': 'ಇದೆ',
        }
        
        # Marathi translation dictionary (basic)
        self.english_to_marathi = {
            'machine': 'मशीन',
            'learning': 'शिक्षण',
            'artificial': 'कृत्रिम',
            'intelligence': 'बुद्धिमत्ता',
            'data': 'डेटा',
            'computer': 'संगणक',
            'technology': 'तंत्रज्ञान',
            'system': 'व्यवस्था',
            'good': 'चांगला',
            'bad': 'वाईट',
            'time': 'वेळ',
            'and': 'आणि',
            'is': 'आहे',
        }
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'hi') -> str:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if source_lang == target_lang:
            return text
        
        if source_lang != 'en':
            # Only support English to other languages for now
            return f"[Translation from {source_lang} not supported - returning original]"
        
        # Select appropriate dictionary
        dictionaries = {
            'hi': self.english_to_hindi,
            'ta': self.english_to_tamil,
            'te': self.english_to_telugu,
            'ka': self.english_to_kannada,
            'mr': self.english_to_marathi,
        }
        
        dictionary = dictionaries.get(target_lang, {})
        
        if not dictionary:
            return f"[Language {target_lang} not supported]"
        
        return self._translate_with_dict(text, dictionary)
    
    def _translate_with_dict(self, text: str, dictionary: Dict[str, str]) -> str:
        """Translate using dictionary"""
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[.,!?;:\'"()-]', '', word)
            punctuation = re.findall(r'[.,!?;:\'"()-]', word)
            
            # Look up translation
            if clean_word in dictionary:
                translated = dictionary[clean_word]
            else:
                translated = word
            
            # Add punctuation back
            if punctuation:
                translated += ''.join(punctuation)
            
            translated_words.append(translated)
        
        return ' '.join(translated_words)
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', 
                       target_lang: str = 'hi') -> List[str]:
        """Translate multiple texts"""
        return [self.translate(text, source_lang, target_lang) for text in texts]
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text using character ranges
        
        Returns:
            Language code
        """
        if not text:
            return 'en'
        
        # Count character patterns
        hindi_chars = sum(1 for c in text if ord(c) >= 0x0900 and ord(c) <= 0x097F)
        tamil_chars = sum(1 for c in text if ord(c) >= 0x0B80 and ord(c) <= 0x0BFF)
        telugu_chars = sum(1 for c in text if ord(c) >= 0x0C00 and ord(c) <= 0x0C7F)
        kannada_chars = sum(1 for c in text if ord(c) >= 0x0C80 and ord(c) <= 0x0CFF)
        marathi_chars = sum(1 for c in text if ord(c) >= 0x0900 and ord(c) <= 0x097F)
        
        total_chars = len(text)
        
        if hindi_chars > total_chars * 0.3:
            return 'hi'
        elif tamil_chars > total_chars * 0.3:
            return 'ta'
        elif telugu_chars > total_chars * 0.3:
            return 'te'
        elif kannada_chars > total_chars * 0.3:
            return 'ka'
        elif marathi_chars > total_chars * 0.3:
            return 'mr'
        else:
            return 'en'
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return self.supported_languages


# Example usage
if __name__ == "__main__":
    translator = SimpleTranslationEngine()
    
    text = "Machine Learning is transforming technology"
    
    print("Original:", text)
    print("Hindi:", translator.translate(text, 'en', 'hi'))
    print("Tamil:", translator.translate(text, 'en', 'ta'))
    print("Telugu:", translator.translate(text, 'en', 'te'))
    print("Kannada:", translator.translate(text, 'en', 'ka'))
    print("Marathi:", translator.translate(text, 'en', 'mr'))
    print("Detected:", translator.detect_language(text))
