"""
MC Castellazzo - News Pages Models
===================================
Pagine Novità con:
- NewsIndexPage (indice articoli con ricerca)
- NewsPage (articolo singolo con galleria)

Ereditano da CodeRedCMS per sfruttare:
- Paginazione, filtri categoria, tags, autore, cover_image
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from coderedcms.blocks import CONTENT_STREAMBLOCKS
from coderedcms.models import CoderedArticleIndexPage, CoderedArticlePage

from apps.core.seo import JsonLdMixin, get_organization_data, clean_html
from apps.website.blocks import GalleryImageBlock


# Blocchi contenuto senza 'table' (richiede handsontable JS non installato)
NEWS_CONTENT_BLOCKS = [
    block for block in CONTENT_STREAMBLOCKS if block[0] != 'table'
]


class NewsIndexFeaturedPage(Orderable):
    """Pagine in evidenza selezionabili nell'indice novità."""
    
    page = ParentalKey(
        "website.NewsIndexPage",
        on_delete=models.CASCADE,
        related_name="featured_pages",
    )
    featured_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Pagina in evidenza"),
    )
    
    panels = [
        FieldPanel("featured_page"),
    ]
    
    class Meta:
        verbose_name = _("Pagina in evidenza")
        verbose_name_plural = _("Pagine in evidenza")


class NewsIndexPage(JsonLdMixin, CoderedArticleIndexPage):
    """
    Indice Novità - eredita tutto da CodeRedCMS.
    
    Features gratuite da CodeRedCMS:
    - Paginazione (index_num_per_page)
    - Filtro categorie (?c=slug)
    - Ordinamento (index_order_by)
    - Cover image
    
    Schema.org: CollectionPage con ItemList
    """
    
    class Meta:
        verbose_name = _("Indice Novità")
        verbose_name_plural = _("Indici Novità")
    
    template = "website/pages/news_index_page.jinja2"
    
    # Solo NewsPage come figli
    subpage_types = ["website.NewsPage"]
    
    # Può stare sotto HomePage
    parent_page_types = ["website.HomePage"]
    
    # Pannelli admin - aggiungiamo le pagine in evidenza
    content_panels = CoderedArticleIndexPage.content_panels + [
        MultiFieldPanel(
            [InlinePanel("featured_pages", label=_("Pagina"))],
            heading=_("Pagine in evidenza"),
        ),
    ]
    
    # =========================================================================
    # Schema.org CollectionPage + ItemList
    # =========================================================================
    
    def get_json_ld_type(self) -> str:
        return "CollectionPage"
    
    def _get_item_schema(self, page) -> dict:
        """
        Genera lo schema.org corretto in base al tipo di pagina.
        
        Supporta:
        - NewsPage → Article
        - EventDetailPage → Event
        - Altre pagine → WebPage
        """
        from apps.website.models.events import EventDetailPage
        
        # EventDetailPage → Event schema
        if isinstance(page, EventDetailPage):
            event_data = {
                "@type": "Event",
                "name": page.event_name or page.title,
                "url": page.full_url,
            }
            if page.start_date:
                event_data["startDate"] = page.start_date.isoformat()
            if page.end_date:
                event_data["endDate"] = page.end_date.isoformat()
            if page.location_name:
                event_data["location"] = {
                    "@type": "Place",
                    "name": page.location_name,
                }
                if page.location_address:
                    event_data["location"]["address"] = page.location_address
            if page.cover_image:
                try:
                    rendition = page.cover_image.get_rendition("fill-400x300")
                    event_data["image"] = rendition.full_url if hasattr(rendition, 'full_url') else rendition.url
                except Exception:
                    pass
            return event_data
        
        # NewsPage → Article schema
        if isinstance(page, NewsPage):
            article_data = {
                "@type": "Article",
                "headline": page.title,
                "url": page.full_url,
            }
            if page.date_display:
                article_data["datePublished"] = page.date_display.isoformat()
            if page.cover_image:
                try:
                    rendition = page.cover_image.get_rendition("fill-400x300")
                    article_data["image"] = rendition.full_url if hasattr(rendition, 'full_url') else rendition.url
                except Exception:
                    pass
            return article_data
        
        # Default → WebPage
        return {
            "@type": "WebPage",
            "name": page.title,
            "url": page.full_url,
        }
    
    def get_json_ld_data(self, request=None) -> dict:
        """
        Genera JSON-LD per l'indice articoli.
        
        Schema.org: CollectionPage con ItemList contenente articoli ed eventi.
        Rileva automaticamente il tipo di ogni risultato (Article, Event, WebPage).
        """
        # Ottieni gli articoli figli live
        articles = NewsPage.objects.child_of(self).live().public().order_by(
            '-first_published_at'
        )[:50]  # Limita a 50 per performance
        
        items = []
        position = 1
        
        for page in articles:
            item_data = {
                "@type": "ListItem",
                "position": position,
                "item": self._get_item_schema(page),
            }
            items.append(item_data)
            position += 1
        
        org = get_organization_data(self)
        
        return {
            "name": self.title,
            "description": clean_html(self.search_description or ""),
            "url": self.full_url,
            "publisher": {
                "@type": "Organization",
                "name": org.get("name", ""),
                "logo": org.get("logo"),
            },
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(items),
                "itemListElement": items,
            },
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Tag recenti - da CodeRedCMS (articoli) e Eventi
        # Ordinati per ultima pubblicazione delle pagine che li usano
        from taggit.models import Tag
        from django.db.models import Count, Max, Q
        
        # Tag da articoli CodeRedCMS
        codered_tags = Tag.objects.filter(
            coderedcms_coderedtag_items__isnull=False,
            coderedcms_coderedtag_items__content_object__locale=self.locale,
        ).annotate(
            last_used=Max('coderedcms_coderedtag_items__content_object__last_published_at'),
            usage_count=Count('coderedcms_coderedtag_items')
        )
        
        # Tag da eventi (EventPageTag)
        from apps.website.models.events import EventPageTag
        event_tags = Tag.objects.filter(
            website_eventpagetag_items__isnull=False,
            website_eventpagetag_items__content_object__locale=self.locale,
        ).annotate(
            last_used=Max('website_eventpagetag_items__content_object__last_published_at'),
            usage_count=Count('website_eventpagetag_items')
        )
        
        # Unisci e ordina
        all_tags = list(codered_tags) + list(event_tags)
        # Rimuovi duplicati mantenendo quello con last_used più recente
        seen = {}
        for tag in all_tags:
            if tag.slug not in seen or (tag.last_used and (not seen[tag.slug].last_used or tag.last_used > seen[tag.slug].last_used)):
                seen[tag.slug] = tag
        recent_tags = sorted(seen.values(), key=lambda t: (t.last_used or '', -t.usage_count), reverse=True)[:5]
        context["recent_tags"] = recent_tags
        
        # Filtra per tag se richiesto
        tag_slug = request.GET.get("tag", "").strip()
        if tag_slug:
            # Rimuovi eventuale # iniziale
            tag_slug = tag_slug.lstrip('#')
            context["active_tag"] = tag_slug
            context["is_search"] = True  # Nascondi articoli normali quando si filtra per tag
            
            # Cerca pagine con questo tag (articoli CodeRedCMS)
            from wagtail.models import Page
            from coderedcms.models import CoderedPage
            
            # Pagine CodeRedCMS con questo tag
            codered_results = CoderedPage.objects.live().public().filter(
                locale=self.locale,
                tags__slug=tag_slug
            )[:12]
            
            # Eventi con questo tag
            from apps.website.models.events import EventDetailPage
            event_results = EventDetailPage.objects.live().public().filter(
                locale=self.locale,
                tags__slug=tag_slug
            )[:12]
            
            # Combina risultati
            all_results = list(codered_results) + list(event_results)
            context["global_search_results"] = [p.specific for p in all_results[:12]]
            context["search_query"] = f"#{tag_slug}"
        
        # Ricerca testuale
        query = request.GET.get("q", "").strip()
        if query:
            from wagtail.models import Page
            from apps.website.models.events import EventDetailPage
            import re
            
            # Ottieni il locale corrente della pagina
            current_locale = self.locale
            
            # Parse query: virgola o | = OR, spazi = AND
            # Esempio: "moto,bici" -> OR, "moto bici" -> AND
            def parse_search_terms(q):
                """Ritorna (terms, is_or_search)"""
                # Controlla se contiene , o |
                if ',' in q or '|' in q:
                    # OR search
                    terms = [t.strip() for t in re.split(r'[,|]', q) if t.strip()]
                    return terms, True
                else:
                    # AND search (spazi)
                    terms = [t.strip() for t in q.split() if t.strip()]
                    return terms, False
            
            terms, is_or = parse_search_terms(query)
            
            def build_q_filter(terms, is_or, fields):
                """Costruisce Q filter per i campi specificati"""
                if not terms:
                    return Q()
                
                term_queries = []
                for term in terms:
                    # Per ogni termine, cerca in tutti i campi (OR tra campi)
                    field_q = Q()
                    for field in fields:
                        field_q |= Q(**{f"{field}__icontains": term})
                    term_queries.append(field_q)
                
                # Combina i termini con AND o OR
                if is_or:
                    result = Q()
                    for tq in term_queries:
                        result |= tq
                else:
                    result = Q()
                    for tq in term_queries:
                        result &= tq
                    # Se result è vuoto, inizializza col primo
                    if term_queries:
                        result = term_queries[0]
                        for tq in term_queries[1:]:
                            result &= tq
                
                return result
            
            # Ricerca in tutte le pagine (titolo)
            page_q = build_q_filter(terms, is_or, ['title'])
            page_results = list(
                Page.objects.live().public()
                .filter(locale=current_locale)
                .filter(page_q)
                .distinct()[:12]
            )
            
            # Ricerca negli eventi (più campi)
            event_q = build_q_filter(terms, is_or, ['title', 'event_name', 'location_name', 'location_address', 'description'])
            event_results = list(
                EventDetailPage.objects.live().public()
                .filter(locale=current_locale)
                .filter(event_q)
                .exclude(id__in=[p.id for p in page_results])
                .distinct()[:8]
            )
            
            # Combina i risultati (rimuovi duplicati)
            seen_ids = set()
            all_results = []
            for p in page_results + event_results:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    all_results.append(p)
            
            context["global_search_results"] = [p.specific for p in all_results[:12]]
            
            # Filtra anche i figli di questo indice
            if "index_children" in context:
                child_q = build_q_filter(terms, is_or, ['title'])
                try:
                    context["index_children"] = context["index_children"].filter(child_q)
                except Exception:
                    pass
            
            context["search_query"] = query
            context["is_search"] = True
        
        # Mostra pagine in evidenza SOLO se non c'è ricerca o filtro tag
        if not context.get("is_search"):
            context["featured_pages"] = [
                fp.featured_page.specific for fp in self.featured_pages.all()
            ]
            context["is_search"] = False
        
        return context


class NewsPage(JsonLdMixin, CoderedArticlePage):
    """
    Articolo Novità - eredita tutto da CodeRedCMS.
    
    Features gratuite da CodeRedCMS:
    - cover_image (foto principale)
    - author + author_display (autore)
    - date_display (data pubblicazione)
    - body (StreamField contenuto)
    - classifier_terms (categorie)
    - tags (tagging)
    - caption (sottotitolo)
    - related_show/related_num (articoli correlati)
    
    Aggiunto:
    - gallery (galleria immagini sfogliabile)
    """
    
    # Override body senza blocco 'table' (richiede handsontable JS)
    body = StreamField(
        NEWS_CONTENT_BLOCKS,
        blank=True,
        null=True,
        use_json_field=True,
        verbose_name=_("Contenuto"),
    )
    
    # Galleria immagini (stesso pattern degli Eventi)
    gallery = StreamField(
        [
            ("image", GalleryImageBlock()),
        ],
        blank=True,
        verbose_name=_("Galleria"),
        use_json_field=True,
    )
    
    # Search index
    search_fields = CoderedArticlePage.search_fields + [
        index.SearchField("gallery"),
    ]
    
    # Body panels - ereditiamo da CodeRedCMS e aggiungiamo galleria
    body_content_panels = CoderedArticlePage.body_content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("gallery"),
            ],
            heading=_("Galleria"),
        ),
    ]
    
    # Content panels - ereditiamo tutto da CodeRedCMS
    content_panels = CoderedArticlePage.content_panels
    
    class Meta:
        verbose_name = _("Articolo")
        verbose_name_plural = _("Articoli")
    
    template = "website/pages/news_page.jinja2"
    
    # Solo sotto NewsIndexPage
    parent_page_types = ["website.NewsIndexPage"]
    
    # Nessun figlio
    subpage_types = []
    
    # =========================================================================
    # Schema.org Article
    # =========================================================================
    
    def get_json_ld_type(self):
        return "Article"
    
    def get_json_ld_data(self, request=None):
        org = get_organization_data(self)
        
        data = {
            "@type": self.get_json_ld_type(),
            "headline": self.title,
            "datePublished": self.date_display.isoformat() if self.date_display else None,
            "dateModified": self.last_published_at.isoformat() if self.last_published_at else None,
            "author": {
                "@type": "Person",
                "name": self.author_display or (self.author.get_full_name() if self.author else None),
            },
            "publisher": {
                "@type": "Organization",
                "name": org.get("name", ""),
                "logo": org.get("logo"),
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
        }
        
        # Cover image
        if self.cover_image:
            rendition = self.cover_image.get_rendition("width-1200")
            data["image"] = {
                "@type": "ImageObject",
                "url": rendition.full_url if hasattr(rendition, 'full_url') else rendition.url,
                "width": rendition.width,
                "height": rendition.height,
            }
        
        # Descrizione
        if self.search_description:
            data["description"] = self.search_description
        
        # Categorie
        if self.classifier_terms.exists():
            data["articleSection"] = [term.name for term in self.classifier_terms.all()]
        
        # Tags
        if self.tags.exists():
            data["keywords"] = [tag.name for tag in self.tags.all()]
        
        return data
