"""
MC Castellazzo - StreamField Blocks
====================================
Blocchi riutilizzabili per StreamField.
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


# =============================================================================
# HERO BLOCKS
# =============================================================================

class HeroSlideBlock(blocks.StructBlock):
    """Singola slide dello slider hero."""
    image = ImageChooserBlock(label=_("Immagine"))
    title = blocks.CharBlock(label=_("Titolo"), max_length=100)
    category = blocks.CharBlock(
        label=_("Categoria"),
        max_length=50,
        required=False,
        help_text=_("Es: Raduni, Escursioni, Gare"),
    )
    link = blocks.URLBlock(label=_("Link"), required=False)

    class Meta:
        icon = "image"
        label = _("Slide")


class HeroSliderBlock(blocks.StructBlock):
    """Slider fotografico per homepage."""
    slides = blocks.ListBlock(
        HeroSlideBlock(),
        min_num=1,
        max_num=10,
        label=_("Slides"),
    )
    autoplay = blocks.BooleanBlock(
        label=_("Autoplay"),
        default=True,
        required=False,
    )
    interval = blocks.IntegerBlock(
        label=_("Intervallo (ms)"),
        default=5000,
        min_value=2000,
        max_value=15000,
    )
    height = blocks.ChoiceBlock(
        label=_("Altezza"),
        choices=[
            ("50vh", "50%"),
            ("75vh", "75%"),
            ("100vh", _("Schermo intero")),
        ],
        default="75vh",
    )

    class Meta:
        icon = "image"
        label = _("Slider Fotografico")
        template = "website/blocks/hero_slider_block.html"


class HeroCountdownBlock(blocks.StructBlock):
    """Hero con countdown per evento."""
    badge_text = blocks.CharBlock(
        label=_("Badge"),
        max_length=100,
        default="IL PIÙ ANTICO MOTO CLUB DEL PIEMONTE",
    )
    title = blocks.CharBlock(label=_("Titolo"), max_length=255)
    title_highlight = blocks.CharBlock(
        label=_("Parte evidenziata"),
        max_length=100,
        help_text=_("Testo in oro"),
    )
    subtitle = blocks.CharBlock(label=_("Sottotitolo"), max_length=500)

    # CTA buttons
    cta_primary_text = blocks.CharBlock(label=_("Testo CTA primario"), max_length=50)
    cta_primary_link = blocks.URLBlock(label=_("Link CTA primario"))
    cta_secondary_text = blocks.CharBlock(
        label=_("Testo CTA secondario"),
        max_length=50,
        required=False,
    )
    cta_secondary_link = blocks.URLBlock(
        label=_("Link CTA secondario"),
        required=False,
    )

    # Featured event
    event = blocks.PageChooserBlock(
        label=_("Evento in evidenza"),
        page_type="website.EventDetailPage",
        required=False,
    )
    show_countdown = blocks.BooleanBlock(
        label=_("Mostra countdown"),
        default=True,
        required=False,
    )

    class Meta:
        icon = "date"
        label = _("Hero con Countdown")
        template = "website/blocks/hero_countdown_block.jinja2"


# =============================================================================
# STATS BLOCKS
# =============================================================================

class StatItemBlock(blocks.StructBlock):
    """Singola statistica."""
    icon = blocks.CharBlock(
        label=_("Icona FontAwesome"),
        max_length=50,
        default="fas fa-star",
        help_text=_("Classe FontAwesome, es: fas fa-calendar-alt"),
    )
    icon_bg_color = blocks.ChoiceBlock(
        label=_("Colore sfondo icona"),
        choices=[
            ("bg-gold", _("Oro")),
            ("bg-bordeaux", _("Bordeaux")),
            ("bg-navy", _("Navy")),
            ("bg-amaranth", _("Amaranto")),
        ],
        default="bg-gold",
    )
    value = blocks.CharBlock(label=_("Valore"), max_length=20)
    label = blocks.CharBlock(label=_("Etichetta"), max_length=50)

    class Meta:
        icon = "order"
        label = _("Statistica")


class StatsBlock(blocks.StructBlock):
    """Sezione statistiche."""
    stats = blocks.ListBlock(
        StatItemBlock(),
        min_num=2,
        max_num=6,
        label=_("Statistiche"),
    )
    background = blocks.ChoiceBlock(
        label=_("Sfondo"),
        choices=[
            ("bg-white", _("Bianco")),
            ("bg-cream", _("Crema")),
            ("bg-navy", _("Navy")),
        ],
        default="bg-white",
    )

    class Meta:
        icon = "order"
        label = _("Statistiche")
        template = "website/blocks/stats_block.html"


# =============================================================================
# SECTION CARDS BLOCKS
# =============================================================================

class SectionCardBlock(blocks.StructBlock):
    """Card per sezione del sito."""
    title = blocks.CharBlock(label=_("Titolo"), max_length=100)
    description = blocks.TextBlock(label=_("Descrizione"))
    image = ImageChooserBlock(label=_("Immagine di sfondo"))
    icon = blocks.CharBlock(
        label=_("Icona"),
        max_length=50,
        default="fas fa-arrow-right",
    )
    icon_bg_color = blocks.ChoiceBlock(
        label=_("Colore icona"),
        choices=[
            ("bg-gold text-navy", _("Oro")),
            ("bg-bordeaux text-white", _("Bordeaux")),
            ("bg-navy text-gold", _("Navy")),
            ("bg-amaranth text-white", _("Amaranto")),
            ("bg-white text-amaranth", _("Bianco")),
        ],
        default="bg-gold text-navy",
    )
    link_page = blocks.PageChooserBlock(label=_("Pagina collegata"))
    link_text = blocks.CharBlock(
        label=_("Testo link"),
        max_length=50,
        default="Scopri di più",
    )
    link_color = blocks.ChoiceBlock(
        label=_("Colore link"),
        choices=[
            ("text-gold", _("Oro")),
            ("text-bordeaux", _("Bordeaux")),
            ("text-navy", _("Navy")),
            ("text-amaranth", _("Amaranto")),
        ],
        default="text-gold",
    )

    class Meta:
        icon = "doc-full"
        label = _("Card Sezione")
        template = "website/blocks/section_card_block.html"


class SectionCardsGridBlock(blocks.StructBlock):
    """Griglia di cards sezione."""
    heading_label = blocks.CharBlock(
        label=_("Etichetta intestazione"),
        max_length=50,
        required=False,
    )
    heading_title = blocks.CharBlock(
        label=_("Titolo"),
        max_length=100,
    )
    heading_subtitle = blocks.CharBlock(
        label=_("Sottotitolo"),
        max_length=255,
        required=False,
    )
    cards = blocks.ListBlock(
        SectionCardBlock(),
        min_num=1,
        max_num=6,
        label=_("Cards"),
    )
    layout = blocks.ChoiceBlock(
        label=_("Layout"),
        choices=[
            ("grid-3", _("3 colonne")),
            ("grid-2", _("2 colonne")),
            ("grid-3-2", _("3 + 2 colonne (5 cards)")),
        ],
        default="grid-3",
    )

    class Meta:
        icon = "grip"
        label = _("Griglia Sezioni")
        template = "website/blocks/section_cards_grid_block.html"


# =============================================================================
# CTA BLOCK
# =============================================================================

class CTABlock(blocks.StructBlock):
    """Sezione Call-to-Action."""
    title = blocks.CharBlock(label=_("Titolo"), max_length=150)
    title_highlight = blocks.CharBlock(
        label=_("Parola evidenziata"),
        max_length=50,
        required=False,
        help_text=_("Parte del titolo in oro"),
    )
    subtitle = blocks.TextBlock(label=_("Sottotitolo"), required=False)

    # Primary CTA
    cta_primary_text = blocks.CharBlock(label=_("Testo primario"), max_length=50)
    cta_primary_link = blocks.URLBlock(label=_("Link primario"))
    cta_primary_icon = blocks.CharBlock(
        label=_("Icona primaria"),
        max_length=50,
        default="fas fa-user-plus",
        required=False,
    )

    # Secondary CTA
    cta_secondary_text = blocks.CharBlock(
        label=_("Testo secondario"),
        max_length=50,
        required=False,
    )
    cta_secondary_link = blocks.URLBlock(
        label=_("Link secondario"),
        required=False,
    )
    cta_secondary_icon = blocks.CharBlock(
        label=_("Icona secondaria"),
        max_length=50,
        default="fas fa-phone",
        required=False,
    )

    background = blocks.ChoiceBlock(
        label=_("Sfondo"),
        choices=[
            ("bg-navy", _("Navy")),
            ("bg-bordeaux", _("Bordeaux")),
            ("bg-gradient-hero", _("Gradiente")),
        ],
        default="bg-navy",
    )

    class Meta:
        icon = "pick"
        label = _("Call-to-Action")
        template = "website/blocks/cta_block.html"


# =============================================================================
# VALUES BLOCK
# =============================================================================

class ValueItemBlock(blocks.StructBlock):
    """Singolo valore."""
    icon = blocks.CharBlock(
        label=_("Icona"),
        max_length=50,
        default="fas fa-heart",
    )
    title = blocks.CharBlock(label=_("Titolo"), max_length=50)
    description = blocks.TextBlock(label=_("Descrizione"))

    class Meta:
        icon = "pick"
        label = _("Valore")


class ValuesBlock(blocks.StructBlock):
    """Sezione valori."""
    heading = blocks.CharBlock(
        label=_("Titolo sezione"),
        max_length=100,
        default="I Nostri Valori",
    )
    values = blocks.ListBlock(
        ValueItemBlock(),
        min_num=1,
        max_num=6,
        label=_("Valori"),
    )

    class Meta:
        icon = "pick"
        label = _("Valori")
        template = "website/blocks/values_block.html"


# =============================================================================
# TIMELINE BLOCK
# =============================================================================

class TimelineItemBlock(blocks.StructBlock):
    """Singolo evento nella timeline."""
    year = blocks.CharBlock(
        label=_("Anno"),
        max_length=10,
    )
    title = blocks.CharBlock(
        label=_("Titolo"),
        max_length=100,
    )
    description = blocks.TextBlock(
        label=_("Descrizione"),
    )
    highlight = blocks.BooleanBlock(
        label=_("Evidenzia (bordo gold)"),
        required=False,
        default=False,
    )
    color = blocks.ChoiceBlock(
        label=_("Colore badge"),
        choices=[
            ("gold", _("Gold")),
            ("navy", _("Navy")),
            ("amaranth", _("Amaranto")),
        ],
        default="navy",
    )

    class Meta:
        icon = "date"
        label = _("Evento Timeline")


class TimelineBlock(blocks.StructBlock):
    """Sezione timeline storica."""
    heading = blocks.CharBlock(
        label=_("Titolo sezione"),
        max_length=100,
        default="La Nostra Storia",
    )
    events = blocks.ListBlock(
        TimelineItemBlock(),
        min_num=1,
        label=_("Eventi"),
    )

    class Meta:
        icon = "history"
        label = _("Timeline Storica")
        template = "website/blocks/timeline_block.html"


# =============================================================================
# GALLERY BLOCKS (ESTESI)
# =============================================================================

class GalleryImageBlock(blocks.StructBlock):
    """
    Blocco per immagine galleria con categoria (schema.org ImageObject).
    """
    image = ImageChooserBlock(label=_("Immagine"))
    caption = blocks.CharBlock(
        label=_("Didascalia"),
        max_length=255,
        required=False,
    )
    category = blocks.ChoiceBlock(
        label=_("Categoria"),
        choices=[
            ("all", _("Tutti")),
            ("raduni", _("Raduni")),
            ("escursioni", _("Escursioni")),
            ("gare", _("Gare")),
            ("sociali", _("Eventi Sociali")),
        ],
        default="all",
    )

    class Meta:
        icon = "image"
        label = _("Immagine")


class GalleryBlock(blocks.StructBlock):
    """
    Galleria con filtri categoria e lightbox.
    """
    title = blocks.CharBlock(
        label=_("Titolo galleria"),
        max_length=255,
        required=False,
    )
    show_filters = blocks.BooleanBlock(
        label=_("Mostra filtri categoria"),
        default=True,
        required=False,
    )
    images = blocks.ListBlock(
        GalleryImageBlock(),
        label=_("Immagini"),
    )
    columns = blocks.ChoiceBlock(
        label=_("Colonne"),
        choices=[
            ("grid-cols-2", _("2 colonne")),
            ("grid-cols-3", _("3 colonne")),
            ("grid-cols-4", _("4 colonne")),
        ],
        default="grid-cols-4",
    )

    class Meta:
        icon = "image"
        label = _("Galleria")
        template = "website/blocks/gallery_block.html"


# =============================================================================
# CONTENT BLOCKS (ESISTENTI)
# =============================================================================

class ArticleBlock(blocks.StructBlock):
    """
    Blocco Article per Timeline (schema.org Article/NewsArticle).
    """
    headline = blocks.CharBlock(
        label=_("Titolo"),
        max_length=255,
        help_text=_("Titolo dell'articolo"),
    )
    image = ImageChooserBlock(
        label=_("Immagine"),
        required=False,
    )
    date_published = blocks.DateBlock(
        label=_("Data pubblicazione"),
    )
    article_section = blocks.CharBlock(
        label=_("Categoria"),
        max_length=100,
        required=False,
        help_text=_("Categoria o tema dell'articolo"),
    )
    summary = blocks.RichTextBlock(
        label=_("Sommario"),
        required=False,
    )
    url = blocks.URLBlock(
        label=_("Link approfondimento"),
        required=False,
    )

    class Meta:
        icon = "doc-full"
        label = _("Articolo")
        template = "website/blocks/article_block.html"


class MemberBlock(blocks.StructBlock):
    """
    Blocco per membro del consiglio direttivo (schema.org Person).
    """
    name = blocks.CharBlock(
        label=_("Nome"),
        max_length=255,
    )
    role = blocks.CharBlock(
        label=_("Ruolo"),
        max_length=100,
    )
    image = ImageChooserBlock(
        label=_("Foto"),
        required=False,
    )
    bio = blocks.RichTextBlock(
        label=_("Biografia"),
        required=False,
    )

    class Meta:
        icon = "user"
        label = _("Membro")
        template = "website/blocks/member_block.html"


class DocumentBlock(blocks.StructBlock):
    """
    Blocco per documento allegato.
    """
    title = blocks.CharBlock(
        label=_("Titolo"),
        max_length=255,
    )
    document = DocumentChooserBlock(
        label=_("Documento"),
    )
    description = blocks.TextBlock(
        label=_("Descrizione"),
        required=False,
    )

    class Meta:
        icon = "doc-full-inverse"
        label = _("Documento")
        template = "website/blocks/document_block.html"


class MapBlock(blocks.StructBlock):
    """
    Blocco mappa OpenStreetMap con Leaflet.
    """
    title = blocks.CharBlock(
        label=_("Titolo"),
        max_length=255,
        required=False,
    )
    address = blocks.CharBlock(
        label=_("Indirizzo"),
        max_length=500,
        help_text=_("Indirizzo da geocodificare"),
    )
    latitude = blocks.FloatBlock(
        label=_("Latitudine"),
        required=False,
        help_text=_("Lascia vuoto per geocodifica automatica"),
    )
    longitude = blocks.FloatBlock(
        label=_("Longitudine"),
        required=False,
    )
    zoom = blocks.IntegerBlock(
        label=_("Zoom"),
        default=15,
        min_value=1,
        max_value=19,
    )
    height = blocks.CharBlock(
        label=_("Altezza"),
        default="400px",
        max_length=20,
    )

    class Meta:
        icon = "site"
        label = _("Mappa")
        template = "website/blocks/map_block.html"


class EventCardBlock(blocks.StructBlock):
    """
    Blocco per card evento (schema.org Event).
    """
    name = blocks.CharBlock(
        label=_("Nome evento"),
        max_length=255,
    )
    start_date = blocks.DateTimeBlock(
        label=_("Data inizio"),
    )
    end_date = blocks.DateTimeBlock(
        label=_("Data fine"),
        required=False,
    )
    location_name = blocks.CharBlock(
        label=_("Luogo"),
        max_length=255,
    )
    location_address = blocks.CharBlock(
        label=_("Indirizzo"),
        max_length=500,
        required=False,
    )
    image = ImageChooserBlock(
        label=_("Immagine"),
        required=False,
    )
    description = blocks.RichTextBlock(
        label=_("Descrizione"),
        required=False,
    )
    event_status = blocks.ChoiceBlock(
        label=_("Stato evento"),
        choices=[
            ("EventScheduled", _("Programmato")),
            ("EventCancelled", _("Annullato")),
            ("EventPostponed", _("Posticipato")),
            ("EventRescheduled", _("Riprogrammato")),
        ],
        default="EventScheduled",
    )
    event_url = blocks.URLBlock(
        label=_("Link dettaglio"),
        required=False,
    )

    class Meta:
        icon = "date"
        label = _("Evento")
        template = "website/blocks/event_card_block.html"

