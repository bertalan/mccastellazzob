"""
MC Castellazzo - Gallery Page Model
====================================
Pagina galleria fotografica con filtri categoria.
schema.org ImageGallery
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable

from apps.core.schema import SchemaOrgMixin
from apps.website.blocks import GalleryBlock


class GalleryImage(Orderable):
    """
    Immagine singola della galleria con categoria.
    Usato con InlinePanel per upload multiplo.
    """
    page = ParentalKey(
        "GalleryPage",
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Immagine"),
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Didascalia"),
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ("all", _("Tutti")),
            ("raduni", _("Raduni")),
            ("escursioni", _("Escursioni")),
            ("gare", _("Gare")),
            ("sociali", _("Eventi Sociali")),
        ],
        default="all",
        verbose_name=_("Categoria"),
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
        FieldPanel("category"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Immagine Galleria")
        verbose_name_plural = _("Immagini Galleria")


class GalleryPage(SchemaOrgMixin, Page):
    """
    Pagina Galleria Fotografica - schema.org ImageGallery.
    Supporta upload multiplo tramite InlinePanel.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    show_filters = models.BooleanField(
        default=True,
        verbose_name=_("Mostra filtri categoria"),
    )
    
    columns = models.CharField(
        max_length=20,
        choices=[
            ("2", _("2 colonne")),
            ("3", _("3 colonne")),
            ("4", _("4 colonne")),
        ],
        default="4",
        verbose_name=_("Colonne"),
    )
    
    # StreamField per compatibilità con blocchi esistenti
    gallery = StreamField(
        [
            ("gallery", GalleryBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Gallerie (blocchi)"),
        help_text=_("Opzionale: usa i blocchi o le immagini sotto"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/gallery_page.jinja2"
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("show_filters"),
                FieldPanel("columns"),
            ],
            heading=_("Impostazioni Galleria"),
        ),
        InlinePanel(
            "gallery_images",
            label=_("Immagini"),
            help_text=_("Trascina per riordinare. Puoi selezionare più immagini dalla libreria."),
        ),
        FieldPanel("gallery"),
    ]
    
    class Meta:
        verbose_name = _("Galleria")
        verbose_name_plural = _("Gallerie")
    
    # === Helper Methods ===
    def get_all_images(self):
        """Restituisce tutte le immagini (InlinePanel + StreamField)."""
        images = []
        
        # Immagini da InlinePanel
        for img in self.gallery_images.all():
            images.append({
                "image": img.image,
                "caption": img.caption,
                "category": img.category,
            })
        
        # Immagini da StreamField (compatibilità)
        for block in self.gallery:
            if block.block_type == "gallery":
                for img in block.value.get("images", []):
                    if img.get("image"):
                        images.append({
                            "image": img["image"],
                            "caption": img.get("caption", ""),
                            "category": img.get("category", "all"),
                        })
        
        return images
    
    def get_categories(self):
        """Restituisce le categorie presenti nelle immagini."""
        categories = set()
        for img in self.get_all_images():
            if img.get("category") and img["category"] != "all":
                categories.add(img["category"])
        return sorted(categories)
    
    # === Schema.org Methods ===
    def get_schema_org_type(self) -> str:
        return "ImageGallery"
    
    def get_schema_org_data(self) -> dict:
        images = []
        for img in self.get_all_images():
            if img.get("image"):
                images.append({
                    "@type": "ImageObject",
                    "contentUrl": img["image"].get_rendition("original").url,
                    "caption": img.get("caption", ""),
                })
        
        return {
            "name": self.title,
            "description": self.intro if self.intro else "",
            "image": images,
        }
