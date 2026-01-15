#!/usr/bin/env python
"""Script per creare le traduzioni delle pagine."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mccastellazzob.settings.docker')
django.setup()

from wagtail.models import Locale, Page
from django.db import transaction

# Titoli tradotti per le pagine principali
TRANSLATIONS = {
    'en': {
        'Chi Siamo': 'About Us',
        'Consiglio Direttivo': 'Board of Directors',
        'Trasparenza': 'Transparency',
        'Contatti': 'Contacts',
        'Eventi': 'Events',
        'Archivio Eventi': 'Events Archive',
        'Galleria Fotografica': 'Photo Gallery',
        'Privacy Policy': 'Privacy Policy',
    },
    'de': {
        'Chi Siamo': 'Uber Uns',
        'Consiglio Direttivo': 'Vorstand',
        'Trasparenza': 'Transparenz',
        'Contatti': 'Kontakt',
        'Eventi': 'Veranstaltungen',
        'Archivio Eventi': 'Veranstaltungsarchiv',
        'Galleria Fotografica': 'Fotogalerie',
        'Privacy Policy': 'Datenschutz',
    },
    'fr': {
        'Chi Siamo': 'A Propos',
        'Consiglio Direttivo': 'Conseil Administration',
        'Trasparenza': 'Transparence',
        'Contatti': 'Contacts',
        'Eventi': 'Evenements',
        'Archivio Eventi': 'Archives Evenements',
        'Galleria Fotografica': 'Galerie Photos',
        'Privacy Policy': 'Politique Confidentialite',
    },
    'es': {
        'Chi Siamo': 'Quienes Somos',
        'Consiglio Direttivo': 'Junta Directiva',
        'Trasparenza': 'Transparencia',
        'Contatti': 'Contactos',
        'Eventi': 'Eventos',
        'Archivio Eventi': 'Archivo Eventos',
        'Galleria Fotografica': 'Galeria Fotos',
        'Privacy Policy': 'Politica Privacidad',
    },
}

def create_translations():
    it_locale = Locale.objects.get(language_code='it')
    
    # Tutte le pagine da tradurre
    all_pages = [
        ('Chi Siamo', 3),
        ('Consiglio Direttivo', 4),
        ('Trasparenza', 4),
        ('Contatti', 4),
        ('Eventi', 3),
        ('Archivio Eventi', 3),
        ('Galleria Fotografica', 3),
        ('Privacy Policy', 3),
    ]
    
    for lang_code in ['en', 'de', 'fr', 'es']:
        target_locale = Locale.objects.get(language_code=lang_code)
        
        print(f"\n=== {lang_code.upper()} ===")
        
        for title, depth in all_pages:
            try:
                # Trova la pagina italiana
                it_page = Page.objects.get(locale=it_locale, title=title, depth=depth)
                
                # Trova la traduzione esistente tramite translation_key
                try:
                    translated = Page.objects.get(
                        translation_key=it_page.translation_key,
                        locale=target_locale
                    ).specific
                    
                    # Aggiorna titolo e slug
                    new_title = TRANSLATIONS[lang_code].get(title, title)
                    new_slug = new_title.lower().replace(' ', '-')
                    
                    if translated.title != new_title:
                        translated.title = new_title
                        translated.slug = new_slug
                        translated.save_revision().publish()
                        print(f"  U {title} -> {new_title}")
                    else:
                        print(f"  OK {title}")
                        
                except Page.DoesNotExist:
                    print(f"  X {title} - traduzione non trovata")
                    
            except Page.DoesNotExist:
                print(f"  X {title} - originale non trovata")
            except Exception as e:
                print(f"  X {title} - errore: {e}")

if __name__ == '__main__':
    with transaction.atomic():
        create_translations()
    print("\nDone!")
