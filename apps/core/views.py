"""
MC Castellazzo - Views per traduzione automatica
=================================================
View per tradurre automaticamente una pagina dalla lingua sorgente (IT).
"""
import logging
import time
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from wagtail.models import Page, Locale
from wagtail.fields import RichTextField, StreamField

logger = logging.getLogger(__name__)


def get_translator():
    """Inizializza il traduttore."""
    from apps.core.machine_translator import DeepTranslatorMachineTranslator
    return DeepTranslatorMachineTranslator()


def translate_text(translator, text, source_lang, target_lang):
    """Traduce un testo con gestione errori."""
    if not text or not isinstance(text, str) or not text.strip():
        return text
    try:
        return translator._translate_html(text, source_lang, target_lang)
    except Exception as e:
        logger.warning(f"Errore traduzione: {e}")
        return text


def translate_value(translator, value, source_lang, target_lang):
    """
    Traduce ricorsivamente qualsiasi valore:
    - str: traduce
    - dict: traduce ricorsivamente i campi testuali
    - list: traduce ogni elemento
    """
    if value is None:
        return None
    
    if isinstance(value, str):
        if value.strip():
            time.sleep(0.2)  # Rate limiting
            return translate_text(translator, value, source_lang, target_lang)
        return value
    
    if isinstance(value, dict):
        translated = {}
        for k, v in value.items():
            # Salta campi non testuali
            if k in ('id', 'pk', 'image', 'document', 'page', 'link_page', 
                     'icon', 'icon_bg_color', 'link_color', 'background',
                     'layout', 'autoplay', 'interval', 'height', 'show_countdown',
                     'columns', 'show_filters', 'order', 'type'):
                translated[k] = v
            else:
                translated[k] = translate_value(translator, v, source_lang, target_lang)
        return translated
    
    if isinstance(value, list):
        return [translate_value(translator, item, source_lang, target_lang) for item in value]
    
    # Altri tipi (int, bool, etc.) - ritorna così com'è
    return value


def translate_stream_data(translator, stream_data, source_lang, target_lang):
    """Traduce i dati grezzi di uno StreamField."""
    if not stream_data:
        return stream_data
    
    # Ottieni i dati raw
    if hasattr(stream_data, 'raw_data'):
        raw = list(stream_data.raw_data)
    elif hasattr(stream_data, 'stream_data'):
        raw = list(stream_data.stream_data)
    elif isinstance(stream_data, list):
        raw = stream_data
    else:
        return stream_data
    
    translated = []
    for block in raw:
        if isinstance(block, dict):
            translated_block = {
                'type': block.get('type'),
                'value': translate_value(translator, block.get('value'), source_lang, target_lang),
            }
            if 'id' in block:
                translated_block['id'] = block['id']
            translated.append(translated_block)
        else:
            translated.append(block)
    
    return translated


@staff_member_required
def auto_translate_page_view(request, page_id):
    """
    View che traduce automaticamente una pagina dalla versione italiana.
    
    Traduce TUTTI i campi:
    - Campi di testo semplici (CharField, TextField)
    - RichTextField
    - StreamField con tutti i blocchi nidificati
    """
    page = get_object_or_404(Page, id=page_id).specific
    current_locale = page.locale
    target_lang = current_locale.language_code
    
    # Non tradurre pagine italiane
    if target_lang == "it":
        messages.warning(request, "Questa pagina è già in italiano, non serve tradurla.")
        return redirect("wagtailadmin_pages:edit", page.id)
    
    # Trova la versione italiana
    try:
        it_locale = Locale.objects.get(language_code="it")
        it_page = page.get_translation(it_locale).specific
    except (Locale.DoesNotExist, Page.DoesNotExist):
        messages.error(request, "Impossibile trovare la versione italiana di questa pagina.")
        return redirect("wagtailadmin_pages:edit", page.id)
    
    translator = get_translator()
    translated_fields = []
    errors = []
    
    # === 1. Campi di testo semplici ===
    simple_text_fields = [
        'title', 'seo_title', 'search_description',
        'organization_name', 'hero_title', 'hero_subtitle',
        'intro', 'subtitle', 'summary', 'excerpt',
        'welcome_title', 'welcome_text',
        'cta_text', 'cta_button_text',
        'event_title', 'event_description',
        'page_title', 'page_subtitle',
    ]
    
    for field_name in simple_text_fields:
        if hasattr(it_page, field_name) and hasattr(page, field_name):
            it_value = getattr(it_page, field_name)
            if it_value and isinstance(it_value, str) and it_value.strip():
                try:
                    translated = translate_text(translator, it_value, "it", target_lang)
                    setattr(page, field_name, translated)
                    translated_fields.append(field_name)
                    logger.info(f"Tradotto {field_name}")
                except Exception as e:
                    errors.append(f"{field_name}: {e}")
    
    # === 2. RichTextField (description, body se è RichText, ecc.) ===
    rich_text_fields = ['description', 'intro', 'body', 'content']
    
    for field_name in rich_text_fields:
        if hasattr(it_page, field_name):
            field = it_page._meta.get_field(field_name) if hasattr(it_page._meta, 'get_field') else None
            it_value = getattr(it_page, field_name)
            
            # Se è una stringa (RichTextField), traducila
            if isinstance(it_value, str) and it_value.strip():
                if field_name not in translated_fields:
                    try:
                        translated = translate_text(translator, it_value, "it", target_lang)
                        setattr(page, field_name, translated)
                        translated_fields.append(field_name)
                        logger.info(f"Tradotto RichText {field_name}")
                    except Exception as e:
                        errors.append(f"{field_name}: {e}")
    
    # === 3. StreamField ===
    stream_field_names = ['body', 'content', 'blocks', 'gallery_blocks', 'articles', 
                          'slides', 'stats', 'cards', 'members', 'documents', 'timeline']
    
    for field_name in stream_field_names:
        if not hasattr(it_page, field_name):
            continue
        
        it_field = getattr(it_page, field_name)
        
        # Verifica se è uno StreamField
        if not (hasattr(it_field, 'raw_data') or hasattr(it_field, 'stream_data')):
            continue
        
        try:
            translated_data = translate_stream_data(translator, it_field, "it", target_lang)
            
            if translated_data:
                setattr(page, field_name, translated_data)
                if field_name not in translated_fields:
                    translated_fields.append(f"{field_name} (StreamField)")
                logger.info(f"Tradotto StreamField {field_name}")
        except Exception as e:
            errors.append(f"StreamField {field_name}: {e}")
            logger.error(f"Errore StreamField {field_name}: {e}")
    
    # === 4. Salva come bozza ===
    if translated_fields:
        try:
            page.save_revision(user=request.user)
            success_msg = f"✅ Traduzione completata! Campi tradotti: {', '.join(translated_fields)}."
            if errors:
                success_msg += f" Errori: {len(errors)}"
            messages.success(request, success_msg)
        except Exception as e:
            logger.error(f"Errore salvataggio: {e}")
            messages.error(request, f"Errore nel salvataggio: {e}")
    else:
        if errors:
            messages.warning(request, f"Nessun campo tradotto. Errori: {', '.join(errors)}")
        else:
            messages.info(request, "Nessun campo da tradurre trovato.")
    
    return redirect("wagtailadmin_pages:edit", page.id)
