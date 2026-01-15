"""
MC Castellazzo - Context Processors
====================================
Fornisce variabili globali per tutti i templates.
"""
from django.conf import settings
from django.utils.translation import get_language


def schema_org(request):
    """
    Fornisce l'URL base per i dati schema.org.
    """
    return {
        "schema_org_base": "https://schema.org",
    }


def site_colors(request):
    """
    Fornisce i colori del tema.
    """
    return {
        "colors": getattr(settings, "THEME_COLORS", {
            "oro": "#D4AF37",
            "blu_nautico": "#1B263B",
            "amaranto": "#9B1D64",
        }),
    }


def navigation(request):
    """
    Fornisce navbar e footer per la lingua corrente.
    Usato in Jinja2 templates dove i template tags Django non funzionano.
    """
    from wagtail.models import Locale
    from apps.website.models import Navbar, Footer

    lang_code = get_language() or "it"
    try:
        locale = Locale.objects.get(language_code=lang_code)
    except Locale.DoesNotExist:
        try:
            locale = Locale.objects.get(language_code="it")
        except Locale.DoesNotExist:
            return {"navbar": None, "footer": None}

    navbar = Navbar.objects.filter(is_active=True, locale=locale).first()
    footer = Footer.objects.filter(is_active=True, locale=locale).first()

    return {
        "navbar": navbar,
        "footer": footer,
    }


def main_pages(request):
    """
    Fornisce le URL delle pagine principali per la lingua corrente.
    Compatibile con Wagtail/CodeRedCMS per evitare URL hardcoded nei template.
    
    Uso nei template:
        {{ main_pages.home }} → /it/ o /en/ etc.
        {{ main_pages.events }} → /it/eventi/
        {{ main_pages.about }} → /it/chi-siamo/
        {{ main_pages.contact }} → /it/chi-siamo/contatti/
    """
    from wagtail.models import Locale, Site
    
    lang_code = get_language() or "it"
    
    pages = {
        "home": None,
        "events": None,
        "events_archive": None,
        "about": None,
        "contact": None,
        "privacy": None,
        "news": None,
    }
    
    try:
        locale = Locale.objects.get(language_code=lang_code)
    except Locale.DoesNotExist:
        try:
            locale = Locale.objects.get(language_code="it")
        except Locale.DoesNotExist:
            return {"main_pages": pages}
    
    # Get the site's root page
    site = Site.find_for_request(request)
    if not site:
        return {"main_pages": pages}
    
    # Try to import page models - use try/except for robustness
    try:
        from apps.website.models import (
            HomePage, EventsPage, EventsArchivePage, 
            AboutPage, ContactPage, PrivacyPage, TimelinePage
        )
        
        # Find pages for current locale
        home = HomePage.objects.filter(locale=locale).live().first()
        if home:
            pages["home"] = home.url
        
        events = EventsPage.objects.filter(locale=locale).live().first()
        if events:
            pages["events"] = events.url
            
        events_archive = EventsArchivePage.objects.filter(locale=locale).live().first()
        if events_archive:
            pages["events_archive"] = events_archive.url
            
        about = AboutPage.objects.filter(locale=locale).live().first()
        if about:
            pages["about"] = about.url
            
        contact = ContactPage.objects.filter(locale=locale).live().first()
        if contact:
            pages["contact"] = contact.url
            
        privacy = PrivacyPage.objects.filter(locale=locale).live().first()
        if privacy:
            pages["privacy"] = privacy.url
            
        news = TimelinePage.objects.filter(locale=locale).live().first()
        if news:
            pages["news"] = news.url
            
    except ImportError:
        pass
    
    return {"main_pages": pages}


def page_translations(request):
    """
    Fornisce le traduzioni disponibili per la pagina corrente.
    Usato dal language switcher per costruire link corretti.
    
    Uso nei template:
        {% for lang_code, lang_url in page_translations.items() %}
            <a href="{{ lang_url }}">{{ lang_code }}</a>
        {% endfor %}
    """
    from wagtail.models import Locale, Page, Site
    
    translations = {}
    languages = ['it', 'en', 'fr', 'de', 'es']
    
    current_path = request.path
    
    # Cerca la pagina corrente usando il metodo di Wagtail
    site = Site.find_for_request(request)
    if not site:
        # Fallback: homepage per ogni lingua
        for lang in languages:
            translations[lang] = f'/{lang}/'
        return {"page_translations": translations}
    
    # Trova la pagina usando il path resolver di Wagtail
    page = None
    try:
        # Rimuovi la lingua dal path per trovare la pagina
        path_parts = current_path.strip('/').split('/')
        if path_parts and path_parts[0] in languages:
            # Path senza prefisso lingua
            remaining_path = path_parts[1:] if len(path_parts) > 1 else []
        else:
            remaining_path = path_parts
        
        # Cerca pagine per ogni locale per trovare quella corrente
        current_locale = None
        for lang in languages:
            try:
                locale = Locale.objects.get(language_code=lang)
                # Trova la root page per questa lingua
                root_pages = Page.objects.filter(
                    locale=locale,
                    depth=2  # Le homepage sono a depth 2
                ).live()
                
                for root in root_pages:
                    try:
                        route_result = root.route(request, remaining_path)
                        if route_result and route_result.page:
                            # Abbiamo trovato la pagina!
                            page = route_result.page
                            current_locale = locale
                            break
                    except Exception:
                        continue
                
                if page:
                    break
            except Locale.DoesNotExist:
                continue
                
    except Exception:
        pass
    
    if page:
        # Ottieni tutte le traduzioni della pagina
        try:
            page_translations_qs = page.get_translations(inclusive=True)
            for translated_page in page_translations_qs:
                lang = translated_page.locale.language_code
                if lang in languages:
                    translations[lang] = translated_page.url
        except Exception:
            pass
    
    # Fallback per lingue mancanti: homepage della lingua
    for lang in languages:
        if lang not in translations:
            translations[lang] = f'/{lang}/'
    
    return {"page_translations": translations}
