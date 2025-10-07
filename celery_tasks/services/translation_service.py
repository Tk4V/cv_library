"""
Translation service for handling CV translation operations.
"""
from typing import Dict, Tuple, Optional
from django.contrib.sessions.models import Session
from main.enums import Language
from .base_service import BaseService


class TranslationService(BaseService):
    """Service for handling CV translation operations."""
    
    def __init__(self):
        super().__init__()
        self._translation_providers = {
            'google': self._translate_with_google,
            'microsoft': self._translate_with_microsoft,
            'openai': self._translate_with_openai
        }
    
    def translate_cv(self, cv, target_language: str) -> Tuple[Dict[str, str], bool]:
        """
        Translate CV to target language.
        
        Args:
            cv: CV object to translate
            target_language: Target language name or code
            
        Returns:
            Tuple of (translations_dict, success_flag)
        """
        # Try to find the language by name first
        lang_enum = None
        for lang in Language:
            if lang.value.lower() == target_language.lower():
                lang_enum = lang
                break
        
        # If not found by name, try by enum key
        if not lang_enum:
            try:
                lang_enum = Language(target_language.upper())
            except ValueError:
                # If still not found, try to find by partial match
                for lang in Language:
                    if target_language.lower() in lang.value.lower() or lang.value.lower() in target_language.lower():
                        lang_enum = lang
                        break
        
        if not lang_enum:
            return {}, False
        
        translations = {}
        enabled = False
        
        for provider_name, translate_func in self._translation_providers.items():
            try:
                result = translate_func(cv, lang_enum.value)
                if result:
                    translations.update(result)
                    enabled = True
                    break
            except Exception:
                continue
        
        return translations, enabled
    
    def get_available_languages(self) -> list:
        """Get list of available languages."""
        return [lang.value for lang in Language]
    
    def get_language_code(self, language_name: str) -> str:
        """Get language code for translation services."""
        # Common language code mappings
        language_codes = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Russian': 'ru',
            'Chinese': 'zh',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Arabic': 'ar',
            'Hindi': 'hi',
            'Dutch': 'nl',
            'Swedish': 'sv',
            'Norwegian': 'no',
            'Danish': 'da',
            'Finnish': 'fi',
            'Polish': 'pl',
            'Czech': 'cs',
            'Hungarian': 'hu',
            'Romanian': 'ro',
            'Bulgarian': 'bg',
            'Croatian': 'hr',
            'Serbian': 'sr',
            'Slovak': 'sk',
            'Slovenian': 'sl',
            'Greek': 'el',
            'Turkish': 'tr',
            'Hebrew': 'he',
            'Persian': 'fa',
            'Urdu': 'ur',
            'Bengali': 'bn',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Gujarati': 'gu',
            'Kannada': 'kn',
            'Malayalam': 'ml',
            'Punjabi': 'pa',
            'Ukrainian': 'uk',
            'Belarusian': 'be',
            'Lithuanian': 'lt',
            'Latvian': 'lv',
            'Estonian': 'et',
            'Georgian': 'ka',
            'Armenian': 'hy',
            'Azerbaijani': 'az',
            'Kazakh': 'kk',
            'Uzbek': 'uz',
            'Kyrgyz': 'ky',
            'Tajik': 'tg',
            'Turkmen': 'tk',
            'Mongolian': 'mn',
            'Thai': 'th',
            'Vietnamese': 'vi',
            'Indonesian': 'id',
            'Malay': 'ms',
            'Tagalog': 'tl',
            'Swahili': 'sw',
            'Amharic': 'am',
            'Yoruba': 'yo',
            'Igbo': 'ig',
            'Hausa': 'ha',
            'Zulu': 'zu',
            'Afrikaans': 'af',
            'Albanian': 'sq',
            'Maltese': 'mt',
            'Icelandic': 'is',
            'Irish': 'ga',
            'Welsh': 'cy',
            'Scottish Gaelic': 'gd',
            'Basque': 'eu',
            'Catalan': 'ca',
            'Galician': 'gl',
        }
        
        return language_codes.get(language_name, 'en')  # Default to English
    
    def _translate_with_google(self, cv, target_language: str) -> Optional[Dict[str, str]]:
        """Translate using Google Translate (placeholder)."""
        # Get language code for translation service
        lang_code = self.get_language_code(target_language)
        
        # Placeholder implementation - in real implementation, you would use Google Translate API
        return {
            'bio': f"[{lang_code}] {cv.bio}",
            'skills': f"[{lang_code}] {cv.skills}",
            'projects': f"[{lang_code}] {cv.projects}",
            'contacts': f"[{lang_code}] {cv.contacts}",
            'lang': target_language,
            'lang_code': lang_code
        }
    
    def _translate_with_microsoft(self, cv, target_language: str) -> Optional[Dict[str, str]]:
        """Translate using Microsoft Translator (placeholder)."""
        # Placeholder implementation
        return None
    
    def _translate_with_openai(self, cv, target_language: str) -> Optional[Dict[str, str]]:
        """Translate using OpenAI (placeholder)."""
        # Placeholder implementation
        return None
