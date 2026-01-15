# 🚀 Integrazione della Grafica Statica in CoderedCMS / Wagtail

Questa guida spiega come trasferire la grafica e il sistema di colori realizzati in `motoclub-static/` al progetto Django/Wagtail del sito MC Castellazzo Bormida.

---

## 📋 Panoramica

| Elemento Statico | Destinazione Wagtail |
|------------------|----------------------|
| `css/style.css` | `static/css/motoclub.css` |
| `css/animations.css` | `static/css/animations.css` |
| `js/main.js` | `static/js/motoclub.js` |
| `js/color-manager.js` | (opzionale) `static/js/color-manager.js` |
| `images/*` | `static/images/` oppure upload Wagtail |
| `colors.json` | `static/colors.json` oppure SiteSettings |
| `*.html` struttura | `templates/website/base.jinja2` e blocks |

---

## 1️⃣ Copiare gli Asset Statici

### 1.1 CSS

Copia i file CSS nella cartella `static/`:

```bash
cp motoclub-static/css/style.css static/css/motoclub.css
cp motoclub-static/css/animations.css static/css/animations.css
```

### 1.2 JavaScript

```bash
cp motoclub-static/js/main.js static/js/motoclub.js
# Opzionale: sistema colori dinamico
cp motoclub-static/js/color-manager.js static/js/color-manager.js
```

### 1.3 Immagini

```bash
cp motoclub-static/images/MotoClubCastellazzoBormida-logo.webp static/images/
```

> **Nota:** Le immagini gestite da Wagtail (logo, galleria, eventi) vanno caricate tramite admin in `wagtailimages`.

---

## 2️⃣ Integrare nel Template Base Jinja2

Modifica `templates/website/base.jinja2`:

### 2.1 Head - Aggiungere CSS e Font

```jinja2
{# Nel <head>, dopo le meta #}

{# Google Fonts #}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

{# Font Awesome #}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

{# AOS Animate #}
<link rel="stylesheet" href="https://unpkg.com/aos@2.3.1/dist/aos.css">

{# CSS Motoclub #}
<link rel="stylesheet" href="{{ static('css/motoclub.css') }}">
<link rel="stylesheet" href="{{ static('css/animations.css') }}">
```

### 2.2 Variabili CSS Dinamiche

Sostituisci le variabili `:root` inline con quelle del profilo caldo:

```jinja2
<style>
:root {
    /* Colori Primari - Profilo Caldo */
    --gold: #ffd700;
    --gold-dark: #f6c401;
    --bordeaux: #ab0031;
    
    /* Colori Secondari */
    --navy: #1B263B;
    --navy-light: #2A3B52;
    --amaranth: #9B1D64;
    --cream: #FFF8E7;
    
    /* Neutri */
    --white: #FFFFFF;
    --black: #000000;
    --gray-100: #F8F9FA;
    --gray-200: #E9ECEF;
    --gray-400: #9CA3AF;
    --gray-800: #343A40;
    
    /* Gradienti */
    --gradient-primary: linear-gradient(135deg, #ab0031 0%, #f6c401 50%, #ffd700 100%);
    --gradient-navbar: linear-gradient(135deg, rgba(171, 0, 49, 0.95) 0%, rgba(27, 38, 59, 0.95) 100%);
    --gradient-hero: linear-gradient(135deg, #1B263B 0%, #ab0031 50%, #ffd700 100%);
    
    /* Ombre */
    --shadow-gold: 0 10px 30px rgba(255, 215, 0, 0.3);
    --shadow-bordeaux: 0 8px 25px rgba(171, 0, 49, 0.25);
    
    /* Font */
    --font-heading: 'Montserrat', sans-serif;
    --font-body: 'Inter', sans-serif;
}
</style>
```

### 2.3 Body - Script

Prima di `</body>`:

```jinja2
{# AOS Init #}
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });
</script>

{# JavaScript Motoclub #}
<script src="{{ static('js/motoclub.js') }}"></script>
```

---

## 3️⃣ Convertire la Navbar

Sostituisci la navbar in `base.jinja2` con la struttura responsive del sito statico:

```jinja2
{# Skip link accessibilità #}
<a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-gold text-navy px-4 py-2 rounded z-50">
    {% trans %}Vai al contenuto principale{% endtrans %}
</a>

<header id="header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
    <nav class="navbar" style="background: var(--gradient-navbar);">
        <div class="max-w-7xl mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                {# Logo #}
                <a href="/{{ request.LANGUAGE_CODE }}/" class="flex items-center gap-3">
                    {% if settings.website.SiteSettings.logo %}
                        {{ image(settings.website.SiteSettings.logo, "height-56", class="h-14 w-auto") }}
                    {% else %}
                        <img src="{{ static('images/MotoClubCastellazzoBormida-logo.webp') }}" alt="Logo" class="h-14 w-14">
                    {% endif %}
                    <div>
                        <span class="text-gold font-heading font-bold text-xl block">MC Castellazzo Bormida</span>
                        <span class="text-white/80 text-sm">Dal 1933</span>
                    </div>
                </a>
                
                {# Menu Desktop #}
                <div class="hidden lg:flex items-center gap-8">
                    <a href="/{{ request.LANGUAGE_CODE }}/" class="text-white hover:text-gold transition-colors">Home</a>
                    <a href="/{{ request.LANGUAGE_CODE }}/chi-siamo/" class="text-white hover:text-gold transition-colors">Chi Siamo</a>
                    <a href="/{{ request.LANGUAGE_CODE }}/eventi/" class="text-white hover:text-gold transition-colors">Eventi</a>
                    <a href="/{{ request.LANGUAGE_CODE }}/galleria/" class="text-white hover:text-gold transition-colors">Galleria</a>
                    <a href="/{{ request.LANGUAGE_CODE }}/contatti/" class="text-white hover:text-gold transition-colors">Contatti</a>
                </div>
                
                {# Auth + Lang #}
                <div class="flex items-center gap-4">
                    {# Language Switcher #}
                    <div class="lang-switcher hidden md:flex">
                        {% for lang_code, lang_name in LANGUAGES %}
                            <a href="/{{ lang_code }}{{ request.path[3:] }}" 
                               class="{% if request.LANGUAGE_CODE == lang_code %}bg-gold text-navy{% else %}text-white border border-white/30{% endif %} px-2 py-1 rounded text-sm">
                                {{ lang_code|upper }}
                            </a>
                        {% endfor %}
                    </div>
                    
                    {# Auth Links #}
                    {% if request.user.is_authenticated %}
                        <a href="{{ url('account_logout') }}" class="btn btn-secondary text-sm">{% trans %}Esci{% endtrans %}</a>
                    {% else %}
                        <a href="{{ url('account_login') }}" class="btn btn-primary text-sm">{% trans %}Accedi{% endtrans %}</a>
                    {% endif %}
                    
                    {# Mobile Menu Button #}
                    <button id="mobile-menu-btn" class="lg:hidden text-white text-2xl" aria-label="Apri menu">
                        <i class="fas fa-bars"></i>
                    </button>
                </div>
            </div>
        </div>
    </nav>
</header>

{# Spacer per fixed header #}
<div class="h-20 lg:h-24"></div>
```

---

## 4️⃣ Convertire il Footer

```jinja2
<footer class="bg-navy pt-16 pb-8" role="contentinfo">
    <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-4 gap-8 mb-12">
            {# Col 1: Logo e descrizione #}
            <div>
                <div class="flex items-center gap-3 mb-4">
                    {% if settings.website.SiteSettings.logo %}
                        {{ image(settings.website.SiteSettings.logo, "height-48", class="h-12", aria_hidden="true") }}
                    {% endif %}
                    <span class="text-gold font-heading font-bold">MC Castellazzo Bormida</span>
                </div>
                <p class="text-gray-400 text-sm">Dal 1933 la passione per le due ruote nel cuore del Piemonte.</p>
            </div>
            
            {# Col 2: Link Rapidi #}
            <nav aria-label="{% trans %}Link rapidi{% endtrans %}">
                <h3 class="text-gold font-heading font-bold mb-4">{% trans %}Link Rapidi{% endtrans %}</h3>
                <ul class="space-y-2 text-gray-400 text-sm">
                    <li><a href="/{{ request.LANGUAGE_CODE }}/chi-siamo/" class="hover:text-gold transition-colors">{% trans %}Chi Siamo{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/eventi/" class="hover:text-gold transition-colors">{% trans %}Eventi{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/galleria/" class="hover:text-gold transition-colors">{% trans %}Galleria{% endtrans %}</a></li>
                    <li><a href="/{{ request.LANGUAGE_CODE }}/contatti/" class="hover:text-gold transition-colors">{% trans %}Contatti{% endtrans %}</a></li>
                </ul>
            </nav>
            
            {# Col 3: Contatti #}
            <div>
                <h3 class="text-gold font-heading font-bold mb-4">{% trans %}Contatti{% endtrans %}</h3>
                <ul class="space-y-2 text-gray-400 text-sm">
                    <li><i class="fas fa-map-marker-alt text-gold mr-2"></i>Via Roma 45, Castellazzo Bormida</li>
                    <li><i class="fas fa-phone text-gold mr-2"></i>+39 0131 278945</li>
                    <li><i class="fas fa-envelope text-gold mr-2"></i>info@mccastellazzob.com</li>
                </ul>
            </div>
            
            {# Col 4: Social #}
            <div>
                <h3 class="text-gold font-heading font-bold mb-4">{% trans %}Seguici{% endtrans %}</h3>
                <div class="flex gap-4">
                    {% if settings.website.SiteSettings.facebook_url %}
                        <a href="{{ settings.website.SiteSettings.facebook_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition-all" aria-label="Facebook">
                            <i class="fab fa-facebook-f"></i>
                        </a>
                    {% endif %}
                    {% if settings.website.SiteSettings.instagram_url %}
                        <a href="{{ settings.website.SiteSettings.instagram_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition-all" aria-label="Instagram">
                            <i class="fab fa-instagram"></i>
                        </a>
                    {% endif %}
                    {% if settings.website.SiteSettings.youtube_url %}
                        <a href="{{ settings.website.SiteSettings.youtube_url }}" class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white hover:bg-gold hover:text-navy transition-all" aria-label="YouTube">
                            <i class="fab fa-youtube"></i>
                        </a>
                    {% endif %}
                </div>
            </div>
        </div>
        
        {# Footer Bottom #}
        <div class="border-t border-white/10 pt-8 text-center text-gray-500 text-sm">
            <p>{{ settings.website.SiteSettings.footer_text }}</p>
        </div>
    </div>
</footer>
```

---

## 5️⃣ Blocchi Wagtail per Contenuti

### 5.1 Hero Block

Crea `templates/website/blocks/hero_block.html`:

```jinja2
<section class="relative min-h-[60vh] flex items-center overflow-hidden" style="background: var(--gradient-hero);">
    <div class="absolute inset-0 bg-black/40"></div>
    {% if self.background_image %}
        <img src="{{ self.background_image.url }}" alt="" class="absolute inset-0 w-full h-full object-cover mix-blend-overlay">
    {% endif %}
    <div class="relative z-10 max-w-7xl mx-auto px-6 py-20 text-center text-white">
        <h1 class="text-4xl md:text-6xl font-heading font-bold mb-6" data-aos="fade-up">
            {{ self.title }}
        </h1>
        {% if self.subtitle %}
            <p class="text-xl md:text-2xl opacity-90 max-w-2xl mx-auto" data-aos="fade-up" data-aos-delay="100">
                {{ self.subtitle }}
            </p>
        {% endif %}
        {% if self.cta_text and self.cta_link %}
            <a href="{{ self.cta_link }}" class="inline-flex items-center gap-2 mt-8 px-8 py-4 bg-gold text-navy font-bold rounded-full hover:bg-white transition-all" data-aos="fade-up" data-aos-delay="200">
                {{ self.cta_text }}
                <i class="fas fa-arrow-right"></i>
            </a>
        {% endif %}
    </div>
</section>
```

### 5.2 Event Card Block

Crea/aggiorna `templates/website/blocks/event_card_block.html`:

```jinja2
<article class="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-gold transition-all duration-300 group" data-aos="fade-up">
    {% if self.image %}
        <div class="relative h-48 overflow-hidden">
            {{ image(self.image, "fill-400x200", class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500") }}
            <div class="absolute top-4 left-4 bg-gold text-navy px-3 py-1 rounded-full text-sm font-bold">
                {{ self.date|date("d M") }}
            </div>
        </div>
    {% endif %}
    <div class="p-6">
        <h3 class="text-xl font-heading font-bold text-navy mb-2">{{ self.title }}</h3>
        <p class="text-gray-600 text-sm mb-4">{{ self.description|truncatewords(20) }}</p>
        <div class="flex items-center text-sm text-gray-500">
            <i class="fas fa-map-marker-alt text-bordeaux mr-2"></i>
            {{ self.location }}
        </div>
    </div>
</article>
```

---

## 6️⃣ Aggiungere Tailwind CSS (Opzionale)

Se preferisci Tailwind compilato invece del CDN:

### 6.1 Installa Tailwind

```bash
npm init -y
npm install -D tailwindcss
npx tailwindcss init
```

### 6.2 Configura `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,jinja2}",
    "./motoclub-static/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'gold': '#ffd700',
        'gold-dark': '#f6c401',
        'bordeaux': '#ab0031',
        'navy': '#1B263B',
        'navy-light': '#2A3B52',
        'amaranth': '#9B1D64',
        'cream': '#FFF8E7',
      },
      fontFamily: {
        'heading': ['Montserrat', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### 6.3 Crea `static/css/input.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Importa stili custom */
@import './motoclub.css';
```

### 6.4 Build

```bash
npx tailwindcss -i static/css/input.css -o static/css/output.css --watch
```

---

## 7️⃣ Checklist Migrazione

### File da copiare
- [ ] `css/style.css` → `static/css/motoclub.css`
- [ ] `css/animations.css` → `static/css/animations.css`
- [ ] `js/main.js` → `static/js/motoclub.js`
- [ ] `images/MotoClubCastellazzoBormida-logo.webp` → `static/images/`

### Template da modificare
- [ ] `templates/website/base.jinja2` - head, navbar, footer
- [ ] Creare/aggiornare blocks per hero, cards, gallery

### Wagtail Admin
- [ ] Caricare logo in SiteSettings
- [ ] Configurare URL social media
- [ ] Impostare testo footer

### Test
- [ ] Verificare responsive (mobile, tablet, desktop)
- [ ] Testare accessibilità (WAVE, axe)
- [ ] Controllare contrasti colore
- [ ] Validare HTML

---

## 8️⃣ Estensioni SiteSettings (Opzionale)

Per gestire i colori da admin, estendi `SiteSettings`:

```python
# apps/website/models/settings.py

class SiteSettings(BaseGenericSetting):
    # ... campi esistenti ...
    
    # Colori personalizzabili
    primary_color = models.CharField(
        _("Colore Primario (Gold)"),
        max_length=7,
        default="#ffd700",
        help_text=_("Formato HEX, es. #ffd700")
    )
    
    secondary_color = models.CharField(
        _("Colore Secondario (Bordeaux)"),
        max_length=7,
        default="#ab0031",
    )
    
    navbar_style = models.CharField(
        _("Stile Navbar"),
        max_length=20,
        choices=[
            ('gradient', _('Gradiente Bordeaux-Navy')),
            ('solid-navy', _('Navy Solido')),
            ('transparent', _('Trasparente')),
        ],
        default='gradient',
    )
```

Poi nel template:

```jinja2
<style>
:root {
    --gold: {{ settings.website.SiteSettings.primary_color }};
    --bordeaux: {{ settings.website.SiteSettings.secondary_color }};
}
</style>
```

---

## 📚 Riferimenti

- [Documentazione Wagtail](https://docs.wagtail.org/)
- [CoderedCMS Docs](https://docs.coderedcorp.com/cms/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [motoclub-static/README.md](README.md) - Specifiche grafiche
- [motoclub-static/COLOR_SYSTEM.md](COLOR_SYSTEM.md) - Sistema colori

---

**MC Castellazzo Bormida** | Integrazione Wagtail v1.0 | Gennaio 2026
