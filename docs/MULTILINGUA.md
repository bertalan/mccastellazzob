# 🌐 Gestione Multilingua - mccastellazzob.com

Questo documento descrive l'implementazione del supporto multilingua nel sito.

## Lingue Supportate

| Codice | Lingua | Predefinita |
|--------|--------|-------------|
| `it` | Italiano | ✅ Sì |
| `en` | English | ❌ |
| `fr` | Français | ❌ |

---

## Configurazione Django/Wagtail

### Settings (`base.py`)

```python
# Lingua predefinita
LANGUAGE_CODE = "it"

# Abilita i18n in Wagtail
WAGTAIL_I18N_ENABLED = True
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Lingue permesse nell'admin
WAGTAILADMIN_PERMITTED_LANGUAGES = [
    ('it', 'Italiano'),
    ('en', 'English'),
    ('fr', 'French')
]

# Lingue contenuti (sincronizzate con LANGUAGES)
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
    ('it', "Italiano"),
    ('fr', 'French'),
]

# Sincronizza albero pagine tra lingue
WAGTAILSIMPLETRANSLATION_SYNC_PAGE_TREE = True
```

### Middleware

```python
MIDDLEWARE = [
    # ... altri middleware ...
    "django.middleware.locale.LocaleMiddleware",  # DEVE essere presente
]
```

### App Installate

```python
INSTALLED_APPS = [
    # ... 
    "wagtail.locales",                    # Gestione locali
    "wagtail.contrib.simple_translation", # Traduzione semplificata
]
```

---

## URL Multilingua

### Configurazione (`urls.py`)

```python
from django.conf.urls.i18n import i18n_patterns

# URL senza prefisso lingua
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(crx_admin_urls)),
    path("docs/", include(wagtaildocs_urls)),
]

# URL con prefisso lingua (es. /en/page, /fr/page)
# prefix_default_language=False: italiano senza prefisso (/)
urlpatterns += i18n_patterns(
    path('search/', localized_search, name='crx_search'),
    path("", include(crx_urls)),
    prefix_default_language=False,  # / = italiano, /en/ = inglese, /fr/ = francese
)
```

### Struttura URL risultante

| Lingua | URL Home | URL Pagina |
|--------|----------|------------|
| Italiano | `/` | `/chi-siamo/` |
| English | `/en/` | `/en/about-us/` |
| Français | `/fr/` | `/fr/a-propos/` |

---

## Context Processor

### File: `website/context_processors.py`

Fornisce `{{ current_language }}` in tutti i template.

```python
def current_language(request):
    lang_code = get_language()
    languages = dict(settings.WAGTAIL_CONTENT_LANGUAGES)
    default_language_code = settings.LANGUAGE_CODE[:2]
    return {
        'current_language': languages.get(lang_code, languages[default_language_code])
    }
```

**Uso nei template:**
```html
{% if current_language == "Italiano" %}...{% endif %}
```

---

## Modelli Traducibili

### Navbar e Footer

Entrambi usano `TranslatableMixin` per supporto multilingua:

```python
from wagtail.models import TranslatableMixin, Locale

class Navbar(TranslatableMixin, models.Model):
    class Meta:
        unique_together = [('translation_key', 'locale')]
    # ...

class Footer(TranslatableMixin, models.Model):
    class Meta:
        unique_together = [('translation_key', 'locale')]
    # ...
```

### Filtraggio nei Template

```html
{% load website_tags %}
{% get_website_navbars as navbars %}
{% for navbar in navbars %}
    {% if navbar.locale|striptags == current_language %}
        {# Mostra navbar della lingua corrente #}
    {% endif %}
{% endfor %}
```

---

## Ricerca Localizzata

### File: `website/views.py`

La ricerca filtra i risultati per lingua corrente:

```python
def localized_search(request):
    current_language = translation.get_language()
    current_locale = Locale.objects.get(language_code=current_language)
    results = Page.objects.live().filter(locale=current_locale)
    # ...
```

---

## Switcher Lingua (Navbar)

### Template: `snippets/navbar.html`

```html
{% for translation in page.get_translations.live %}
    <a href="{% pageurl translation %}" 
       rel="alternate" 
       hreflang="{{ translation.locale.language_code }}">
        {% if translation.locale.language_code == 'it' %}
            <img src="{% static 'website/svg/flag-it-40x30.svg' %}" alt="it">
        {% elif translation.locale.language_code == 'fr' %}
            <img src="{% static 'website/svg/flag-fr-40x30.svg' %}" alt="fr">
        {% else %}
            <img src="{% static 'website/svg/flag-en-40x30.svg' %}" alt="en">
        {% endif %}
    </a>
{% endfor %}
```

---

## File Statici per Lingue

```
website/static/website/svg/
├── flag-it-40x30.svg   # Bandiera Italia
├── flag-en-40x30.svg   # Bandiera UK/USA
└── flag-fr-40x30.svg   # Bandiera Francia
```

---

## Traduzioni Stringhe (gettext)

### Uso nei template

```html
{% load i18n %}
{% trans 'Search' %}
{% blocktrans %}Welcome to our site{% endblocktrans %}
```

### File .po/.mo

```
website/locale/
├── en/LC_MESSAGES/django.po
├── fr/LC_MESSAGES/django.po
└── it/LC_MESSAGES/django.po
```

### Comandi

```bash
# Estrai stringhe traducibili
python manage.py makemessages -l en -l fr -l it

# Compila traduzioni
python manage.py compilemessages
```

---

## Checklist Sviluppo Multilingua

- [ ] Creare pagine in tutte e tre le lingue
- [ ] Tradurre Navbar e Footer per ogni locale
- [ ] Verificare `prefix_default_language=False` (italiano senza /it/)
- [ ] Testare switcher lingua
- [ ] Verificare ricerca filtrata per lingua
- [ ] Compilare file `.po` se presenti stringhe traducibili

---

## Note per Docker (sviluppo)

Il file `docker.py` eredita le configurazioni i18n da `base.py`, quindi **non servono modifiche** per il supporto multilingua in ambiente Docker.

---

*Ultimo aggiornamento: Gennaio 2026*
