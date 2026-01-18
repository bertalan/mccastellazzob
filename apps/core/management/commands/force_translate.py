"""
Management command per forzare la sincronizzazione e traduzione di tutte le pagine.

Uso:
    python manage.py force_translate              # Tutte le pagine
    python manage.py force_translate --page=3     # Solo pagina con ID 3
    python manage.py force_translate --slug=home  # Solo pagina con slug 'home'
    python manage.py force_translate --dry-run    # Mostra cosa farebbe senza modificare
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Locale
from wagtail_localize.models import TranslationSource, Translation, StringTranslation
from deep_translator import GoogleTranslator


class Command(BaseCommand):
    help = "Forza la sincronizzazione e traduzione di tutte le pagine"

    def add_arguments(self, parser):
        parser.add_argument(
            "--page",
            type=int,
            help="ID della pagina specifica da tradurre",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="Slug della pagina specifica da tradurre",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra cosa verrebbe fatto senza modificare",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Salta i segmenti già tradotti",
        )

    def handle(self, *args, **options):
        self.dry_run = options.get("dry_run", False)
        self.skip_existing = options.get("skip_existing", False)
        self.lang_map = {"fr": "fr", "en": "en", "de": "de", "es": "es"}
        self.target_locales = Locale.objects.exclude(language_code="it")

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("FORCE TRANSLATE - Sincronizzazione e Traduzione"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if self.dry_run:
            self.stdout.write(self.style.WARNING("MODALITÀ DRY-RUN: nessuna modifica verrà effettuata"))

        # Trova le pagine da tradurre
        source_locale = Locale.objects.get(language_code="it")

        if options.get("page"):
            pages = Page.objects.filter(id=options["page"])
        elif options.get("slug"):
            pages = Page.objects.filter(slug=options["slug"], locale=source_locale)
        else:
            # Tutte le pagine italiane (esclusa la root)
            pages = Page.objects.filter(locale=source_locale, depth__gte=2)

        self.stdout.write(f"\nPagine da processare: {pages.count()}")

        stats = {"sources_created": 0, "translations_created": 0, "segments_translated": 0, "pages_published": 0, "errors": 0}

        for page in pages:
            self.process_page(page.specific, stats)

        # Riepilogo
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("RIEPILOGO"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  TranslationSource create: {stats['sources_created']}")
        self.stdout.write(f"  Translation create: {stats['translations_created']}")
        self.stdout.write(f"  Segmenti tradotti: {stats['segments_translated']}")
        self.stdout.write(f"  Pagine pubblicate: {stats['pages_published']}")
        self.stdout.write(f"  Errori: {stats['errors']}")

    def process_page(self, page, stats):
        """Processa una singola pagina."""
        self.stdout.write(f"\n--- {page.title} (ID: {page.id}) ---")

        # 1. Crea o aggiorna TranslationSource
        source = self.ensure_translation_source(page, stats)
        if not source:
            return

        # 2. Crea Translation per ogni lingua mancante
        for locale in self.target_locales:
            translation = self.ensure_translation(source, page, locale, stats)
            if not translation:
                continue

            # 3. Traduci i segmenti
            self.translate_segments(source, translation, locale, stats)

            # 4. Pubblica la traduzione
            self.publish_translation(translation, stats)

    def ensure_translation_source(self, page, stats):
        """Assicura che esista una TranslationSource per la pagina."""
        try:
            source, created = TranslationSource.get_or_create_from_instance(page)
            if created:
                stats["sources_created"] += 1
                self.stdout.write(self.style.SUCCESS(f"  TranslationSource: CREATA"))
            else:
                # Aggiorna la source con i dati correnti
                if not self.dry_run:
                    source.update_from_db()
                self.stdout.write(f"  TranslationSource: già esistente (aggiornata)")
            return source
        except Exception as e:
            stats["errors"] += 1
            self.stdout.write(self.style.ERROR(f"  TranslationSource: ERRORE - {e}"))
            return None

    def ensure_translation(self, source, page, locale, stats):
        """Assicura che esista una Translation per la lingua."""
        # Verifica se esiste già la pagina tradotta
        translated_page = Page.objects.filter(
            translation_key=page.translation_key,
            locale=locale
        ).first()

        if not translated_page:
            self.stdout.write(f"    {locale.language_code.upper()}: Pagina tradotta non esiste, skip")
            return None

        # Trova o crea Translation
        translation = Translation.objects.filter(source=source, target_locale=locale).first()

        if not translation:
            if self.dry_run:
                self.stdout.write(f"    {locale.language_code.upper()}: Translation da creare")
                return None

            translation = Translation.objects.create(
                source=source,
                target_locale=locale,
            )
            stats["translations_created"] += 1
            self.stdout.write(self.style.SUCCESS(f"    {locale.language_code.upper()}: Translation CREATA"))

        return translation

    def translate_segments(self, source, translation, locale, stats):
        """Traduce i segmenti di testo."""
        target_lang = locale.language_code
        if target_lang not in self.lang_map:
            return

        segments = source.stringsegment_set.all()

        for segment in segments:
            string_obj = segment.string
            original_text = string_obj.data
            context = segment.context

            # Verifica se già tradotto
            existing = StringTranslation.objects.filter(
                translation_of=string_obj,
                locale=locale,
                context=context
            ).first()

            if existing:
                if self.skip_existing:
                    continue
                # Aggiorna traduzione esistente
                translated = self.translate_text(original_text, self.lang_map[target_lang])
                if translated and translated != existing.data:
                    if not self.dry_run:
                        existing.data = translated
                        existing.save()
                    stats["segments_translated"] += 1
            else:
                # Crea nuova traduzione
                translated = self.translate_text(original_text, self.lang_map[target_lang])
                if translated and translated != original_text:
                    # Fix per slug: rimuovi caratteri non validi
                    if context.path == "slug":
                        translated = self.sanitize_slug(translated)

                    if not self.dry_run:
                        StringTranslation.objects.create(
                            translation_of=string_obj,
                            locale=locale,
                            context=context,
                            data=translated,
                        )
                    stats["segments_translated"] += 1

    def translate_text(self, text, target):
        """Traduce il testo usando Google Translator."""
        if not text or len(text.strip()) < 2:
            return text
        try:
            return GoogleTranslator(source="it", target=target).translate(text)
        except Exception:
            return None

    def sanitize_slug(self, slug):
        """Rende lo slug valido per Wagtail."""
        import re
        from django.utils.text import slugify

        # Prima prova slugify standard
        sanitized = slugify(slug)
        if sanitized:
            return sanitized

        # Fallback: rimuovi caratteri non validi
        sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", slug.lower())
        return sanitized or "page"

    def publish_translation(self, translation, stats):
        """Pubblica la traduzione sulla pagina target."""
        if self.dry_run:
            self.stdout.write(f"    {translation.target_locale.language_code.upper()}: da pubblicare")
            return

        try:
            translation.save_target(publish=True)
            stats["pages_published"] += 1
            self.stdout.write(self.style.SUCCESS(f"    {translation.target_locale.language_code.upper()}: PUBBLICATA"))
        except Exception as e:
            stats["errors"] += 1
            self.stdout.write(self.style.ERROR(f"    {translation.target_locale.language_code.upper()}: ERRORE - {e}"))
