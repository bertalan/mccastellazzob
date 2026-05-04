"""
Helper per archiviare gli EventDetailPage passati.

Espone `archive_past_events()` chiamata sia dal management command
che dal middleware "lazy daily" (apps.core.daily_tasks).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ArchiveResult:
    moved: int = 0
    candidates: int = 0
    skipped_no_archive: int = 0
    skipped_already_archived: int = 0


def archive_past_events(*, dry_run: bool = True, grace_days: int = 1) -> ArchiveResult:
    """
    Sposta sotto la rispettiva EventsArchivePage del locale tutti gli
    EventDetailPage la cui end_date (o start_date se end_date è None)
    è precedente a `now - grace_days`.

    SAFE-BY-DEFAULT: ``dry_run=True`` di default. Per eseguire davvero gli
    spostamenti, passare esplicitamente ``dry_run=False``.

    Idempotente: salta gli eventi già figli di un EventsArchivePage.
    """
    # Import locale per evitare AppRegistryNotReady
    from apps.website.models.events import EventDetailPage, EventsArchivePage

    now = timezone.now()
    cutoff = now - timezone.timedelta(days=grace_days)
    result = ArchiveResult()

    archives = {a.locale_id: a for a in EventsArchivePage.objects.all()}
    if not archives:
        logger.warning("archive_past_events: nessuna EventsArchivePage configurata")
        return result

    archive_ids = {a.id for a in archives.values()}
    candidates: list[tuple] = []

    for evt in EventDetailPage.objects.all().select_related("locale"):
        ref = evt.end_date or evt.start_date
        if ref is None or ref >= cutoff:
            continue
        if evt.get_parent().id in archive_ids:
            result.skipped_already_archived += 1
            continue
        archive = archives.get(evt.locale_id)
        if archive is None:
            result.skipped_no_archive += 1
            continue
        candidates.append((evt, archive))

    result.candidates = len(candidates)

    if dry_run or not candidates:
        return result

    with transaction.atomic():
        for evt, archive in candidates:
            evt.move(archive, pos="last-child")
            result.moved += 1
            logger.info(
                "archive_past_events: moved id=%s '%s' (loc=%s) → archive id=%s",
                evt.id, evt.title, evt.locale.language_code, archive.id,
            )

    return result
