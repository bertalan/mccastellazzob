"""
Management command: sposta gli eventi passati sotto EventsArchivePage.

Wrapper attorno a `apps.website.services.archive.archive_past_events`.
La stessa logica viene invocata in modalità "lazy daily" dal middleware
`apps.core.daily_tasks.DailyTasksMiddleware` alla prima richiesta del giorno.

Uso manuale (DRY-RUN di default, mostra cosa farebbe senza modificare nulla):
    python manage.py archive_past_events                # anteprima
    python manage.py archive_past_events --execute      # esegui davvero
    python manage.py archive_past_events --execute --days-grace 0
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.website.services.archive import archive_past_events


class Command(BaseCommand):
    help = (
        "Sposta gli EventDetailPage passati sotto EventsArchivePage del rispettivo locale. "
        "DRY-RUN di default: usa --execute per applicare le modifiche."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Applica le modifiche. Senza questo flag il comando è solo un'anteprima.",
        )
        parser.add_argument("--days-grace", type=int, default=1)

    def handle(self, *args, **options):
        execute = options["execute"]
        dry_run = not execute
        result = archive_past_events(
            dry_run=dry_run,
            grace_days=options["days_grace"],
        )
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"[DRY-RUN] Da spostare: {result.candidates} | "
                f"già archiviati: {result.skipped_already_archived} | "
                f"senza archivio per locale: {result.skipped_no_archive}\n"
                f"Per applicare davvero, rilanciare con --execute."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Spostati: {result.moved} | "
                f"già archiviati: {result.skipped_already_archived} | "
                f"senza archivio per locale: {result.skipped_no_archive}"
            ))
