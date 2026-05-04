"""
Test per apps.website.services.archive.archive_past_events.
"""
import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.website.services.archive import archive_past_events


@pytest.fixture
def events_tree(site):
    """Crea EventsPage + EventsArchivePage figli della homepage."""
    from apps.website.models.events import EventsPage, EventsArchivePage, EventDetailPage

    home = site.root_page.specific
    suffix = uuid.uuid4().hex[:8]
    events_page = EventsPage(title="Eventi Test", slug=f"eventi-test-{suffix}")
    home.add_child(instance=events_page)
    archive_page = EventsArchivePage(
        title="Archivio Test", slug=f"archivio-test-{suffix}"
    )
    home.add_child(instance=archive_page)
    return events_page, archive_page, EventDetailPage


@pytest.mark.django_db
def test_archive_past_events_moves_only_past(events_tree):
    events_page, archive_page, EventDetailPage = events_tree
    now = timezone.now()
    s = uuid.uuid4().hex[:6]

    past = EventDetailPage(
        title=f"Past-{s}",
        slug=f"past-{s}",
        event_name="Past",
        start_date=now - timedelta(days=10),
        end_date=now - timedelta(days=9),
        location_name="X",
    )
    events_page.add_child(instance=past)

    future = EventDetailPage(
        title=f"Future-{s}",
        slug=f"future-{s}",
        event_name="Future",
        start_date=now + timedelta(days=10),
        location_name="X",
    )
    events_page.add_child(instance=future)

    result = archive_past_events(dry_run=False)

    assert result.moved >= 1
    past.refresh_from_db()
    future.refresh_from_db()
    assert past.get_parent().id == archive_page.id
    assert future.get_parent().id == events_page.id


@pytest.mark.django_db
def test_archive_past_events_idempotent(events_tree):
    events_page, archive_page, EventDetailPage = events_tree
    now = timezone.now()
    s = uuid.uuid4().hex[:6]

    past = EventDetailPage(
        title=f"Past2-{s}",
        slug=f"past2-{s}",
        event_name="Past2",
        start_date=now - timedelta(days=20),
        end_date=now - timedelta(days=19),
        location_name="X",
    )
    events_page.add_child(instance=past)

    first = archive_past_events(dry_run=False)
    second = archive_past_events(dry_run=False)

    assert first.moved >= 1
    # secondo run: il nostro past già archiviato deve essere skipped
    assert second.moved == 0
    assert second.skipped_already_archived >= 1
    past.refresh_from_db()
    assert past.get_parent().id == archive_page.id


@pytest.mark.django_db
def test_archive_past_events_dry_run(events_tree):
    events_page, archive_page, EventDetailPage = events_tree
    now = timezone.now()
    s = uuid.uuid4().hex[:6]

    past = EventDetailPage(
        title=f"PastDry-{s}",
        slug=f"past-dry-{s}",
        event_name="PastDry",
        start_date=now - timedelta(days=5),
        end_date=now - timedelta(days=4),
        location_name="X",
    )
    events_page.add_child(instance=past)

    result = archive_past_events(dry_run=True)

    assert result.candidates >= 1
    assert result.moved == 0
    past.refresh_from_db()
    assert past.get_parent().id == events_page.id


@pytest.mark.django_db
def test_archive_past_events_dry_run_is_default(events_tree):
    """SAFETY: chiamare archive_past_events() senza args non deve modificare nulla."""
    events_page, archive_page, EventDetailPage = events_tree
    now = timezone.now()
    s = uuid.uuid4().hex[:6]

    past = EventDetailPage(
        title=f"SafeDefault-{s}",
        slug=f"safe-default-{s}",
        event_name="SafeDefault",
        start_date=now - timedelta(days=30),
        end_date=now - timedelta(days=29),
        location_name="X",
    )
    events_page.add_child(instance=past)

    result = archive_past_events()  # default = dry_run=True

    assert result.moved == 0
    assert result.candidates >= 1
    past.refresh_from_db()
    assert past.get_parent().id == events_page.id


@pytest.mark.django_db
def test_archive_past_events_grace_days(events_tree):
    events_page, archive_page, EventDetailPage = events_tree
    now = timezone.now()
    s = uuid.uuid4().hex[:6]

    just_ended = EventDetailPage(
        title=f"JustEnded-{s}",
        slug=f"just-ended-{s}",
        event_name="JustEnded",
        start_date=now - timedelta(hours=2),
        end_date=now - timedelta(hours=1),
        location_name="X",
    )
    events_page.add_child(instance=just_ended)

    # Default grace_days=1: evento finito 1h fa NON viene archiviato
    result = archive_past_events(dry_run=False)
    just_ended.refresh_from_db()
    assert just_ended.get_parent().id == events_page.id

    # grace_days=0: archivia anche eventi appena finiti
    result = archive_past_events(dry_run=False, grace_days=0)
    just_ended.refresh_from_db()
    assert just_ended.get_parent().id == archive_page.id
