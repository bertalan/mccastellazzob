"""
MC Castellazzo - Machine Translator per Wagtail Localize
=========================================================
Traduttore automatico usando deep-translator (MyMemory - gratuito).
Integrato con Wagtail Localize per traduzione con un clic.

In produzione, sostituire con DeepL o Google Cloud Translate.
"""
import logging
import re
import time
from html.parser import HTMLParser

from wagtail_localize.machine_translators.base import BaseMachineTranslator
from wagtail_localize.strings import StringValue

logger = logging.getLogger(__name__)


# Mapping delle lingue wagtail -> codici MyMemory (formato completo)
# MyMemory usa codici come 'it-IT', 'en-GB', etc.
# GoogleTranslator e DeepL usano codici semplici come 'it', 'en'
LANGUAGE_MAP_MYMEMORY = {
    "it": "it-IT",
    "en": "en-GB",
    "de": "de-DE",
    "fr": "fr-FR",
    "es": "es-ES",
}

LANGUAGE_MAP_SIMPLE = {
    "it": "italian",
    "en": "english",
    "de": "german",
    "fr": "french",
    "es": "spanish",
}


class HTMLTextExtractor(HTMLParser):
    """Estrae testo da HTML mantenendo la struttura."""
    
    def __init__(self):
        super().__init__()
        self.result = []
        self.text_parts = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        if self.text_parts:
            self.result.append(("text", "".join(self.text_parts)))
            self.text_parts = []
        attrs_str = ""
        for name, value in attrs:
            attrs_str += f' {name}="{value}"'
        self.result.append(("start", f"<{tag}{attrs_str}>"))
        self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        if self.text_parts:
            self.result.append(("text", "".join(self.text_parts)))
            self.text_parts = []
        self.result.append(("end", f"</{tag}>"))
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
    
    def handle_data(self, data):
        if data.strip():
            self.text_parts.append(data)
        elif data:
            self.text_parts.append(data)
    
    def handle_entityref(self, name):
        self.text_parts.append(f"&{name};")
    
    def handle_charref(self, name):
        self.text_parts.append(f"&#{name};")
    
    def get_parts(self):
        if self.text_parts:
            self.result.append(("text", "".join(self.text_parts)))
        return self.result


class DeepTranslatorMachineTranslator(BaseMachineTranslator):
    """
    Traduttore machine per Wagtail Localize usando deep-translator.
    
    Usa MyMemory (gratuito, 1000 req/giorno senza email, 10000 con email).
    Supporta traduzione di HTML preservando i tag.
    
    In produzione, configurare TRANSLATOR_PROVIDER in settings per usare
    'deepl' o 'google' con le rispettive API key.
    """
    
    display_name = "MyMemory Translate (Gratuito)"
    
    def __init__(self, options=None):
        super().__init__(options)
        self.delay = (options or {}).get("DELAY", 0.5)
        # Provider: 'mymemory' (default gratuito), 'google', 'deepl'
        self.provider = (options or {}).get("PROVIDER", "mymemory")
        # Email opzionale per MyMemory (aumenta limite a 10000/giorno)
        self.mymemory_email = (options or {}).get("MYMEMORY_EMAIL", None)
    
    def _get_translator(self, source_lang, target_lang):
        """Crea un'istanza del traduttore in base al provider configurato."""
        try:
            if self.provider == "google":
                from deep_translator import GoogleTranslator
                # Google usa codici semplici o nomi completi
                src = LANGUAGE_MAP_SIMPLE.get(source_lang, source_lang)
                tgt = LANGUAGE_MAP_SIMPLE.get(target_lang, target_lang)
                return GoogleTranslator(source=src, target=tgt)
            elif self.provider == "deepl":
                from deep_translator import DeeplTranslator
                api_key = (self.options or {}).get("DEEPL_API_KEY", "")
                return DeeplTranslator(source=source_lang, target=target_lang, api_key=api_key)
            else:
                # Default: MyMemory (gratuito) - richiede codici completi
                from deep_translator import MyMemoryTranslator
                src = LANGUAGE_MAP_MYMEMORY.get(source_lang, source_lang)
                tgt = LANGUAGE_MAP_MYMEMORY.get(target_lang, target_lang)
                if self.mymemory_email:
                    return MyMemoryTranslator(
                        source=src, 
                        target=tgt,
                        email=self.mymemory_email
                    )
                return MyMemoryTranslator(source=src, target=tgt)
        except ImportError as e:
            logger.error(f"deep-translator non installato o provider non disponibile: {e}")
            raise
    
    def _translate_text(self, text, source_lang, target_lang):
        """Traduce un singolo testo."""
        if not text or not text.strip():
            return text
        
        # Preserva gli spazi iniziali e finali
        leading_space = len(text) - len(text.lstrip())
        trailing_space = len(text) - len(text.rstrip())
        
        translator = self._get_translator(source_lang, target_lang)
        
        try:
            translated = translator.translate(text.strip())
            
            # Ripristina spazi
            if leading_space:
                translated = " " * leading_space + translated
            if trailing_space:
                translated = translated + " " * trailing_space
                
            return translated
        except Exception as e:
            logger.warning(f"Errore traduzione '{text[:50]}...': {e}")
            return text
    
    def _translate_html(self, html, source_lang, target_lang):
        """Traduce HTML preservando i tag."""
        if not html or not html.strip():
            return html
        
        # Estrai le parti
        parser = HTMLTextExtractor()
        parser.feed(html)
        parts = parser.get_parts()
        
        # Traduci solo le parti testuali
        result = []
        for part_type, content in parts:
            if part_type == "text" and content.strip():
                translated = self._translate_text(content, source_lang, target_lang)
                result.append(translated)
                time.sleep(self.delay)  # Rate limiting
            else:
                result.append(content)
        
        return "".join(result)
    
    def translate(self, source_locale, target_locale, strings):
        """
        Traduce una lista di StringValue.
        
        Args:
            source_locale: Locale sorgente (es. it)
            target_locale: Locale destinazione (es. en)
            strings: Lista di StringValue da tradurre
            
        Returns:
            Dict con StringValue originali come chiavi e traduzioni come valori
        """
        source_lang = LANGUAGE_MAP_SIMPLE.get(
            source_locale.language_code, 
            source_locale.language_code
        )
        target_lang = LANGUAGE_MAP_SIMPLE.get(
            target_locale.language_code,
            target_locale.language_code
        )
        
        logger.info(
            f"Traduzione automatica: {source_lang} -> {target_lang} "
            f"({len(strings)} stringhe)"
        )
        
        translations = {}
        
        for i, string in enumerate(strings):
            try:
                # Ottieni l'HTML traducibile
                html = string.get_translatable_html()
                
                if not html or not html.strip():
                    translations[string] = string
                    continue
                
                # Verifica se contiene tag HTML
                has_html = bool(re.search(r"<[^>]+>", html))
                
                if has_html:
                    translated_html = self._translate_html(html, source_lang, target_lang)
                    translations[string] = StringValue.from_translated_html(translated_html)
                else:
                    translated_text = self._translate_text(html, source_lang, target_lang)
                    translations[string] = StringValue.from_plaintext(translated_text)
                
                # Log progresso
                if (i + 1) % 10 == 0:
                    logger.info(f"Tradotte {i + 1}/{len(strings)} stringhe...")
                
                # Rate limiting per evitare blocchi
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Errore traduzione stringa {i}: {e}")
                translations[string] = string
        
        logger.info(f"Traduzione completata: {len(translations)} stringhe")
        return translations
    
    def can_translate(self, source_locale, target_locale):
        """
        Verifica se questa coppia di lingue è supportata.
        """
        source = source_locale.language_code
        target = target_locale.language_code
        
        # Evita traduzione nella stessa lingua
        if source == target:
            return False
        
        # Verifica che entrambe le lingue siano supportate
        supported = {"it", "en", "de", "fr", "es"}
        return source in supported and target in supported
