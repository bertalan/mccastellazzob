"""
Management command to populate the site with initial content.
Creates locales, site, homepage, navbar, footer, and pages in IT/EN/FR.
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Locale, Page, Site
from apps.website.models import (
    ArticleIndexPage,
    ArticlePage,
    EventIndexPage,
    EventPage,
    Footer,
    FormPage,
    LocationIndexPage,
    LocationPage,
    Navbar,
    WebPage,
)


class Command(BaseCommand):
    help = "Populate the site with initial multilingual content"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing content before creating new content",
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Populating site content...")

        # 1. Create locales
        self.create_locales()

        # 2. Create/update site structure
        self.create_site_structure()

        # 3. Create navbar snippets
        self.create_navbars()

        # 4. Create footer snippets
        self.create_footers()

        self.stdout.write(self.style.SUCCESS("✅ Content population complete!"))

    def create_locales(self):
        """Create IT, EN, FR locales if they don't exist."""
        locales_data = [
            ("it", "Italiano"),
            ("en", "English"),
            ("fr", "Français"),
        ]

        for lang_code, lang_name in locales_data:
            locale, created = Locale.objects.get_or_create(language_code=lang_code)
            if created:
                self.stdout.write(f"  ✓ Created locale: {lang_name} ({lang_code})")
            else:
                self.stdout.write(f"  • Locale exists: {lang_name} ({lang_code})")

    def create_site_structure(self):
        """Create homepage and site structure for all languages."""
        it_locale = Locale.objects.get(language_code="it")
        en_locale = Locale.objects.get(language_code="en")
        fr_locale = Locale.objects.get(language_code="fr")

        # Get or create root page
        root_page = Page.objects.filter(depth=1).first()
        if not root_page:
            self.stdout.write(self.style.ERROR("  ✗ Root page not found!"))
            return

        # Get or update Italian homepage (default)
        home_it = self._get_or_update_homepage(root_page, it_locale, "Home", "home")

        # Get or create English homepage
        home_en = self._get_or_update_homepage(
            root_page, en_locale, "Home", "home-en", translation_of=home_it
        )

        # Get or create French homepage
        home_fr = self._get_or_update_homepage(
            root_page, fr_locale, "Home", "home-fr", translation_of=home_it
        )

        # Set up Site
        if home_it:
            site, created = Site.objects.get_or_create(
                is_default_site=True,
                defaults={
                    "hostname": "localhost",
                    "port": 8002,
                    "site_name": "MC Castellazzo Bormida",
                    "root_page": home_it,
                },
            )
            if created:
                self.stdout.write("  ✓ Created default site")
            else:
                if site.root_page != home_it:
                    site.root_page = home_it
                    site.site_name = "MC Castellazzo Bormida"
                    site.save()
                    self.stdout.write("  ✓ Updated default site root page")
                else:
                    self.stdout.write("  • Default site exists")

        # Create subpages
        if home_it and home_en and home_fr:
            self._create_subpages(home_it, home_en, home_fr)

    def _get_or_update_homepage(
        self, root_page, locale, title, slug, translation_of=None
    ):
        """Get existing homepage or update default Wagtail page for a specific locale."""
        try:
            # Check if homepage already exists as WebPage
            existing_webpage = WebPage.objects.filter(slug=slug, locale=locale).first()
            if existing_webpage:
                self.stdout.write(f"  • Homepage exists as WebPage: {title} ({locale.language_code})")
                return existing_webpage

            # Check if there's a default Page (not WebPage) with this slug
            existing_page = Page.objects.filter(slug=slug, locale=locale).first()
            if existing_page:
                # Update the existing page's title
                existing_page.title = title
                existing_page.seo_title = f"MC Castellazzo Bormida - {locale.language_code.upper()}"
                existing_page.search_description = self._get_seo_description(locale.language_code)
                
                if translation_of:
                    existing_page.translation_key = translation_of.translation_key
                
                existing_page.save()
                self.stdout.write(f"  ✓ Updated existing homepage: {title} ({locale.language_code})")
                return existing_page

            # Create new homepage
            homepage = WebPage(
                title=title,
                slug=slug,
                locale=locale,
                seo_title=f"MC Castellazzo Bormida - {locale.language_code.upper()}",
                search_description=self._get_seo_description(locale.language_code),
            )

            if translation_of:
                homepage.translation_key = translation_of.translation_key

            root_page.add_child(instance=homepage)
            homepage.save_revision().publish()
            self.stdout.write(f"  ✓ Created homepage: {title} ({locale.language_code})")
            return homepage

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Error with homepage: {e}")
            )
            return None

    def _get_seo_description(self, lang_code):
        """Get SEO description for each language."""
        descriptions = {
            "it": "Moto Club Castellazzo Bormida - Passione, moto e territorio dal 1933",
            "en": "Moto Club Castellazzo Bormida - Passion, motorcycles and territory since 1933",
            "fr": "Moto Club Castellazzo Bormida - Passion, motos et territoire depuis 1933",
        }
        return descriptions.get(lang_code, descriptions["it"])

    def _create_subpages(self, home_it, home_en, home_fr):
        """Create subpages for all locales."""
        if not home_it or not home_en or not home_fr:
            return

        it_locale = Locale.objects.get(language_code="it")
        en_locale = Locale.objects.get(language_code="en")
        fr_locale = Locale.objects.get(language_code="fr")

        # About page
        about_it = self._create_or_get_page(
            home_it,
            WebPage,
            "La nostra associazione",
            "la-nostra-associazione",
            it_locale,
            body=self._get_about_body("it"),
        )
        about_en = self._create_or_get_page(
            home_en,
            WebPage,
            "Our association",
            "our-association",
            en_locale,
            body=self._get_about_body("en"),
            translation_of=about_it,
        )
        about_fr = self._create_or_get_page(
            home_fr,
            WebPage,
            "Notre association",
            "notre-association",
            fr_locale,
            body=self._get_about_body("fr"),
            translation_of=about_it,
        )

        # Events index page
        events_it = self._create_or_get_page(
            home_it, EventIndexPage, "Incontriamoci", "incontriamoci", it_locale
        )
        events_en = self._create_or_get_page(
            home_en,
            EventIndexPage,
            "Let's get together",
            "lets-get-together",
            en_locale,
            translation_of=events_it,
        )
        events_fr = self._create_or_get_page(
            home_fr,
            EventIndexPage,
            "Rencontrons-nous",
            "rencontrons-nous",
            fr_locale,
            translation_of=events_it,
        )

        # Contact page
        contact_it = self._create_or_get_page(
            home_it, WebPage, "Contatti", "contatti", it_locale
        )
        contact_en = self._create_or_get_page(
            home_en,
            WebPage,
            "Contact Us",
            "contact-us",
            en_locale,
            translation_of=contact_it,
        )
        contact_fr = self._create_or_get_page(
            home_fr,
            WebPage,
            "Contacts",
            "contacts",
            fr_locale,
            translation_of=contact_it,
        )

    def _create_or_get_page(
        self, parent, model, title, slug, locale, body=None, translation_of=None
    ):
        """Create or get a page."""
        try:
            existing = model.objects.filter(slug=slug, locale=locale).first()
            if existing:
                self.stdout.write(f"    • Page exists: {title} ({locale.language_code})")
                return existing

            page_kwargs = {
                "title": title,
                "slug": slug,
                "locale": locale,
            }

            if body and hasattr(model, "body"):
                page_kwargs["body"] = body

            page = model(**page_kwargs)

            if translation_of:
                page.translation_key = translation_of.translation_key

            parent.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(f"    ✓ Created page: {title} ({locale.language_code})")
            return page

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"    ✗ Error creating page {title}: {e}")
            )
            return None

    def _get_about_body(self, lang_code):
        """Get about page body content for each language."""
        bodies = {
            "it": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": """<p><b>MOTO CLUB CASTELLAZZO BORMIDA</b></p>
<h3><b>Passione, moto e territorio</b></h3>
<p>L'associazione motociclistica castellazzese, nata la sera del 16 marzo 1933 per l'iniziativa del dott. Marco Re, elegge a sua patrona la "Vergine Santissima della Creta e delle Grazie" collocando nella propria sede l'immagine donata dal Rettore del Santuario.</p>
<p>Oggi il Moto Club conta circa 200 soci ed è iscritto al CONI e alla Federazione Motociclistica Italiana; partecipa a diversi eventi motociclistici di tipo turistico a livello Regionali e Nazionali ed Internazionale utilizzando la motocicletta come il mezzo per divulgare messaggi di pace e fratellanza tra i popoli.</p>""",
                                        }
                                    ],
                                    "settings": {
                                        "custom_id": "",
                                        "custom_template": "",
                                        "custom_css_class": "",
                                        "column_breakpoint": "md",
                                    },
                                    "column_size": "",
                                },
                            }
                        ],
                        "settings": {
                            "custom_id": "",
                            "custom_template": "",
                            "custom_css_class": "",
                        },
                    },
                }
            ],
            "en": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": """<p><b>MOTO CLUB CASTELLAZZO BORMIDA</b></p>
<h3><b>Passion, motorcycles and territory</b></h3>
<p>The Castellazzo motorcycle association, founded on the evening of March 16, 1933, on the initiative of Dr. Marco Re, elected the "Most Holy Virgin of Creta and Graces" as its patron saint, placing in its headquarters the image donated by the Rector of the Sanctuary.</p>
<p>Today, the Moto Club has approximately 200 members and is registered with the Italian National Olympic Committee (CONI) and the Italian Motorcycling Federation; it participates in various tourist-type motorcycle events at the Regional, National, and International levels, using the motorcycle as a means to spread messages of peace and brotherhood among peoples.</p>""",
                                        }
                                    ],
                                    "settings": {
                                        "custom_id": "",
                                        "custom_template": "",
                                        "custom_css_class": "",
                                        "column_breakpoint": "md",
                                    },
                                    "column_size": "",
                                },
                            }
                        ],
                        "settings": {
                            "custom_id": "",
                            "custom_template": "",
                            "custom_css_class": "",
                        },
                    },
                }
            ],
            "fr": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": """<p><b>MOTO CLUB CASTELLAZZO BORMIDA</b></p>
<h3><b>Passion, motos et territoire</b></h3>
<p>L'association motocycliste de Castellazzo, née le soir du 16 mars 1933 à l'initiative du Dr Marco Re, choisit comme patronne la « Vierge Marie Très Sainte de la Creta et des Grâces » en plaçant dans son siège l'image donnée par le Recteur du Sanctuaire.</p>
<p>Aujourd'hui, le Moto Club compte environ 200 membres et est inscrit au CONI et à la Fédération Motocycliste Italienne ; il participe à divers événements motocyclistes de type touristique au niveau régional, national et international en utilisant la moto comme moyen de diffuser des messages de paix et de fraternité entre les peuples.</p>""",
                                        }
                                    ],
                                    "settings": {
                                        "custom_id": "",
                                        "custom_template": "",
                                        "custom_css_class": "",
                                        "column_breakpoint": "md",
                                    },
                                    "column_size": "",
                                },
                            }
                        ],
                        "settings": {
                            "custom_id": "",
                            "custom_template": "",
                            "custom_css_class": "",
                        },
                    },
                }
            ],
        }
        return bodies.get(lang_code, bodies["it"])

    def create_navbars(self):
        """Create navbar snippets for all locales."""
        it_locale = Locale.objects.get(language_code="it")
        en_locale = Locale.objects.get(language_code="en")
        fr_locale = Locale.objects.get(language_code="fr")

        # Italian navbar
        navbar_it = self._create_or_get_navbar(
            "NavBar Italiano",
            it_locale,
            [
                {"type": "link", "value": {"button_title": "Home", "page_link": None, "other_link": "/"}},
                {"type": "link", "value": {"button_title": "La nostra associazione", "page_link": None, "other_link": "/la-nostra-associazione/"}},
                {"type": "link", "value": {"button_title": "Eventi", "page_link": None, "other_link": "/incontriamoci/"}},
                {"type": "link", "value": {"button_title": "Contatti", "page_link": None, "other_link": "/contatti/"}},
            ],
        )

        # English navbar
        navbar_en = self._create_or_get_navbar(
            "NavBar Inglese",
            en_locale,
            [
                {"type": "link", "value": {"button_title": "Home", "page_link": None, "other_link": "/en/"}},
                {"type": "link", "value": {"button_title": "Our association", "page_link": None, "other_link": "/en/our-association/"}},
                {"type": "link", "value": {"button_title": "Events", "page_link": None, "other_link": "/en/lets-get-together/"}},
                {"type": "link", "value": {"button_title": "Contact Us", "page_link": None, "other_link": "/en/contact-us/"}},
            ],
            translation_of=navbar_it,
        )

        # French navbar
        navbar_fr = self._create_or_get_navbar(
            "NavBar Francese",
            fr_locale,
            [
                {"type": "link", "value": {"button_title": "Home", "page_link": None, "other_link": "/fr/"}},
                {"type": "link", "value": {"button_title": "Notre association", "page_link": None, "other_link": "/fr/notre-association/"}},
                {"type": "link", "value": {"button_title": "Événements", "page_link": None, "other_link": "/fr/rencontrons-nous/"}},
                {"type": "link", "value": {"button_title": "Contacts", "page_link": None, "other_link": "/fr/contacts/"}},
            ],
            translation_of=navbar_it,
        )

    def _create_or_get_navbar(self, name, locale, menu_items, translation_of=None):
        """Create or get a navbar snippet."""
        try:
            existing = Navbar.objects.filter(name=name, locale=locale).first()
            if existing:
                self.stdout.write(f"  • Navbar exists: {name}")
                return existing

            navbar = Navbar(
                name=name,
                locale=locale,
                menu_items=menu_items,
            )

            if translation_of:
                navbar.translation_key = translation_of.translation_key

            navbar.save()
            self.stdout.write(f"  ✓ Created navbar: {name}")
            return navbar

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error creating navbar: {e}"))
            return None

    def create_footers(self):
        """Create footer snippets for all locales."""
        it_locale = Locale.objects.get(language_code="it")
        en_locale = Locale.objects.get(language_code="en")
        fr_locale = Locale.objects.get(language_code="fr")

        footer_content = {
            "it": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": "<p>© 2025 MC Castellazzo Bormida - Tutti i diritti riservati</p>",
                                        }
                                    ],
                                    "column_size": "",
                                },
                            }
                        ],
                    },
                }
            ],
            "en": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": "<p>© 2025 MC Castellazzo Bormida - All rights reserved</p>",
                                        }
                                    ],
                                    "column_size": "",
                                },
                            }
                        ],
                    },
                }
            ],
            "fr": [
                {
                    "type": "row",
                    "value": {
                        "fluid": False,
                        "content": [
                            {
                                "type": "content",
                                "value": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": "<p>© 2025 MC Castellazzo Bormida - Tous droits réservés</p>",
                                        }
                                    ],
                                    "column_size": "",
                                },
                            }
                        ],
                    },
                }
            ],
        }

        # Italian footer
        footer_it = self._create_or_get_footer(
            "Footer Italiano", it_locale, footer_content["it"]
        )

        # English footer
        footer_en = self._create_or_get_footer(
            "Footer Inglese", en_locale, footer_content["en"], translation_of=footer_it
        )

        # French footer
        footer_fr = self._create_or_get_footer(
            "Footer Francese", fr_locale, footer_content["fr"], translation_of=footer_it
        )

    def _create_or_get_footer(self, name, locale, content, translation_of=None):
        """Create or get a footer snippet."""
        try:
            existing = Footer.objects.filter(name=name, locale=locale).first()
            if existing:
                self.stdout.write(f"  • Footer exists: {name}")
                return existing

            footer = Footer(
                name=name,
                locale=locale,
                content=content,
            )

            if translation_of:
                footer.translation_key = translation_of.translation_key

            footer.save()
            self.stdout.write(f"  ✓ Created footer: {name}")
            return footer

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error creating footer: {e}"))
            return None
