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

from apps.core.seo import JsonLdMixin, clean_html, image_object
from apps.website.blocks import GalleryBlock, CollectionGalleryBlock


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
    title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Titolo"),
        help_text=_("Titolo dell'immagine (visibile nel lightbox)"),
    )
    caption = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Descrizione"),
        help_text=_("Descrizione dell'immagine (visibile nel lightbox)"),
    )
    category = models.ForeignKey(
        "website.GalleryCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Categoria"),
        help_text=_("Categoria per il filtro galleria"),
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("title"),
        FieldPanel("caption"),
        FieldPanel("category"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Immagine Galleria")
        verbose_name_plural = _("Immagini Galleria")


class GalleryPage(JsonLdMixin, Page):
    """
    Pagina Galleria Fotografica - schema.org ImageGallery.
    Supporta upload multiplo tramite InlinePanel.
    Supporta importazione automatica da Collection Wagtail.
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
    
    # StreamField con blocchi galleria e collezione
    gallery = StreamField(
        [
            ("gallery", GalleryBlock()),
            ("collection_gallery", CollectionGalleryBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Gallerie (blocchi)"),
        help_text=_("Usa blocchi immagine singola o importa da collezioni Wagtail"),
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
    def _get_source_gallery_blocks(self):
        """
        Restituisce i blocchi gallery dalla pagina sorgente se questa è una traduzione.
        Utile quando le traduzioni non hanno blocchi propri.
        """
        # Se questa pagina non ha blocchi gallery, prova a usare quelli della sorgente
        if not self.gallery or len(self.gallery) == 0:
            # Cerca la pagina sorgente (translation_key uguale, locale diversa)
            try:
                source_page = GalleryPage.objects.filter(
                    translation_key=self.translation_key
                ).exclude(id=self.id).first()
                
                if source_page and source_page.gallery:
                    return source_page.gallery
            except Exception:
                pass
        
        return self.gallery
    
    def get_gallery_sections(self):
        """
        Restituisce le sezioni della galleria con titoli e immagini.
        
        Ogni sezione ha:
        - id: slug univoco per anchor links
        - title: titolo della sezione (o nome collezione)
        - images: lista di immagini
        
        Returns:
            list[dict]: Lista di sezioni con id, title, images
        """
        from django.utils.text import slugify
        from wagtail.images import get_image_model
        Image = get_image_model()
        
        sections = []
        seen_image_ids = set()
        
        # 1. Sezione InlinePanel (se ha immagini)
        inline_images = []
        for img in self.gallery_images.all():
            inline_images.append({
                "image": img.image,
                "title": img.title or img.image.title or "",
                "caption": img.caption or "",
                "category": img.category,
            })
            seen_image_ids.add(img.image.id)
        
        if inline_images:
            sections.append({
                "id": "galleria-principale",
                "title": _("Galleria Principale"),
                "images": inline_images,
            })
        
        # 2. Sezioni da StreamField (usa sorgente se traduzione è vuota)
        gallery_blocks = self._get_source_gallery_blocks()
        for idx, block in enumerate(gallery_blocks):
            if block.block_type == "collection_gallery":
                collection_value = block.value.get("collection")
                block_category = block.value.get("category")
                block_title = block.value.get("title") or ""
                
                if collection_value:
                    # collection_value può essere un ID (int) o un oggetto Collection
                    from wagtail.models import Collection as WagtailCollection
                    if isinstance(collection_value, int):
                        try:
                            collection = WagtailCollection.objects.get(id=collection_value)
                        except WagtailCollection.DoesNotExist:
                            continue
                    else:
                        collection = collection_value
                    
                    section_images = []
                    collection_images = Image.objects.filter(
                        collection=collection
                    ).order_by("created_at")
                    
                    for img in collection_images:
                        if img.id in seen_image_ids:
                            continue
                        
                        tag_names = [tag.name for tag in img.tags.all()]
                        caption = ", ".join(tag_names) if tag_names else ""
                        
                        section_images.append({
                            "image": img,
                            "title": img.title or "",
                            "caption": caption,
                            "category": block_category,
                        })
                        seen_image_ids.add(img.id)
                    
                    if section_images:
                        # Usa il titolo del blocco, o il nome della collezione
                        title = block_title or collection.name
                        sections.append({
                            "id": slugify(title) or f"sezione-{idx}",
                            "title": title,
                            "images": section_images,
                        })
                        
            elif block.block_type == "gallery":
                section_images = []
                for img in block.value.get("images", []):
                    if img.get("image") and img["image"].id not in seen_image_ids:
                        section_images.append({
                            "image": img["image"],
                            "title": img.get("title") or "",
                            "caption": img.get("caption") or "",
                            "category": img.get("category"),
                        })
                        seen_image_ids.add(img["image"].id)
                
                if section_images:
                    sections.append({
                        "id": f"galleria-{idx}",
                        "title": _("Galleria"),
                        "images": section_images,
                    })
        
        return sections
    
    def get_all_images(self):
        """
        Restituisce tutte le immagini (InlinePanel + StreamField con Collection e Gallery).
        
        Ordine di precedenza:
        1. Immagini da InlinePanel (priorità alta, ordinate per sort_order)
        2. Immagini da StreamField (blocchi collection_gallery e gallery)
        
        Le immagini già presenti in InlinePanel non vengono duplicate.
        """
        from wagtail.images import get_image_model
        Image = get_image_model()
        
        images = []
        seen_image_ids = set()  # Per evitare duplicati
        
        # 1. Immagini da InlinePanel (priorità alta)
        for img in self.gallery_images.all():
            images.append({
                "image": img.image,
                "title": img.title or img.image.title or "",
                "caption": img.caption or "",
                "category": img.category,
            })
            seen_image_ids.add(img.image.id)
        
        # 2. Immagini da StreamField (usa sorgente se traduzione è vuota)
        gallery_blocks = self._get_source_gallery_blocks()
        for block in gallery_blocks:
            if block.block_type == "collection_gallery":
                # Blocco collezione: carica tutte le immagini dalla collection
                collection_value = block.value.get("collection")
                block_category = block.value.get("category")
                
                if collection_value:
                    # collection_value può essere un ID (int) o un oggetto Collection
                    from wagtail.models import Collection as WagtailCollection
                    if isinstance(collection_value, int):
                        try:
                            collection = WagtailCollection.objects.get(id=collection_value)
                        except WagtailCollection.DoesNotExist:
                            continue
                    else:
                        collection = collection_value
                    
                    collection_images = Image.objects.filter(
                        collection=collection
                    ).order_by("created_at")
                    
                    for img in collection_images:
                        # Salta se già presente
                        if img.id in seen_image_ids:
                            continue
                        
                        # Costruisci caption dai tag
                        tag_names = [tag.name for tag in img.tags.all()]
                        caption = ", ".join(tag_names) if tag_names else ""
                        
                        images.append({
                            "image": img,
                            "title": img.title or "",
                            "caption": caption,
                            "category": block_category,
                        })
                        seen_image_ids.add(img.id)
                        
            elif block.block_type == "gallery":
                # Blocco galleria legacy: immagini singole
                for img in block.value.get("images", []):
                    if img.get("image") and img["image"].id not in seen_image_ids:
                        images.append({
                            "image": img["image"],
                            "title": img.get("title") or "",
                            "caption": img.get("caption") or "",
                            "category": img.get("category"),
                        })
                        seen_image_ids.add(img["image"].id)
        
        return images
    
    def get_categories(self):
        """Restituisce le categorie uniche presenti nelle immagini."""
        categories = {}
        for img in self.get_all_images():
            cat = img.get("category")
            if cat and hasattr(cat, 'slug'):
                categories[cat.slug] = cat
        return sorted(categories.values(), key=lambda x: x.sort_order)
    
    def get_all_tags(self):
        """Restituisce tutti i tag unici dalle immagini della galleria."""
        from collections import Counter
        tag_counter = Counter()
        
        for img in self.get_all_images():
            image_obj = img.get("image")
            if image_obj and hasattr(image_obj, 'tags'):
                for tag in image_obj.tags.all():
                    tag_counter[tag.name] += 1
        
        # Restituisce lista di tuple (tag_name, count) ordinata per frequenza
        return tag_counter.most_common()
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "ImageGallery"
    
    def get_json_ld_data(self, request=None) -> dict:
        images = []
        for img in self.get_all_images():
            if img.get("image"):
                images.append(image_object(
                    url=img["image"].get_rendition("original").url,
                    caption=img.get("caption", ""),
                ))
        
        return {
            "name": self.title,
            "description": clean_html(self.intro) if self.intro else "",
            "image": images,
        }
