"""
Management command per ritentare le traduzioni fallite/pendenti.

Le StringTranslation con `data=""` sono quelle che non sono state tradotte
(worker Gunicorn ucciso per timeout, rate limit, errore di rete, ecc.).

Uso:
    python manage.py retry_translations                  # tutte le lingue
    python manage.py retry_translations --locale=fr      # solo francese
    python manage.py retry_translations --max=50         # massimo 50 stringhe
    python manage.py retry_translations --dry-run        # mostra quante senza modificare

Cron (esempio ogni ora):
    0 * * * * /www/wwwroot/mccastellazzob.com/venv_new/bin/python \
              /www/wwwroot/mccastellazzob.com/app/manage.py retry_translations \
              --settings=mccastellazzob.settings.prod >> /var/log/retry_translations.log 2>&1
"""
from django.core.management.base import BaseCommand
from wagtail_localize.models import StringTranslation


class Command(BaseCommand):
    help = "Riprova le traduzioni pendenti (StringTranslation con data vuota)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--locale",
            type=str,
            help="Codice lingua target (es. fr, en, de, es). Ometti per tutte.",
        )
        parser.add_argument(
            "--max",
            type=int,
            default=200,
            help="Numero massimo di stringhe da tradurre per esecuzione (default: 200)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra quante stringhe pendenti ci sono senza tradurre",
        )

    def handle(self, *args, **options):
        locale_code = options.get("locale")
        max_strings = options.get("max", 200)
        dry_run = options.get("dry_run", False)

        qs = StringTranslation.objects.filter(data="")
        if locale_code:
            qs = qs.filter(locale__language_code=locale_code)

        count = qs.count()
        label = f"[{locale_code}]" if locale_code else "[tutte le lingue]"

        self.stdout.write(f"Stringhe pendenti {label}: {count}")

        if dry_run or count == 0:
            if count == 0:
                self.stdout.write(self.style.SUCCESS("Nessuna stringa pendente."))
            return

        self.stdout.write(f"Avvio traduzione (max {max_strings})…")

        from apps.core.machine_translator import translate_pending_segments
        stats = translate_pending_segments(locale_code=locale_code, max_strings=max_strings)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completato — tradotte: {stats['done']}, "
                f"saltate: {stats['skipped']}, "
                f"errori: {stats['errors']}"
            )
        )

        # Mostra quante rimangono
        remaining = StringTranslation.objects.filter(data="")
        if locale_code:
            remaining = remaining.filter(locale__language_code=locale_code)
        r = remaining.count()
        if r:
            self.stdout.write(
                self.style.WARNING(
                    f"Stringhe ancora pendenti {label}: {r} — "
                    f"riesegui `retry_translations` o aspetta il prossimo cron."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Tutte le stringhe {label} sono tradotte!"))
