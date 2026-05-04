"""
DailyTasksMiddleware
====================
Esegue task quotidiani "pigri": alla prima richiesta del giorno (per processo)
acquisisce un lock atomico via cache e lancia i job in un thread di background,
così la response dell'utente non viene rallentata.

Lock chiave: ``daily_tasks:<task_name>:<YYYY-MM-DD>`` con TTL di ~26h.
Se la cache non è condivisa fra più worker (LocMemCache), ogni worker
proverà l'``add()`` ma solo il primo riuscirà sui backend condivisi
(database/file/redis); con LocMemCache nel peggior caso il job gira N volte
nello stesso giorno (idempotente, quindi è sicuro).

Per disabilitare: settare ``DAILY_TASKS_ENABLED = False`` nei settings.
"""
from __future__ import annotations

import logging
import threading

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

_LOCK_TTL_SECONDS = 26 * 3600  # 26h: copre il rollover di mezzanotte
_TASK_NAME = "archive_past_events"


def _run_archive_in_background():
    """Esegue il job in un thread, isolato da errori."""
    try:
        # Import locale per evitare circular import a startup
        from apps.website.services.archive import archive_past_events

        # Esecuzione reale: il default del servizio è dry_run=True (safe-by-default).
        result = archive_past_events(dry_run=False)
        logger.info(
            "DailyTasks[%s] done: moved=%s candidates=%s already_archived=%s no_archive=%s",
            _TASK_NAME, result.moved, result.candidates,
            result.skipped_already_archived, result.skipped_no_archive,
        )
    except Exception:  # noqa: BLE001
        logger.exception("DailyTasks[%s] failed", _TASK_NAME)


class DailyTasksMiddleware:
    """Trigger lazy dei job giornalieri al primo hit della giornata."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "DAILY_TASKS_ENABLED", True)

    def __call__(self, request):
        if self.enabled:
            self._maybe_trigger()
        return self.get_response(request)

    def _maybe_trigger(self):
        today = timezone.localdate().isoformat()
        cache_key = f"daily_tasks:{_TASK_NAME}:{today}"
        try:
            # cache.add() ritorna True solo se la chiave non esisteva → lock acquisito
            acquired = cache.add(cache_key, "1", timeout=_LOCK_TTL_SECONDS)
        except Exception:  # noqa: BLE001
            logger.exception("DailyTasksMiddleware: cache.add failed")
            return

        if not acquired:
            return

        logger.info("DailyTasks[%s] triggered for %s", _TASK_NAME, today)
        # Esegui in background per non rallentare la response
        thread = threading.Thread(
            target=_run_archive_in_background,
            name=f"daily-{_TASK_NAME}",
            daemon=True,
        )
        thread.start()
