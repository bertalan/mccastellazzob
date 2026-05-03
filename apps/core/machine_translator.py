"""
MC Castellazzo - Machine Translator per Wagtail Localize
=========================================================
Traduttore automatico usando deep-translator con catena di fallback.
Prova i provider configurati in ordine: se uno va in timeout o fallisce,
passa al successivo. Ogni chiamata HTTP ha un timeout fisso per evitare
che i worker Gunicorn vengano uccisi.

Provider supportati: 'google', 'mymemory', 'deepl'
Default: ['google', 'mymemory'] — Google primo (più veloce), poi MyMemory.

Configurazione in settings.py:
    WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
        'CLASS': 'apps.core.machine_translator.DeepTranslatorMachineTranslator',
        'OPTIONS': {
            'DELAY': 0.3,
            'HTTP_TIMEOUT': 8,
            'PROVIDERS': ['google', 'mymemory'],
        }
    }

Per tradurre le stringhe non ancora tradotte (fallback CLI):
    python manage.py retry_translations
    python manage.py retry_translations --locale=fr
"""
import concurrent.futures
import logging
import re
import time
from html.parser import HTMLParser

from wagtail_localize.machine_translators.base import BaseMachineTranslator
from wagtail_localize.strings import StringValue

logger = logging.getLogger(__name__)


# Mapping delle lingue wagtail -> codici MyMemory (formato completo)
LANGUAGE_MAP_MYMEMORY = {
    "it": "it-IT",
    "en": "en-GB",
    "de": "de-DE",
    "fr": "fr-FR",
    "es": "es-ES",
}

# Mapping per Google Translate (codici ISO)
LANGUAGE_MAP_ISO = {
    "it": "it",
    "en": "en",
    "de": "de",
    "fr": "fr",
    "es": "es",
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
    Traduttore machine per Wagtail Localize con catena di fallback.

    Prova ogni provider in ordine (default: Google → MyMemory).
    Ogni chiamata HTTP ha un timeout configurabile (default 8s) per evitare
    che i worker Gunicorn vengano uccisi in attesa di risposte bloccate.

    Se tutte le traduzioni falliscono, le stringhe restano nel DB con
    translation_type='' — usare `manage.py retry_translations` per riprovarle.
    """

    display_name = "Multi-Provider Translator (Google + MyMemory)"

    def __init__(self, options=None):
        super().__init__(options)
        opts = options or {}
        self.delay = opts.get("DELAY", 0.3)
        self.http_timeout = opts.get("HTTP_TIMEOUT", 8)
        # Lista provider in ordine di priorità
        self.providers = opts.get("PROVIDERS", ["google", "mymemory"])
        # Opzioni specifiche provider
        self.mymemory_email = opts.get("MYMEMORY_EMAIL", None)
        self.deepl_api_key = opts.get("DEEPL_API_KEY", "")

    # ------------------------------------------------------------------
    # Creazione istanze traduttori
    # ------------------------------------------------------------------

    def _make_google_translator(self, source_lang, target_lang):
        from deep_translator import GoogleTranslator
        src = LANGUAGE_MAP_ISO.get(source_lang, source_lang)
        tgt = LANGUAGE_MAP_ISO.get(target_lang, target_lang)
        return GoogleTranslator(source=src, target=tgt)

    def _make_mymemory_translator(self, source_lang, target_lang):
        from deep_translator import MyMemoryTranslator
        src = LANGUAGE_MAP_MYMEMORY.get(source_lang, source_lang)
        tgt = LANGUAGE_MAP_MYMEMORY.get(target_lang, target_lang)
        if self.mymemory_email:
            return MyMemoryTranslator(source=src, target=tgt, email=self.mymemory_email)
        return MyMemoryTranslator(source=src, target=tgt)

    def _make_deepl_translator(self, source_lang, target_lang):
        from deep_translator import DeeplTranslator
        src = LANGUAGE_MAP_ISO.get(source_lang, source_lang)
        tgt = LANGUAGE_MAP_ISO.get(target_lang, target_lang)
        return DeeplTranslator(source=src, target=tgt, api_key=self.deepl_api_key)

    def _make_translator(self, provider, source_lang, target_lang):
        if provider == "google":
            return self._make_google_translator(source_lang, target_lang)
        elif provider == "deepl":
            return self._make_deepl_translator(source_lang, target_lang)
        else:  # mymemory (default)
            return self._make_mymemory_translator(source_lang, target_lang)

    # ------------------------------------------------------------------
    # Traduzione con timeout + fallback
    # ------------------------------------------------------------------

    def _call_translate(self, translator, text):
        """Chiama translator.translate() in un thread separato con timeout."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(translator.translate, text.strip())
            return future.result(timeout=self.http_timeout)

    def _translate_with_provider(self, text, source_lang, target_lang, provider):
        """Tenta la traduzione con un singolo provider. Rilancia eccezioni."""
        translator = self._make_translator(provider, source_lang, target_lang)
        return self._call_translate(translator, text)

    def _translate_text(self, text, source_lang, target_lang):
        """
        Traduce un singolo testo provando i provider in ordine.
        Restituisce il testo originale se tutti i provider falliscono.
        """
        if not text or not text.strip():
            return text

        leading = len(text) - len(text.lstrip())
        trailing = len(text) - len(text.rstrip())

        for provider in self.providers:
            try:
                result = self._translate_with_provider(
                    text, source_lang, target_lang, provider
                )
                if result and result.strip():
                    if leading:
                        result = " " * leading + result
                    if trailing:
                        result = result + " " * trailing
                    return result
            except concurrent.futures.TimeoutError:
                logger.warning(
                    f"[{provider}] timeout ({self.http_timeout}s) su '{text[:40]}...'"
                    f" — passo al provider successivo"
                )
            except Exception as e:
                logger.warning(
                    f"[{provider}] errore su '{text[:40]}...': {e}"
                    f" — passo al provider successivo"
                )

        logger.error(
            f"Tutti i provider hanno fallito per '{text[:60]}'. "
            f"Stringa non tradotta — riesegui `retry_translations`."
        )
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


# ---------------------------------------------------------------------------
# Funzione standalone: traduzione segmenti pendenti in background
# ---------------------------------------------------------------------------

# Lock per evitare avvii simultanei (es. più visitatori concorrenti)
import threading
_translation_lock = threading.Lock()
_translation_in_progress = False


def translate_pending_segments(locale_code=None, max_strings=200):
    """
    Traduce le StringTranslation che non hanno ancora una traduzione
    (data vuota o translation_type vuoto).

    Chiamabile da:
    - management command `retry_translations`
    - hook Wagtail `page_served` (background thread)

    Args:
        locale_code: codice lingua target (es. 'fr'). None = tutte le lingue.
        max_strings: limite massimo per esecuzione (evita run infiniti).

    Returns:
        dict con contatori {done, skipped, errors}
    """
    global _translation_in_progress

    # Controlla se c'è già una traduzione in corso
    if not _translation_lock.acquire(blocking=False):
        logger.info("translate_pending_segments: già in esecuzione, skip.")
        return {"done": 0, "skipped": 0, "errors": 0}

    _translation_in_progress = True
    stats = {"done": 0, "skipped": 0, "errors": 0}

    try:
        from django.conf import settings
        from wagtail.models import Locale
        from wagtail_localize.models import StringTranslation

        # Ottieni configurazione translator dagli stessi settings di Wagtail
        mt_settings = getattr(settings, "WAGTAILLOCALIZE_MACHINE_TRANSLATOR", {})
        opts = mt_settings.get("OPTIONS", {})
        translator = DeepTranslatorMachineTranslator(options=opts)

        # Trova StringTranslation senza dato tradotto
        qs = StringTranslation.objects.filter(data="").select_related(
            "translation_of", "locale", "context"
        )
        if locale_code:
            qs = qs.filter(locale__language_code=locale_code)

        pending = list(qs[:max_strings])

        if not pending:
            logger.info("translate_pending_segments: nessuna stringa pendente.")
            return stats

        logger.info(
            f"translate_pending_segments: {len(pending)} stringhe pendenti"
            + (f" [{locale_code}]" if locale_code else "")
        )

        # Raggruppa per lingua sorgente/target per ridurre istanze traduttore
        it_locale = Locale.objects.filter(language_code="it").first()
        if not it_locale:
            logger.error("Locale italiano non trovato.")
            return stats

        # Mappa codici semplici per la chiamata _translate_text
        for st in pending:
            try:
                src = LANGUAGE_MAP_ISO.get("it", "it")
                tgt = LANGUAGE_MAP_ISO.get(st.locale.language_code, st.locale.language_code)

                original = st.translation_of.data
                if not original or not original.strip():
                    stats["skipped"] += 1
                    continue

                has_html = bool(re.search(r"<[^>]+>", original))
                if has_html:
                    result = translator._translate_html(original, src, tgt)
                else:
                    result = translator._translate_text(original, src, tgt)

                if result and result != original:
                    st.data = result
                    st.save(update_fields=["data"])
                    stats["done"] += 1
                    time.sleep(translator.delay)
                else:
                    stats["skipped"] += 1

            except Exception as e:
                logger.error(f"translate_pending_segments errore su stringa {st.pk}: {e}")
                stats["errors"] += 1

    except Exception as e:
        logger.exception(f"translate_pending_segments errore generale: {e}")
    finally:
        _translation_in_progress = False
        _translation_lock.release()

    logger.info(
        f"translate_pending_segments completato — "
        f"done={stats['done']}, skip={stats['skipped']}, err={stats['errors']}"
    )
    return stats

