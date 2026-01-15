# 📐 Proposta di Modifica Struttura CoderedCMS/Wagtail

## Obiettivo

Integra nel progetto Django/Wagtail tutti gli asset del sito statico motoclub-static/ e configura il sistema in questo modo:
    - Usa l’ultima versione stabile di CoderedCMS, Wagtail e Django, con gestione completa dei contenuti dinamici da CMS.
    - Attiva e configura il supporto multilingue per IT, EN, ES, FR, DE (URL, contenuti, menu, pagine e stringhe dell’interfaccia).
    - Implementa i markup Schema.org per migliorare SEO (organizzazione, eventi, articoli, gallerie/foto).
    - Implementa controlli automatici e linee guida per garantire conformità WCAG 2.2 livello AAA (colori, contrasti, tastiera, ARIA, struttura semantica).
    - Esegui una revisione critica di sicurezza e applica best practice (hardening, permessi, autenticazione, rate limiting, sanitizzazione input, protezione form).
    - Rendi le gallerie riutilizzabili: devono essere richiamabili da qualunque pagina tramite relazione (es. scelta da CMS o blocco riutilizzabile).
    - Implementa un sistema di upload galleria:
        + Upload multiplo di file (immagini/video) in un’unica operazione.
        + Campi di testo per tag e descrizione generale della galleria.
        + Le descrizioni iniziali degli elementi vengono copiate dal nome file.
        + Accesso pubblico al form, ma:
            - Proteggi con un CAPTCHA matematico.
            - Richiedi un token inviato via email a un utente già approvato nel sistema (whitelist).
    - Integra questo sistema nel flusso editoriale del CMS (moderazione, approvazione, pubblicazione).


---

## 📊 Mappatura Elementi Grafici → Wagtail

| Elemento Statico | Componente Wagtail | Stato Attuale | Azione |
|------------------|-------------------|---------------|--------|
| Navbar dorata responsive | `base.jinja2` | ❌ Stile diverso | **Aggiornare** |
| Photo Slider homepage | `HeroSliderBlock` | ❌ Mancante | **Creare** |
| Hero con countdown | `HeroCountdownBlock` | ❌ Mancante | **Creare** |
| Stats section | `StatsBlock` | ❌ Mancante | **Creare** |
| Cards sezioni | `SectionCardBlock` | ❌ Mancante | **Creare** |
| Timeline verticale | `TimelinePage` | ✅ Esiste | **Aggiornare stile** |
| Member cards | `MemberBlock` | ✅ Esiste | **Aggiornare stile** |
| Event cards | `EventCardBlock` | ✅ Esiste | **Aggiornare stile** |
| Gallery con filtri | `GalleryBlock` | ⚠️ Parziale | **Estendere** |
| Contact form + mappa | `ContactPage` | ✅ Esiste | **Aggiornare stile** |
| Footer 4 colonne | `base.jinja2` | ❌ Stile diverso | **Aggiornare** |
| CTA section | `CTABlock` | ❌ Mancante | **Creare** |
| Valori cards | `ValueBlock` | ❌ Mancante | **Creare** |

---

## 1️⃣ Nuovi StreamField Blocks

### 1.1 `HeroSliderBlock`

Slider fotografico con navigazione e overlay.

```python
# apps/website/blocks.py

class HeroSlideBlock(blocks.StructBlock):
    """Singola slide dello slider hero."""
    image = ImageChooserBlock(label=_("Immagine"))
    title = blocks.CharBlock(label=_("Titolo"), max_length=100)
    category = blocks.CharBlock(
        label=_("Categoria"),
        max_length=50,
        required=False,
        help_text=_("Es: Raduni, Escursioni, Gare")
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
            ("100vh", "Schermo intero"),
        ],
        default="75vh",
    )
    
    class Meta:
        icon = "image"
        label = _("Slider Fotografico")
        template = "website/blocks/hero_slider_block.html"
```

### 1.2 `HeroCountdownBlock`

Hero section con countdown per evento in evidenza.

```python
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
    cta_secondary_text = blocks.CharBlock(label=_("Testo CTA secondario"), max_length=50, required=False)
    cta_secondary_link = blocks.URLBlock(label=_("Link CTA secondario"), required=False)
    
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
        template = "website/blocks/hero_countdown_block.html"
```

### 1.3 `StatsBlock`

Sezione statistiche con icone animate.

```python
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
            ("bg-gold", "Oro"),
            ("bg-bordeaux", "Bordeaux"),
            ("bg-navy", "Navy"),
            ("bg-amaranth", "Amaranto"),
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
            ("bg-white", "Bianco"),
            ("bg-cream", "Crema"),
            ("bg-navy", "Navy"),
        ],
        default="bg-white",
    )
    
    class Meta:
        icon = "order"
        label = _("Statistiche")
        template = "website/blocks/stats_block.html"
```

### 1.4 `SectionCardBlock`

Card per sezioni con immagine, icona e link.

```python
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
            ("bg-gold text-navy", "Oro"),
            ("bg-bordeaux text-white", "Bordeaux"),
            ("bg-navy text-gold", "Navy"),
            ("bg-amaranth text-white", "Amaranto"),
            ("bg-white text-amaranth", "Bianco"),
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
            ("text-gold", "Oro"),
            ("text-bordeaux", "Bordeaux"),
            ("text-navy", "Navy"),
            ("text-amaranth", "Amaranto"),
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
            ("grid-3", "3 colonne"),
            ("grid-2", "2 colonne"),
            ("grid-3-2", "3 + 2 colonne (5 cards)"),
        ],
        default="grid-3",
    )
    
    class Meta:
        icon = "grip"
        label = _("Griglia Sezioni")
        template = "website/blocks/section_cards_grid_block.html"
```

### 1.5 `CTABlock`

Sezione call-to-action.

```python
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
            ("bg-navy", "Navy"),
            ("bg-bordeaux", "Bordeaux"),
            ("bg-gradient-hero", "Gradiente"),
        ],
        default="bg-navy",
    )
    
    class Meta:
        icon = "pick"
        label = _("Call-to-Action")
        template = "website/blocks/cta_block.html"
```

### 1.6 `ValueBlock`

Card valori (Passione, Amicizia, Avventura).

```python
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
```

### 1.7 Estensione `GalleryBlock`

Aggiungere filtri per categoria.

```python
class GalleryImageBlock(blocks.StructBlock):
    """Blocco per immagine galleria con categoria."""
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
    """Galleria con filtri categoria e lightbox."""
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
            ("grid-cols-2", "2 colonne"),
            ("grid-cols-3", "3 colonne"),
            ("grid-cols-4", "4 colonne"),
        ],
        default="grid-cols-4",
    )
    
    class Meta:
        icon = "image"
        label = _("Galleria")
        template = "website/blocks/gallery_block.html"
```

---

## 2️⃣ Modifiche ai Models Esistenti

### 2.1 `HomePage`

Aggiungere StreamField per contenuti flessibili.

```python
# apps/website/models/home.py

from apps.website.blocks import (
    HeroSliderBlock, HeroCountdownBlock, StatsBlock,
    SectionCardsGridBlock, CTABlock, ValuesBlock,
)

class HomePage(SchemaOrgMixin, Page):
    # ... campi esistenti ...
    
    # Nuovo: StreamField per body flessibile
    body = StreamField(
        [
            ("hero_slider", HeroSliderBlock()),
            ("hero_countdown", HeroCountdownBlock()),
            ("stats", StatsBlock()),
            ("section_cards", SectionCardsGridBlock()),
            ("cta", CTABlock()),
            ("values", ValuesBlock()),
            ("gallery", GalleryBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Contenuto pagina"),
    )
    
    content_panels = Page.content_panels + [
        # ... pannelli esistenti ...
        FieldPanel("body"),
    ]
```

### 2.2 `AboutPage`

Aggiungere timeline e valori.

```python
# apps/website/models/about.py

class AboutPage(SchemaOrgMixin, Page):
    # ... campi esistenti ...
    
    # Timeline milestones
    milestones = StreamField(
        [
            ("milestone", ArticleBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Tappe storiche"),
    )
    
    # Valori
    values = StreamField(
        [
            ("value", ValueItemBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Valori"),
    )
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("milestones"),
        FieldPanel("values"),
    ]
```

### 2.3 `EventsPage`

Aggiungere evento in evidenza.

```python
# apps/website/models/events.py

class EventsPage(SchemaOrgMixin, Page):
    # ... campi esistenti ...
    
    # Evento in evidenza (featured)
    featured_event = models.ForeignKey(
        "website.EventDetailPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Evento in evidenza"),
        help_text=_("Mostrato con countdown nella hero"),
    )
    
    # Tipi di eventi (per filtri)
    show_event_types = models.BooleanField(
        _("Mostra sezione tipi eventi"),
        default=True,
    )
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("featured_event"),
        FieldPanel("show_event_types"),
    ]
```

### 2.4 Nuova `GalleryPage`

Pagina dedicata alla galleria.

```python
# apps/website/models/gallery.py (NUOVO FILE)

"""
MC Castellazzo - Gallery Page Model
====================================
schema.org ImageGallery
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.schema import SchemaOrgMixin
from apps.website.blocks import GalleryBlock


class GalleryPage(SchemaOrgMixin, Page):
    """
    Pagina Galleria Fotografica - schema.org ImageGallery.
    """
    
    intro = models.TextField(
        _("Introduzione"),
        blank=True,
    )
    
    gallery = StreamField(
        [
            ("gallery", GalleryBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Gallerie"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/gallery_page.jinja2"
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("gallery"),
    ]
    
    class Meta:
        verbose_name = _("Galleria")
        verbose_name_plural = _("Gallerie")
    
    def get_schema_org_type(self) -> str:
        return "ImageGallery"
    
    def get_schema_org_data(self) -> dict:
        images = []
        for gallery_block in self.gallery:
            if gallery_block.block_type == "gallery":
                for img in gallery_block.value.get("images", []):
                    if img.get("image"):
                        images.append({
                            "@type": "ImageObject",
                            "url": img["image"].get_rendition("original").url,
                            "caption": img.get("caption", ""),
                        })
        
        return {
            "name": self.title,
            "description": self.intro,
            "image": images,
        }
```

---

## 3️⃣ Nuovi Template Blocks

### Struttura directory

```
templates/website/blocks/
├── hero_slider_block.html      # NUOVO
├── hero_countdown_block.html   # NUOVO
├── stats_block.html            # NUOVO
├── section_card_block.html     # NUOVO
├── section_cards_grid_block.html  # NUOVO
├── cta_block.html              # NUOVO
├── values_block.html           # NUOVO
├── gallery_block.html          # AGGIORNARE
├── article_block.html          # AGGIORNARE stile
├── member_block.html           # AGGIORNARE stile
├── event_card_block.html       # AGGIORNARE stile
├── map_block.html              # OK
└── document_block.html         # OK
```

### 3.1 Esempio `hero_slider_block.html`

```jinja2
{# templates/website/blocks/hero_slider_block.html #}
<section id="photo-slider" class="relative w-full overflow-hidden bg-navy pt-24" style="height: {{ self.height }};">
    <div class="slider-container h-full relative" data-autoplay="{{ self.autoplay|lower }}" data-interval="{{ self.interval }}">
        <div class="slider-track h-full flex transition-transform duration-700 ease-in-out">
            {% for slide in self.slides %}
            <div class="slide min-w-full h-full relative">
                {{ image(slide.image, "fill-1600x900", class="w-full h-full object-cover") }}
                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-navy/90 to-transparent p-8">
                    <h3 class="text-white text-3xl font-bold">{{ slide.title }}</h3>
                    {% if slide.category %}
                    <p class="text-gold text-sm mt-2">{{ slide.category }}</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>

        {# Navigation #}
        <button class="slider-prev absolute left-4 top-1/2 -translate-y-1/2 bg-gold/90 hover:bg-gold text-navy w-12 h-12 rounded-full flex items-center justify-center transition shadow-lg z-10" aria-label="{% trans %}Foto precedente{% endtrans %}">
            <i class="fas fa-chevron-left" aria-hidden="true"></i>
        </button>
        <button class="slider-next absolute right-4 top-1/2 -translate-y-1/2 bg-gold/90 hover:bg-gold text-navy w-12 h-12 rounded-full flex items-center justify-center transition shadow-lg z-10" aria-label="{% trans %}Foto successiva{% endtrans %}">
            <i class="fas fa-chevron-right" aria-hidden="true"></i>
        </button>

        {# Dots #}
        <div class="slider-dots absolute bottom-20 left-1/2 -translate-x-1/2 flex gap-2 z-10">
            {% for slide in self.slides %}
            <button class="dot w-3 h-3 rounded-full {% if loop.first %}bg-gold{% else %}bg-white/50{% endif %}" data-index="{{ loop.index0 }}" aria-label="{% trans %}Vai alla foto{% endtrans %} {{ loop.index }}"></button>
            {% endfor %}
        </div>
    </div>
</section>
```

---

## 4️⃣ Static Files

### Struttura proposta

```
static/
├── css/
│   ├── motoclub.css          # CSS principale (da style.css statico)
│   ├── animations.css        # Animazioni
│   └── variables.css         # Variabili CSS (colori, font)
├── js/
│   ├── motoclub.js           # JS principale
│   ├── slider.js             # Logica slider
│   ├── gallery-lightbox.js   # Lightbox galleria
│   ├── countdown.js          # Countdown eventi
│   └── mobile-menu.js        # Menu mobile
└── images/
    └── MotoClubCastellazzoBormida-logo.webp
```

### 4.1 `variables.css`

```css
:root {
    /* Colori Primari - Profilo Caldo */
    --gold: #ffd700;
    --gold-dark: #f6c401;
    --bordeaux: #ab0031;
    
    /* Colori Secondari */
    --navy: #1B263B;
    --navy-light: #2D3E5C;
    --amaranth: #9B1D64;
    --amaranth-dark: #7A164F;
    --cream: #FEFCF6;
    --warm-gray: #F5F3EE;
    
    /* Neutri */
    --white: #FFFFFF;
    --black: #000000;
    --gray-100: #F8F9FA;
    --gray-400: #9CA3AF;
    --gray-600: #6B7280;
    --gray-800: #343A40;
    
    /* Gradienti */
    --gradient-primary: linear-gradient(135deg, #ab0031 0%, #f6c401 50%, #ffd700 100%);
    --gradient-navbar: linear-gradient(135deg, rgba(171, 0, 49, 0.95) 0%, rgba(27, 38, 59, 0.95) 100%);
    --gradient-hero: linear-gradient(135deg, #1B263B 0%, #ab0031 50%, #ffd700 100%);
    
    /* Ombre */
    --shadow-gold: 0 10px 30px rgba(255, 215, 0, 0.3);
    --shadow-bordeaux: 0 8px 25px rgba(171, 0, 49, 0.25);
    --shadow-card: 0 4px 20px rgba(27, 38, 59, 0.1);
    
    /* Font */
    --font-heading: 'Montserrat', sans-serif;
    --font-body: 'Inter', sans-serif;
    
    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 2rem;
    --space-xl: 4rem;
    
    /* Border Radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 1rem;
    --radius-xl: 1.5rem;
    --radius-full: 9999px;
}
```

---

## 5️⃣ Modifiche a `base.jinja2`

### 5.1 Head aggiornato

```jinja2
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}{{ page.title }}{% endblock %} | MC Castellazzo</title>
    
    {# SEO #}
    <meta name="description" content="{% block meta_description %}MC Castellazzo - Motoclub dal 1933{% endblock %}">
    
    {# Schema.org JSON-LD #}
    {% if page.get_json_ld is defined %}
    <script type="application/ld+json">{{ page.get_json_ld() }}</script>
    {% endif %}
    
    {# Preconnect #}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    {# Google Fonts #}
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    {# Font Awesome #}
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    {# AOS Animate #}
    <link rel="stylesheet" href="https://unpkg.com/aos@2.3.1/dist/aos.css">
    
    {# Leaflet (mappe) #}
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    
    {# Tailwind CDN (o compilato) #}
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'gold': '#ffd700',
                        'gold-dark': '#f6c401',
                        'bordeaux': '#ab0031',
                        'navy': '#1B263B',
                        'navy-light': '#2D3E5C',
                        'amaranth': '#9B1D64',
                        'cream': '#FEFCF6',
                        'warm-gray': '#F5F3EE',
                    },
                    fontFamily: {
                        'heading': ['Montserrat', 'sans-serif'],
                        'body': ['Inter', 'sans-serif'],
                    },
                }
            }
        }
    </script>
    
    {# CSS Custom #}
    <link rel="stylesheet" href="{{ static('css/motoclub.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
```

### 5.2 Navbar aggiornata

```jinja2
{# Skip Link #}
<a href="#main-content" class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 bg-gold text-navy px-4 py-2 rounded z-50 font-bold">
    {% trans %}Vai al contenuto principale{% endtrans %}
</a>

{# Navbar #}
<nav id="navbar" class="fixed w-full z-50 bg-gold shadow-md" aria-label="{% trans %}Navigazione principale{% endtrans %}">
    <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex justify-between items-center">
            {# Logo #}
            <a href="/{{ request.LANGUAGE_CODE }}/" class="flex items-center gap-4">
                {% if settings.website.SiteSettings.logo %}
                    {{ image(settings.website.SiteSettings.logo, "height-56", class="h-14 w-14") }}
                {% else %}
                    <img src="{{ static('images/MotoClubCastellazzoBormida-logo.webp') }}" alt="" class="h-14 w-14">
                {% endif %}
                <div>
                    <span class="text-navy font-heading font-bold text-xl block">MC Castellazzo Bormida</span>
                    <span class="text-navy text-xs tracking-widest">{% trans %}DAL 1933{% endtrans %}</span>
                </div>
            </a>
            
            {# Menu Desktop #}
            <div class="hidden lg:flex items-center gap-8">
                {% set nav_items = [
                    ('/', 'Home'),
                    ('/chi-siamo/', 'Chi Siamo'),
                    ('/consiglio/', 'Il Consiglio'),
                    ('/eventi/', 'Eventi'),
                    ('/galleria/', 'Galleria'),
                ] %}
                {% for url, label in nav_items %}
                    <a href="/{{ request.LANGUAGE_CODE }}{{ url }}" 
                       class="text-navy hover:text-bordeaux transition {% if request.path == '/' ~ request.LANGUAGE_CODE ~ url %}font-semibold border-b-2 border-navy pb-1{% endif %}">
                        {% trans %}{{ label }}{% endtrans %}
                    </a>
                {% endfor %}
                <a href="/{{ request.LANGUAGE_CODE }}/contatti/" class="bg-bordeaux text-white font-bold px-6 py-3 rounded-full hover:bg-gold-dark hover:text-navy transition">
                    {% trans %}Contattaci{% endtrans %}
                </a>
            </div>
            
            {# Language + Auth #}
            <div class="flex items-center gap-4">
                {# Language Switcher #}
                <div class="hidden md:flex gap-1">
                    {% for lang_code, lang_name in [('it', 'IT'), ('fr', 'FR'), ('es', 'ES'), ('en', 'EN')] %}
                        <a href="/{{ lang_code }}{{ request.path[3:] }}" 
                           class="px-2 py-1 rounded text-sm {% if request.LANGUAGE_CODE == lang_code %}bg-navy text-white{% else %}text-navy border border-navy/30{% endif %}">
                            {{ lang_name }}
                        </a>
                    {% endfor %}
                </div>
                
                {# Mobile Menu Button #}
                <button id="mobile-menu-btn" class="lg:hidden text-navy text-2xl" aria-label="{% trans %}Apri menu{% endtrans %}" aria-expanded="false">
                    <i class="fas fa-bars" aria-hidden="true"></i>
                </button>
            </div>
        </div>
    </div>
    
    {# Mobile Menu #}
    <div id="mobile-menu" class="hidden lg:hidden bg-white border-t border-gray-100" role="menu">
        <div class="px-6 py-4 space-y-4">
            {% for url, label in nav_items %}
                <a href="/{{ request.LANGUAGE_CODE }}{{ url }}" class="block text-gray-600 hover:text-navy py-2 border-b border-gray-100" role="menuitem">
                    {% trans %}{{ label }}{% endtrans %}
                </a>
            {% endfor %}
            <a href="/{{ request.LANGUAGE_CODE }}/contatti/" class="block bg-bordeaux text-white text-center font-bold px-6 py-3 rounded-full mt-4" role="menuitem">
                {% trans %}Contattaci{% endtrans %}
            </a>
        </div>
    </div>
</nav>

{# Spacer #}
<div class="h-24"></div>
```

### 5.3 Footer aggiornato

```jinja2
<footer class="bg-navy pt-16 pb-8" role="contentinfo">
    <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
            {# Col 1: Brand #}
            <div>
                <div class="flex items-center gap-4 mb-6">
                    {% if settings.website.SiteSettings.logo %}
                        {{ image(settings.website.SiteSettings.logo, "height-56", class="h-14", aria_hidden="true") }}
                    {% endif %}
                    <div>
                        <span class="text-gold font-heading font-bold text-lg block">MC Castellazzo</span>
                        <span class="text-gray-400 text-sm">Bormida</span>
                    </div>
                </div>
                <p class="text-gray-400 leading-relaxed text-sm">
                    {% trans %}Dal 1933 la passione per le due ruote nel cuore del Piemonte.{% endtrans %}
                </p>
            </div>
            
            {# Col 2: Link Rapidi #}
            <nav aria-label="{% trans %}Link rapidi{% endtrans %}">
                <h3 class="text-gold font-heading font-bold text-lg mb-6">{% trans %}Link Rapidi{% endtrans %}</h3>
                <ul class="space-y-3">
                    <li><a href="/{{ request.LANGUAGE_CODE }}/chi-siamo/" class="text-gray-400 hover:text-gold transition flex items-center gap-2"><i class="fas fa-chevron-right text-xs" aria-hidden="true"></i>{% trans %}Chi Siamo{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/eventi/" class="text-gray-400 hover:text-gold transition flex items-center gap-2"><i class="fas fa-chevron-right text-xs" aria-hidden="true"></i>{% trans %}Eventi{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/galleria/" class="text-gray-400 hover:text-gold transition flex items-center gap-2"><i class="fas fa-chevron-right text-xs" aria-hidden="true"></i>{% trans %}Galleria{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/contatti/" class="text-gray-400 hover:text-gold transition flex items-center gap-2"><i class="fas fa-chevron-right text-xs" aria-hidden="true"></i>{% trans %}Contatti{% endtrans %}</a></li>
                </ul>
            </nav>
            
            {# Col 3: Contatti #}
            <div>
                <h3 class="text-gold font-heading font-bold text-lg mb-6">{% trans %}Contatti{% endtrans %}</h3>
                <ul class="space-y-3 text-gray-400 text-sm">
                    <li class="flex items-start gap-3">
                        <i class="fas fa-map-marker-alt text-gold mt-1" aria-hidden="true"></i>
                        <span>Via Roma 45, 15073<br>Castellazzo Bormida (AL)</span>
                    </li>
                    <li class="flex items-center gap-3">
                        <i class="fas fa-phone text-gold" aria-hidden="true"></i>
                        <a href="tel:+390131278945" class="hover:text-gold transition">+39 0131 278945</a>
                    </li>
                    <li class="flex items-center gap-3">
                        <i class="fas fa-envelope text-gold" aria-hidden="true"></i>
                        <a href="mailto:info@mccastellazzob.com" class="hover:text-gold transition">info@mccastellazzob.com</a>
                    </li>
                </ul>
            </div>
            
            {# Col 4: Social #}
            <div>
                <h3 class="text-gold font-heading font-bold text-lg mb-6">{% trans %}Seguici{% endtrans %}</h3>
                <div class="flex gap-4">
                    {% if settings.website.SiteSettings.facebook_url %}
                    <a href="{{ settings.website.SiteSettings.facebook_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition" aria-label="Facebook">
                        <i class="fab fa-facebook-f" aria-hidden="true"></i>
                    </a>
                    {% endif %}
                    {% if settings.website.SiteSettings.instagram_url %}
                    <a href="{{ settings.website.SiteSettings.instagram_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition" aria-label="Instagram">
                        <i class="fab fa-instagram" aria-hidden="true"></i>
                    </a>
                    {% endif %}
                    {% if settings.website.SiteSettings.youtube_url %}
                    <a href="{{ settings.website.SiteSettings.youtube_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition" aria-label="YouTube">
                        <i class="fab fa-youtube" aria-hidden="true"></i>
                    </a>
                    {% endif %}
                </div>
                
                {# Orari #}
                <div class="mt-6">
                    <h4 class="text-white font-bold mb-2">{% trans %}Segreteria{% endtrans %}</h4>
                    <p class="text-gray-400 text-sm">
                        {% trans %}Mar-Gio: 18:00-20:00{% endtrans %}<br>
                        {% trans %}Sab: 10:00-12:00{% endtrans %}
                    </p>
                </div>
            </div>
        </div>
        
        {# Footer Bottom #}
        <div class="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p class="text-gray-500 text-sm">
                © {{ now().year }} MC Castellazzo Bormida. {% trans %}Tutti i diritti riservati.{% endtrans %}
            </p>
            <div class="flex gap-4 text-gray-500 text-sm">
                <a href="/{{ request.LANGUAGE_CODE }}/privacy/" class="hover:text-gold transition">{% trans %}Privacy{% endtrans %}</a>
                <a href="/{{ request.LANGUAGE_CODE }}/cookie/" class="hover:text-gold transition">{% trans %}Cookie{% endtrans %}</a>
            </div>
        </div>
    </div>
</footer>
```

---

## 6️⃣ Checklist Implementazione

### Fase 1: Blocks (2-3 giorni)
- [ ] Creare `HeroSliderBlock`
- [ ] Creare `HeroCountdownBlock`
- [ ] Creare `StatsBlock`
- [ ] Creare `SectionCardBlock` e `SectionCardsGridBlock`
- [ ] Creare `CTABlock`
- [ ] Creare `ValuesBlock`
- [ ] Aggiornare `GalleryBlock` con categorie
- [ ] Registrare tutti i blocks in `__init__.py`

### Fase 2: Models (1-2 giorni)
- [ ] Aggiungere `body` StreamField a `HomePage`
- [ ] Aggiungere `milestones` e `values` a `AboutPage`
- [ ] Aggiungere `featured_event` a `EventsPage`
- [ ] Creare `GalleryPage`
- [ ] Creare migrazioni
- [ ] Registrare in `models/__init__.py`

### Fase 3: Templates (2-3 giorni)
- [ ] Creare template per ogni nuovo block
- [ ] Aggiornare `base.jinja2` (navbar, footer)
- [ ] Aggiornare template pagine esistenti
- [ ] Creare `gallery_page.jinja2`

### Fase 4: Static (1 giorno)
- [ ] Copiare CSS dal sito statico
- [ ] Copiare JS dal sito statico
- [ ] Organizzare in moduli
- [ ] Testare responsive

### Fase 5: Test e Rifinitura (1-2 giorni)
- [ ] Testare accessibilità (WAVE, axe)
- [ ] Validare HTML
- [ ] Testare responsive (mobile, tablet, desktop)
- [ ] Verificare traduzioni
- [ ] Testare schema.org

---

## 📊 Stima Effort

| Fase | Giorni | Complessità |
|------|--------|-------------|
| Blocks | 2-3 | Media |
| Models | 1-2 | Bassa |
| Templates | 2-3 | Media |
| Static | 1 | Bassa |
| Test | 1-2 | Bassa |
| **Totale** | **7-11** | - |

---

## 📚 File da Creare/Modificare

### Nuovi file
- `apps/website/models/gallery.py`
- `templates/website/pages/gallery_page.jinja2`
- `templates/website/blocks/hero_slider_block.html`
- `templates/website/blocks/hero_countdown_block.html`
- `templates/website/blocks/stats_block.html`
- `templates/website/blocks/section_card_block.html`
- `templates/website/blocks/section_cards_grid_block.html`
- `templates/website/blocks/cta_block.html`
- `templates/website/blocks/values_block.html`
- `static/css/motoclub.css`
- `static/css/variables.css`
- `static/js/motoclub.js`
- `static/js/slider.js`
- `static/js/gallery-lightbox.js`
- `static/js/countdown.js`

### File da modificare
- `apps/website/blocks.py` — aggiungere nuovi blocks
- `apps/website/models/__init__.py` — registrare `GalleryPage`
- `apps/website/models/home.py` — aggiungere `body` StreamField
- `apps/website/models/about.py` — aggiungere `milestones`, `values`
- `apps/website/models/events.py` — aggiungere `featured_event`
- `templates/website/base.jinja2` — navbar, footer, head
- `templates/website/blocks/gallery_block.html` — filtri categoria
- `templates/website/blocks/member_block.html` — stile card
- `templates/website/blocks/event_card_block.html` — stile card
- `templates/website/blocks/article_block.html` — stile timeline

---

**MC Castellazzo Bormida** | Proposta Struttura Wagtail v1.0 | Gennaio 2026
