"""
MC Castellazzo - Translation Utilities
======================================
Auto-traduzione con LibreTranslate (self-hosted o API pubblica).
"""
import requests
from django.conf import settings


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
) -> str | None:
    """
    Traduce testo usando LibreTranslate.
    
    Args:
        text: Testo da tradurre
        source_lang: Codice lingua sorgente (it, fr, es, en)
        target_lang: Codice lingua target
        
    Returns:
        Testo tradotto o None se errore
    """
    # URL LibreTranslate (può essere self-hosted o pubblico)
    base_url = getattr(settings, "LIBRETRANSLATE_URL", "https://libretranslate.com")
    api_key = getattr(settings, "LIBRETRANSLATE_API_KEY", None)
    
    try:
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }
        if api_key:
            payload["api_key"] = api_key
            
        response = requests.post(
            f"{base_url}/translate",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        return data.get("translatedText")
    except (requests.RequestException, ValueError, KeyError):
        pass
    
    return None


def auto_translate_fields(
    instance,
    fields: list[str],
    source_lang: str,
    target_langs: list[str] = None,
) -> dict[str, dict[str, str]]:
    """
    Auto-traduce campi di un'istanza in tutte le lingue target.
    
    Args:
        instance: Oggetto con i campi da tradurre
        fields: Lista nomi campi da tradurre
        source_lang: Lingua sorgente
        target_langs: Lingue target (default: tutte tranne source)
        
    Returns:
        Dict {field_name: {lang: translated_text}}
    """
    if target_langs is None:
        all_langs = [code for code, _ in getattr(settings, "LANGUAGES", [])]
        target_langs = [lang for lang in all_langs if lang != source_lang]
    
    translations = {}
    
    for field_name in fields:
        field_value = getattr(instance, field_name, "")
        if not field_value:
            continue
            
        translations[field_name] = {}
        for target_lang in target_langs:
            translated = translate_text(str(field_value), source_lang, target_lang)
            if translated:
                translations[field_name][target_lang] = translated
    
    return translations
