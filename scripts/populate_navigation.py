"""
Popola Navbar e Footer per tutte le lingue.
Esegui con: python manage.py shell < scripts/populate_navigation.py
"""
from wagtail.models import Locale
from apps.website.models import Navbar, Footer

# =============================================================================
# NAVBAR DATA
# =============================================================================
navbar_data = {
    'it': {
        'name': 'Navigazione Principale',
        'items': [
            {'type': 'link', 'text': 'Home', 'url': '/it/', 'icon': 'fas fa-home'},
            {'type': 'link', 'text': 'Novità', 'url': '/it/novita/', 'icon': 'fas fa-newspaper'},
            {'type': 'dropdown', 'title': 'Chi Siamo', 'icon': 'fas fa-users', 'links': [
                {'text': 'La Nostra Storia', 'url': '/it/chi-siamo/'},
                {'text': 'Consiglio Direttivo', 'url': '/it/chi-siamo/consiglio-direttivo/'},
                {'text': 'Trasparenza', 'url': '/it/chi-siamo/trasparenza/'},
                {'text': 'Contatti', 'url': '/it/chi-siamo/contatti/'},
            ]},
            {'type': 'link', 'text': 'Eventi', 'url': '/it/eventi/', 'icon': 'fas fa-calendar-alt'},
            {'type': 'link', 'text': 'Galleria', 'url': '/it/galleria/', 'icon': 'fas fa-images'},
        ],
    },
    'en': {
        'name': 'Main Navigation',
        'items': [
            {'type': 'link', 'text': 'Home', 'url': '/en/', 'icon': 'fas fa-home'},
            {'type': 'link', 'text': 'News', 'url': '/en/novita/', 'icon': 'fas fa-newspaper'},
            {'type': 'dropdown', 'title': 'About Us', 'icon': 'fas fa-users', 'links': [
                {'text': 'Our History', 'url': '/en/chi-siamo/'},
                {'text': 'Board of Directors', 'url': '/en/chi-siamo/consiglio-direttivo/'},
                {'text': 'Transparency', 'url': '/en/chi-siamo/trasparenza/'},
                {'text': 'Contact Us', 'url': '/en/chi-siamo/contatti/'},
            ]},
            {'type': 'link', 'text': 'Events', 'url': '/en/eventi/', 'icon': 'fas fa-calendar-alt'},
            {'type': 'link', 'text': 'Gallery', 'url': '/en/galleria/', 'icon': 'fas fa-images'},
        ],
    },
    'de': {
        'name': 'Hauptnavigation',
        'items': [
            {'type': 'link', 'text': 'Startseite', 'url': '/de/', 'icon': 'fas fa-home'},
            {'type': 'link', 'text': 'Neuigkeiten', 'url': '/de/novita/', 'icon': 'fas fa-newspaper'},
            {'type': 'dropdown', 'title': 'Über Uns', 'icon': 'fas fa-users', 'links': [
                {'text': 'Unsere Geschichte', 'url': '/de/chi-siamo/'},
                {'text': 'Vorstand', 'url': '/de/chi-siamo/consiglio-direttivo/'},
                {'text': 'Transparenz', 'url': '/de/chi-siamo/trasparenza/'},
                {'text': 'Kontakt', 'url': '/de/chi-siamo/contatti/'},
            ]},
            {'type': 'link', 'text': 'Veranstaltungen', 'url': '/de/eventi/', 'icon': 'fas fa-calendar-alt'},
            {'type': 'link', 'text': 'Galerie', 'url': '/de/galleria/', 'icon': 'fas fa-images'},
        ],
    },
    'fr': {
        'name': 'Navigation Principale',
        'items': [
            {'type': 'link', 'text': 'Accueil', 'url': '/fr/', 'icon': 'fas fa-home'},
            {'type': 'link', 'text': 'Actualités', 'url': '/fr/novita/', 'icon': 'fas fa-newspaper'},
            {'type': 'dropdown', 'title': 'Qui Sommes-Nous', 'icon': 'fas fa-users', 'links': [
                {'text': 'Notre Histoire', 'url': '/fr/chi-siamo/'},
                {'text': "Conseil d'Administration", 'url': '/fr/chi-siamo/consiglio-direttivo/'},
                {'text': 'Transparence', 'url': '/fr/chi-siamo/trasparenza/'},
                {'text': 'Contact', 'url': '/fr/chi-siamo/contatti/'},
            ]},
            {'type': 'link', 'text': 'Événements', 'url': '/fr/eventi/', 'icon': 'fas fa-calendar-alt'},
            {'type': 'link', 'text': 'Galerie', 'url': '/fr/galleria/', 'icon': 'fas fa-images'},
        ],
    },
    'es': {
        'name': 'Navegación Principal',
        'items': [
            {'type': 'link', 'text': 'Inicio', 'url': '/es/', 'icon': 'fas fa-home'},
            {'type': 'link', 'text': 'Novedades', 'url': '/es/novita/', 'icon': 'fas fa-newspaper'},
            {'type': 'dropdown', 'title': 'Quiénes Somos', 'icon': 'fas fa-users', 'links': [
                {'text': 'Nuestra Historia', 'url': '/es/chi-siamo/'},
                {'text': 'Junta Directiva', 'url': '/es/chi-siamo/consiglio-direttivo/'},
                {'text': 'Transparencia', 'url': '/es/chi-siamo/trasparenza/'},
                {'text': 'Contacto', 'url': '/es/chi-siamo/contatti/'},
            ]},
            {'type': 'link', 'text': 'Eventos', 'url': '/es/eventi/', 'icon': 'fas fa-calendar-alt'},
            {'type': 'link', 'text': 'Galería', 'url': '/es/galleria/', 'icon': 'fas fa-images'},
        ],
    },
}

# =============================================================================
# FOOTER DATA
# =============================================================================
footer_data = {
    'it': {
        'name': 'Footer Principale',
        'tagline': 'Il più antico Moto Club del Piemonte. Passione, adrenalina e fratellanza su due ruote dal 1933.',
        'copyright': '© 2026 MC Castellazzo Bormida. Tutti i diritti riservati.',
        'columns': [
            {
                'title': 'Link Rapidi',
                'links': [
                    {'text': 'Home', 'url': '/it/'},
                    {'text': 'Novità', 'url': '/it/novita/'},
                    {'text': 'Chi Siamo', 'url': '/it/chi-siamo/'},
                    {'text': 'Eventi', 'url': '/it/eventi/'},
                    {'text': 'Galleria', 'url': '/it/galleria/'},
                    {'text': 'Contatti', 'url': '/it/chi-siamo/contatti/'},
                ],
            },
            {
                'title': 'Trasparenza',
                'links': [
                    {'text': 'Consiglio Direttivo', 'url': '/it/chi-siamo/consiglio-direttivo/'},
                    {'text': 'Documenti', 'url': '/it/chi-siamo/trasparenza/'},
                    {'text': 'Privacy Policy', 'url': '/it/privacy/'},
                ],
            },
        ],
        'socials': [
            {'platform': 'facebook', 'url': 'https://www.facebook.com/mccastellazzobormida'},
            {'platform': 'instagram', 'url': 'https://www.instagram.com/mccastellazzobormida'},
        ],
    },
    'en': {
        'name': 'Main Footer',
        'tagline': "Piedmont's oldest Motorcycle Club. Passion, adrenaline and brotherhood on two wheels since 1933.",
        'copyright': '© 2026 MC Castellazzo Bormida. All rights reserved.',
        'columns': [
            {
                'title': 'Quick Links',
                'links': [
                    {'text': 'Home', 'url': '/en/'},
                    {'text': 'News', 'url': '/en/novita/'},
                    {'text': 'About Us', 'url': '/en/chi-siamo/'},
                    {'text': 'Events', 'url': '/en/eventi/'},
                    {'text': 'Gallery', 'url': '/en/galleria/'},
                    {'text': 'Contact', 'url': '/en/chi-siamo/contatti/'},
                ],
            },
            {
                'title': 'Transparency',
                'links': [
                    {'text': 'Board of Directors', 'url': '/en/chi-siamo/consiglio-direttivo/'},
                    {'text': 'Documents', 'url': '/en/chi-siamo/trasparenza/'},
                    {'text': 'Privacy Policy', 'url': '/en/privacy/'},
                ],
            },
        ],
        'socials': [
            {'platform': 'facebook', 'url': 'https://www.facebook.com/mccastellazzobormida'},
            {'platform': 'instagram', 'url': 'https://www.instagram.com/mccastellazzobormida'},
        ],
    },
    'de': {
        'name': 'Haupt-Footer',
        'tagline': 'Der älteste Motorradclub des Piemont. Leidenschaft, Adrenalin und Brüderlichkeit auf zwei Rädern seit 1933.',
        'copyright': '© 2026 MC Castellazzo Bormida. Alle Rechte vorbehalten.',
        'columns': [
            {
                'title': 'Schnelllinks',
                'links': [
                    {'text': 'Startseite', 'url': '/de/'},
                    {'text': 'Neuigkeiten', 'url': '/de/novita/'},
                    {'text': 'Über Uns', 'url': '/de/chi-siamo/'},
                    {'text': 'Veranstaltungen', 'url': '/de/eventi/'},
                    {'text': 'Galerie', 'url': '/de/galleria/'},
                    {'text': 'Kontakt', 'url': '/de/chi-siamo/contatti/'},
                ],
            },
            {
                'title': 'Transparenz',
                'links': [
                    {'text': 'Vorstand', 'url': '/de/chi-siamo/consiglio-direttivo/'},
                    {'text': 'Dokumente', 'url': '/de/chi-siamo/trasparenza/'},
                    {'text': 'Datenschutz', 'url': '/de/privacy/'},
                ],
            },
        ],
        'socials': [
            {'platform': 'facebook', 'url': 'https://www.facebook.com/mccastellazzobormida'},
            {'platform': 'instagram', 'url': 'https://www.instagram.com/mccastellazzobormida'},
        ],
    },
    'fr': {
        'name': 'Pied de Page Principal',
        'tagline': 'Le plus ancien Moto Club du Piémont. Passion, adrénaline et fraternité sur deux roues depuis 1933.',
        'copyright': '© 2026 MC Castellazzo Bormida. Tous droits réservés.',
        'columns': [
            {
                'title': 'Liens Rapides',
                'links': [
                    {'text': 'Accueil', 'url': '/fr/'},
                    {'text': 'Actualités', 'url': '/fr/novita/'},
                    {'text': 'Qui Sommes-Nous', 'url': '/fr/chi-siamo/'},
                    {'text': 'Événements', 'url': '/fr/eventi/'},
                    {'text': 'Galerie', 'url': '/fr/galleria/'},
                    {'text': 'Contact', 'url': '/fr/chi-siamo/contatti/'},
                ],
            },
            {
                'title': 'Transparence',
                'links': [
                    {'text': "Conseil d'Administration", 'url': '/fr/chi-siamo/consiglio-direttivo/'},
                    {'text': 'Documents', 'url': '/fr/chi-siamo/trasparenza/'},
                    {'text': 'Politique de Confidentialité', 'url': '/fr/privacy/'},
                ],
            },
        ],
        'socials': [
            {'platform': 'facebook', 'url': 'https://www.facebook.com/mccastellazzobormida'},
            {'platform': 'instagram', 'url': 'https://www.instagram.com/mccastellazzobormida'},
        ],
    },
    'es': {
        'name': 'Pie de Página Principal',
        'tagline': 'El Moto Club más antiguo del Piamonte. Pasión, adrenalina y hermandad sobre dos ruedas desde 1933.',
        'copyright': '© 2026 MC Castellazzo Bormida. Todos los derechos reservados.',
        'columns': [
            {
                'title': 'Enlaces Rápidos',
                'links': [
                    {'text': 'Inicio', 'url': '/es/'},
                    {'text': 'Novedades', 'url': '/es/novita/'},
                    {'text': 'Quiénes Somos', 'url': '/es/chi-siamo/'},
                    {'text': 'Eventos', 'url': '/es/eventi/'},
                    {'text': 'Galería', 'url': '/es/galleria/'},
                    {'text': 'Contacto', 'url': '/es/chi-siamo/contatti/'},
                ],
            },
            {
                'title': 'Transparencia',
                'links': [
                    {'text': 'Junta Directiva', 'url': '/es/chi-siamo/consiglio-direttivo/'},
                    {'text': 'Documentos', 'url': '/es/chi-siamo/trasparenza/'},
                    {'text': 'Política de Privacidad', 'url': '/es/privacy/'},
                ],
            },
        ],
        'socials': [
            {'platform': 'facebook', 'url': 'https://www.facebook.com/mccastellazzobormida'},
            {'platform': 'instagram', 'url': 'https://www.instagram.com/mccastellazzobormida'},
        ],
    },
}


def build_menu_items(items):
    """Costruisce la struttura StreamField per menu_items."""
    menu_items = []
    for item in items:
        if item['type'] == 'link':
            menu_items.append({
                'type': 'link',
                'value': {
                    'button_title': item['text'],
                    'page_link': None,
                    'doc_link': None,
                    'other_link': item['url'],
                    'icon': item.get('icon', ''),
                }
            })
        elif item['type'] == 'dropdown':
            links = []
            for link in item['links']:
                links.append({
                    'button_title': link['text'],
                    'page_link': None,
                    'doc_link': None,
                    'other_link': link['url'],
                    'icon': '',
                })
            menu_items.append({
                'type': 'dropdown',
                'value': {
                    'title': item['title'],
                    'icon': item.get('icon', ''),
                    'links': links,
                }
            })
    return menu_items


def build_footer_columns(columns):
    """Costruisce la struttura StreamField per columns."""
    result = []
    for col in columns:
        links = []
        for link in col['links']:
            links.append({
                'button_title': link['text'],
                'page_link': None,
                'doc_link': None,
                'other_link': link['url'],
                'icon': '',
            })
        result.append({
            'type': 'column',
            'value': {
                'title': col['title'],
                'links': links,
            }
        })
    return result


def build_social_links(socials):
    """Costruisce la struttura StreamField per social_links."""
    result = []
    for social in socials:
        result.append({
            'type': 'social',
            'value': {
                'platform': social['platform'],
                'url': social['url'],
            }
        })
    return result


# =============================================================================
# CREAZIONE NAVBAR
# =============================================================================
print("=" * 60)
print("CREAZIONE NAVBAR")
print("=" * 60)

for lang_code, data in navbar_data.items():
    try:
        locale = Locale.objects.get(language_code=lang_code)
    except Locale.DoesNotExist:
        print(f"❌ Locale {lang_code} non esiste, skip")
        continue
    
    menu_items = build_menu_items(data['items'])
    
    # Elimina navbar esistenti per questa lingua
    Navbar.objects.filter(locale=locale).delete()
    
    navbar = Navbar.objects.create(
        locale=locale,
        name=data['name'],
        is_active=True,
        menu_items=menu_items,
    )
    print(f"✅ Navbar {lang_code}: {data['name']} creata")

# =============================================================================
# CREAZIONE FOOTER
# =============================================================================
print()
print("=" * 60)
print("CREAZIONE FOOTER")
print("=" * 60)

for lang_code, data in footer_data.items():
    try:
        locale = Locale.objects.get(language_code=lang_code)
    except Locale.DoesNotExist:
        print(f"❌ Locale {lang_code} non esiste, skip")
        continue
    
    columns = build_footer_columns(data['columns'])
    social_links = build_social_links(data['socials'])
    
    # Elimina footer esistenti per questa lingua
    Footer.objects.filter(locale=locale).delete()
    
    footer = Footer.objects.create(
        locale=locale,
        name=data['name'],
        is_active=True,
        tagline=data['tagline'],
        columns=columns,
        social_links=social_links,
        copyright_text=data['copyright'],
    )
    print(f"✅ Footer {lang_code}: {data['name']} creato")

print()
print("=" * 60)
print("COMPLETATO!")
print("=" * 60)
print(f"Navbar create: {Navbar.objects.count()}")
print(f"Footer creati: {Footer.objects.count()}")
