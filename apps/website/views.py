"""
Views for the website app.

mccastellazzob.com - Moto Club Castellazzo Bormida
Views custom per ricerca localizzata e altre funzionalità.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.translation import get_language
from wagtail.models import Locale
from wagtail.models import Page

from apps.core.validators import validate_search_query


if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse


def localized_search(request: HttpRequest) -> HttpResponse:
    """
    Ricerca contenuti filtrata per lingua corrente.

    Esegue una ricerca full-text sulle pagine Wagtail,
    filtrando per la lingua attiva e paginando i risultati.

    Args:
        request: HttpRequest con parametri 'q' (query) e 'page' (pagina).

    Returns:
        HttpResponse con template di ricerca renderizzato.

    Note:
        - Valida la query per prevenire attacchi ReDoS
        - Supporta fallback se locale non trovata
        - Paginazione a 20 risultati per pagina
    """
    # Ottieni e valida la query
    raw_query = request.GET.get("q", "")
    try:
        query = validate_search_query(raw_query)
    except Exception:
        query = ""

    search_results = Page.objects.none()

    if query:
        # Ottieni locale corrente
        current_language = get_language() or "it"

        try:
            locale = Locale.objects.get(language_code=current_language)
            search_results = (
                Page.objects.live().filter(locale=locale).search(query, operator="and")
            )
        except Locale.DoesNotExist:
            # Fallback: ricerca senza filtro locale
            search_results = Page.objects.live().search(query, operator="and")

    # Paginazione
    paginator = Paginator(search_results, 20)
    page_number = request.GET.get("page", 1)

    try:
        search_results_page = paginator.page(page_number)
    except PageNotAnInteger:
        search_results_page = paginator.page(1)
    except EmptyPage:
        search_results_page = paginator.page(paginator.num_pages)

    context = {
        "query": query,
        "search_results": search_results_page,
        "total_count": paginator.count,
    }

    return render(request, "website/search.html", context)
