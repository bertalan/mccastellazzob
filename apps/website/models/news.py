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
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from coderedcms.models import CoderedArticleIndexPage, CoderedArticlePage

from apps.core.seo import JsonLdMixin, get_organization_data, clean_html
from apps.website.blocks import GalleryImageBlock


class NewsIndexPage(CoderedArticleIndexPage):
    """
    Indice Novità - eredita tutto da CodeRedCMS.
    
    Features gratuite da CodeRedCMS:
    - Paginazione (index_num_per_page)
    - Filtro categorie (?c=slug)
    - Ordinamento (index_order_by)
    - Cover image
    """
    
    class Meta:
        verbose_name = _("Indice Novità")
        verbose_name_plural = _("Indici Novità")
    
    template = "website/pages/news_index_page.jinja2"
    
    # Solo NewsPage come figli
    subpage_types = ["website.NewsPage"]
    
    # Può stare sotto HomePage
    parent_page_types = ["website.HomePage"]
    
    # Override per aggiungere ricerca testuale
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Ricerca testuale
        query = request.GET.get("q", "").strip()
        if query and "index_children" in context:
            from wagtail.search.models import Query
            # Filtra i risultati per query
            context["index_children"] = context["index_children"].search(query)
            # Registra la query per analytics
            Query.get(query).add_hit()
            context["search_query"] = query
        
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
    
    # Pannelli admin
    content_panels = CoderedArticlePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("gallery"),
            ],
            heading=_("Galleria"),
        ),
    ]
    
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
    
    def get_json_ld_data(self):
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
