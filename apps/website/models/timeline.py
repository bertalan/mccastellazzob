"""
MC Castellazzo - Timeline Page Model
=====================================
schema.org ItemList con articoli verticali.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.schema import SchemaOrgMixin, article
from apps.website.blocks import ArticleBlock


class TimelinePage(SchemaOrgMixin, Page):
    """
    Pagina Timeline - schema.org ItemList.
    
    StreamField con articoli ordinati per data (recenti in cima).
    Template verticale con scroll e hover su foto.
    """
    
    intro = models.TextField(
        _("Introduzione"),
        blank=True,
        help_text=_("Testo introduttivo per la pagina timeline"),
    )
    
    articles = StreamField(
        [
            ("article", ArticleBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Articoli"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/timeline_page.jinja2"
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("articles"),
    ]
    
    class Meta:
        verbose_name = _("Timeline")
        verbose_name_plural = _("Timeline")
    
    def get_articles_sorted(self):
        """Ritorna gli articoli ordinati per data (recenti in cima)."""
        articles_list = []
        for block in self.articles:
            if block.block_type == "article":
                articles_list.append(block.value)
        
        # Ordina per data decrescente
        return sorted(
            articles_list,
            key=lambda x: x.get("date_published") or "",
            reverse=True,
        )
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "ItemList"
    
    def get_schema_org_data(self) -> dict:
        items = []
        for idx, art in enumerate(self.get_articles_sorted(), start=1):
            item = article(
                headline=art.get("headline", ""),
                image_url=art.get("image").get_rendition("fill-800x600").url if art.get("image") else "",
                date_published=str(art.get("date_published", "")),
                article_section=art.get("article_section", ""),
                url=art.get("url", ""),
            )
            items.append({
                "@type": "ListItem",
                "position": idx,
                "item": item,
            })
        
        return {
            "name": self.title,
            "description": self.intro,
            "numberOfItems": len(items),
            "itemListElement": items,
        }
