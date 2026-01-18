"""
MC Castellazzo - Website App Config
"""
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"
    verbose_name = "Sito Web"

    def ready(self):
        """
        Monkey patch per correggere il bug di CodeRedCMS Carousel con Wagtail 7.
        
        Il bug: CarouselSlide ha un campo StreamField (content) in un InlinePanel,
        che causa "MultiValueDictKeyError: 'carousel_slides-0-content-count'"
        quando si tenta di modificare un Carousel nell'admin.
        
        La soluzione: rimuovere il campo 'content' dai panels di CarouselSlide.
        Questo sacrifica la possibilità di aggiungere contenuti HTML nelle slide,
        ma permette di usare il Carousel per semplici immagini.
        """
        try:
            from coderedcms.models.snippet_models import CarouselSlide
            from wagtail.admin.panels import FieldPanel
            
            # Rimuovi il campo content problematico dai panels
            CarouselSlide.panels = [
                FieldPanel("image"),
                FieldPanel("background_color"),
                FieldPanel("custom_css_class"),
                FieldPanel("custom_id"),
                # FieldPanel("content"),  # RIMOSSO - causa bug con Wagtail 7
            ]
        except ImportError:
            pass  # CodeRedCMS non è installato
