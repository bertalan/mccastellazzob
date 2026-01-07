# Proposta di Migrazione a CodeRedCMS 6.0 / Wagtail 7.0 LTS

> **DOCUMENTO DI PIANIFICAZIONE - NON ESEGUIRE SENZA APPROVAZIONE**
> 
> Data: Gennaio 2026
> Progetto: mccastellazzob.com - Moto Club Castellazzo Bormida
> Repository: https://github.com/bertalan/mccastellazzob
> Autore: Analisi automatizzata

---

## 📑 INDICE

1. [Sommario Esecutivo](#-sommario-esecutivo)
2. [Metodologia e Pratiche Moderne](#-metodologia-e-pratiche-moderne)
3. [Analisi CVE e Sicurezza](#-analisi-cve-e-sicurezza)
4. [Analisi Dipendenze Installate](#-analisi-dipendenze-installate)
5. [Ricostruzione Codebase](#-ricostruzione-codebase)
6. [Analisi Compatibilità Codice Custom](#-analisi-compatibilità-codice-custom)
7. [Breaking Changes](#-breaking-changes-coderedcms-60)
8. [Piano di Migrazione](#-piano-di-migrazione)
9. [Test-Driven Development (TDD)](#-test-driven-development-tdd)
10. [CI/CD Pipeline](#-cicd-pipeline---github-actions)
11. [Rollback e Checklist](#️-piano-di-rollback)

---

## 📋 SOMMARIO ESECUTIVO

### Versioni Coinvolte

| Componente | Versione Attuale | Versione Target | Note |
|------------|------------------|-----------------|------|
| **CodeRedCMS** | 5.0.* | 6.0.0 | Breaking changes minori |
| **Wagtail** | 6.4.* | 7.0 LTS | Long Term Support |
| **Django** | 5.1.7 | 5.2 LTS | Long Term Support |
| **Python** | 3.12 | 3.12 (compatibile 3.10-3.13) | Nessun cambiamento |

### Valutazione Rischio Generale

| Aspetto | Livello Rischio | Motivazione |
|---------|-----------------|-------------|
| Ricostruzione codebase | 🟡 MEDIO | Richiede attenzione ma funzionalità mappate |
| Modelli custom | 🟢 BASSO | TranslatableMixin stabile |
| View custom | 🟢 BASSO | localized_search usa API standard |
| Template tags | 🟢 BASSO | Implementazione semplice |
| Configurazione i18n | 🟢 BASSO | Pattern standard |
| Migrazione dati | 🟡 MEDIO | Verificare integrità referenziale |
| Dipendenze esterne | 🟢 BASSO | Tutte compatibili verificate |

### Stima Tempi

| Fase | Durata Stimata |
|------|----------------|
| Setup CI/CD e tooling | 2 ore |
| Ricostruzione codebase | 8-12 ore |
| Scrittura test (TDD) | 6-8 ore |
| Preparazione ambiente test | 2 ore |
| Aggiornamento dipendenze | 1 ora |
| Test e debug | 4-8 ore |
| Migrazione dati | 2-4 ore |
| Migrazione produzione | 1 ora |
| **TOTALE** | **26-38 ore** |

---

## 🛠️ METODOLOGIA E PRATICHE MODERNE

### Principi Guida

Questa migrazione adotta le seguenti pratiche di sviluppo moderno:

| Pratica | Strumento | Obbligatorietà |
|---------|-----------|----------------|
| **Test-Driven Development** | pytest + factory_boy | ✅ OBBLIGATORIO |
| **Security Scanning** | pip-audit, bandit | ✅ OBBLIGATORIO |
| **CI/CD Pipeline** | GitHub Actions | ✅ OBBLIGATORIO |
| **Type Hints** | mypy | 🟡 RACCOMANDATO |
| **Code Quality** | ruff, black, isort | ✅ OBBLIGATORIO |
| **Pre-commit Hooks** | pre-commit | ✅ OBBLIGATORIO |
| **Dependency Management** | pyproject.toml | ✅ OBBLIGATORIO |
| **Error Tracking** | Sentry | 🟡 RACCOMANDATO |
| **Structured Logging** | python-json-logger | 🟡 RACCOMANDATO |

### Stack di Testing

```
pytest                    # Framework di test principale
pytest-django            # Integrazione Django
pytest-cov               # Coverage report
factory_boy              # Factory per modelli (OBBLIGATORIO)
wagtail-factories        # Factory specifiche Wagtail
```

### Stack di Security

```
pip-audit                # Scansione CVE nelle dipendenze
bandit                   # Analisi statica sicurezza Python
safety                   # Controllo vulnerabilità (alternativa)
```

### Stack di Quality

```
ruff                     # Linter ultra-veloce (sostituisce flake8, isort, etc.)
black                    # Formatter Python
mypy                     # Type checking statico
pre-commit               # Hook pre-commit automatici
```

---

## 🔒 ANALISI CVE E SICUREZZA

### CVE Identificate nelle Versioni Attuali

Le seguenti vulnerabilità sono state identificate nelle versioni di Wagtail precedenti alla 7.0 e verranno risolte con l'aggiornamento:

#### 1. GHSA-jmp3-39vp-fwg8 - ReDoS via Search Query Parsing
- **Severità**: MODERATA
- **Data**: Luglio 2024
- **Descrizione**: Vulnerabilità Regular Expression Denial of Service nel parsing delle query di ricerca
- **Impatto su mccastellazzob.com**: POTENZIALE - Il sito usa `localized_search` con query utente
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

#### 2. GHSA-xxfm-vmcf-g33f - Improper Permissions in wagtail.contrib.settings
- **Severità**: MODERATA
- **Data**: Maggio 2024
- **Descrizione**: Problemi di permessi nel modulo settings
- **Impatto su mccastellazzob.com**: BASSO - Il sito usa SiteSettings ma solo in lettura
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

#### 3. GHSA-w2v8-php4-p8hc - Permission Bypass with Per-Field Restrictions
- **Severità**: BASSA
- **Data**: Maggio 2024
- **Descrizione**: Bypass delle restrizioni per campo
- **Impatto su mccastellazzob.com**: MINIMO - Gestione utenti limitata
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

#### 4. GHSA-fc75-58r8-rm3h - User Names Disclosure via Bulk Actions
- **Severità**: BASSA
- **Data**: Ottobre 2023
- **Descrizione**: Disclosure di nomi utente tramite azioni bulk
- **Impatto su mccastellazzob.com**: MINIMO - Pochi utenti admin
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

#### 5. GHSA-33pv-vcgh-jfg9 - DoS via Large File Uploads
- **Severità**: MODERATA
- **Data**: Aprile 2023
- **Descrizione**: Denial of Service tramite upload di file grandi
- **Impatto su mccastellazzob.com**: POTENZIALE - Il sito permette upload immagini
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

#### 6. GHSA-5286-f2rf-35c2 - Stored XSS via ModelAdmin
- **Severità**: MODERATA
- **Data**: Aprile 2023
- **Descrizione**: Cross-Site Scripting stored tramite ModelAdmin
- **Impatto su mccastellazzob.com**: BASSO - Uso limitato di ModelAdmin
- **Risoluzione**: Aggiornamento a Wagtail 7.0+

### Raccomandazione Sicurezza

⚠️ **SI RACCOMANDA FORTEMENTE L'AGGIORNAMENTO** a causa delle vulnerabilità ReDoS (ricerca) e DoS (upload) che potrebbero impattare l'operatività del sito.

### Scansione Continua con pip-audit e bandit

La migrazione implementerà scansione automatica di sicurezza:

#### pip-audit
Scansione CVE nelle dipendenze Python installate:
- Eseguito in CI/CD ad ogni push
- Blocca merge se trovate vulnerabilità critiche
- Report settimanale automatico

#### bandit
Analisi statica del codice Python per vulnerabilità:
- SQL Injection, XSS, Command Injection
- Uso insicuro di pickle, yaml, etc.
- Password hardcoded, debug mode in produzione
- Configurazione: file `.bandit.yaml` in root

---

## � ANALISI DIPENDENZE INSTALLATE

### Moduli Attualmente in Uso

I seguenti moduli sono installati nel progetto e richiedono verifica di compatibilità con lo stack target (CRX 6.0, Wagtail 7.0, Django 5.2):

| Pacchetto | Versione Attuale | Versione Target | Compatibilità | Note |
|-----------|------------------|-----------------|---------------|------|
| **coderedcms** | 5.0.* | 6.0.* | 🟢 Compatibile | Upgrade principale |
| **wagtail** | 6.4.* | ≥7.0,<7.2 | 🟢 Compatibile | LTS |
| **Django** | 5.1.7 | ≥5.2,<6.0 | 🟢 Compatibile | LTS |
| **django-bootstrap5** | (dipendenza CRX) | 26.x | 🟢 Compatibile | Rilascio Gen 2026, supporta Django 5.2 |
| **django-modelcluster** | (dipendenza Wagtail) | 6.4.1 | 🟢 Compatibile | Rilascio Dic 2025 |
| **django-taggit** | (dipendenza Wagtail) | latest | 🟢 Compatibile | Dipendenza transitiva |
| **wagtailcache** | (dipendenza CRX) | 3.0.0 | 🟢 Compatibile | Supporta Wagtail 7.x (Lug 2025) |
| **wagtailseo** | (dipendenza CRX) | 3.1.1 | 🟢 Compatibile | Supporta Wagtail 7.x (Lug 2025) |
| **wagtailgeowidget** | usato per OSM | 9.1.0 | 🟢 Compatibile | Supporta Wagtail 7.1+ (Nov 2025) |

### Dipendenze CodeRedCMS (Transitive)

CodeRedCMS 6.0 include automaticamente:
- `django-bootstrap5` - Form e componenti Bootstrap 5
- `modelcluster` - Gestione cluster di modelli
- `taggit` - Sistema di tagging
- `wagtailcache` - Cache per pagine Wagtail
- `wagtailseo` - SEO e meta tag

### Dipendenze Custom del Progetto

| Modulo | Uso nel Progetto | Compatibilità |
|--------|------------------|---------------|
| **wagtailgeowidget** | Mappe OpenStreetMap | 🟢 v9.1.0 compatibile con Wagtail 7.1+ |
| **wagtail.contrib.simple_translation** | Traduzioni IT/EN/FR | 🟢 Incluso in Wagtail core |
| **wagtail.locales** | Gestione locali | 🟢 Incluso in Wagtail core |

### App Custom del Progetto

| App | Descrizione | Compatibilità |
|-----|-------------|---------------|
| **website** | App principale con modelli custom | 🟢 Da testare |
| **custom_media** | Gestione media personalizzata | 🟢 Da testare |
| **custom_user** | Modello utente personalizzato | 🟢 Da testare |

### Aggiornamento requirements.txt

Le dipendenze devono essere aggiornate come segue:

```diff
# Consult release notes for supported versions of Django, Wagtail, and Python.
# https://docs.coderedcorp.com/wagtail-crx/releases/
- coderedcms==5.0.*
- wagtail==6.4.*
+ coderedcms>=6.0,<7.0
+ wagtail>=7.0,<7.2
+ Django>=5.2,<6.0

# Dipendenze esplicite per OpenStreetMap
+ wagtailgeowidget>=9.1.0
```

### Verifica Pre-Migrazione

Prima della migrazione, eseguire:
```bash
pip-audit -r requirements.txt
```

Questo verificherà che tutte le dipendenze siano prive di CVE note.

---

## 🔄 RICOSTRUZIONE CODEBASE

### Stato Attuale del Codice in /src

Il codice attuale in `/src/mccastellazzob/` presenta diverse problematiche che richiedono una **ricostruzione completa** mantenendo le funzionalità:

#### Problemi Identificati

| Problema | Descrizione | Impatto |
|----------|-------------|---------|
| **Commenti inline eccessivi** | Commenti `#PERSONALIZZAZIONE SYE`, `#FINE SYE` ovunque | Riduce leggibilità |
| **Mancanza type hints** | Nessuna annotazione di tipo | Difficoltà manutenzione |
| **Nessun docstring standard** | Documentazione inconsistente | Comprensione difficile |
| **Import disordinati** | Import non raggruppati/ordinati | Non conforme PEP8 |
| **Nessun test** | Zero test coverage | Rischio regressioni |
| **Codice duplicato** | Logica OSM ripetuta in EventPage e LocationPage | Violazione DRY |
| **Pattern non pythonic** | Manipolazione panel con `.remove()` e `next()` | Fragile e poco chiaro |
| **Sicurezza** | Nessuna validazione input in views | Potenziale vulnerabilità |

### Funzionalità da Preservare

Le seguenti funzionalità **DEVONO** essere mantenute nella ricostruzione:

#### 1. Modelli di Pagina (website/models.py)

| Modello | Funzionalità | Note Ricostruzione |
|---------|--------------|-------------------|
| `ArticlePage` | Pagine articolo/blog | Ereditare da CoderedArticlePage |
| `ArticleIndexPage` | Indice articoli | Ereditare da CoderedArticleIndexPage |
| `EventPage` | Eventi con OSM e JSON-LD | Rifattorizzare integrazione OSM |
| `EventIndexPage` | Indice eventi con JSON-LD | Mantenere schema.org |
| `EventOccurrence` | Occorrenze evento | ParentalKey standard |
| `FormPage` | Form con campi ed email | Ereditare da CoderedFormPage |
| `LocationPage` | Località con OSM e JSON-LD | Rifattorizzare integrazione OSM |
| `LocationIndexPage` | Indice località | Mantenere JSON-LD |
| `WebPage` | Pagine generiche | Ereditare da CoderedWebPage |

#### 2. Snippet Multilingua (website/models.py)

| Snippet | Funzionalità | Note Ricostruzione |
|---------|--------------|-------------------|
| `Navbar` | Navigazione multilingua | TranslatableMixin + unique_together |
| `Footer` | Footer multilingua | TranslatableMixin + unique_together |
| `NavbarLinkBlock` | Link singolo navbar | Ereditare da BaseLinkBlock |
| `NavbarDropdownBlock` | Dropdown navbar | Ereditare da BaseBlock |

#### 3. Blocchi Custom (website/blocks.py)

| Blocco | Funzionalità | Note Ricostruzione |
|--------|--------------|-------------------|
| `LatestContentBlock` | Lista ultimi contenuti (article/event/location) | Refactoring con type hints |
| `HTML_STREAMBLOCKS` (filtrato) | Blocchi HTML senza Google Maps | Rimuovere blocchi Google |
| `LAYOUT_STREAMBLOCKS` (filtrato) | Blocchi layout senza Google Maps | Rimuovere blocchi Google |

#### 4. View (website/views.py)

| View | Funzionalità | Note Ricostruzione |
|------|--------------|-------------------|
| `localized_search` | Ricerca filtrata per locale | Aggiungere validazione, type hints |

#### 5. Utility (website/utils.py)

| Funzione | Funzionalità | Note Ricostruzione |
|----------|--------------|-------------------|
| `get_schemaorg_json_ld` | Generazione JSON-LD schema.org | Type hints, docstring |
| `extract_text_from_streamfield` | Estrazione testo da StreamField | Esiste ma non visibile |

#### 6. Context Processor (website/context_processors.py)

| Funzione | Funzionalità | Note Ricostruzione |
|----------|--------------|-------------------|
| `current_language` | Lingua corrente per template | Semplificare logica |

#### 7. Template Tags (website/templatetags/website_tags.py)

| Tag | Funzionalità | Note Ricostruzione |
|-----|--------------|-------------------|
| `get_website_navbars` | Restituisce navbar | Aggiungere filtro locale |
| `get_website_footers` | Restituisce footer | Aggiungere filtro locale |

#### 8. Modelli Media (custom_media/models.py)

| Modello | Funzionalità | Note Ricostruzione |
|---------|--------------|-------------------|
| `CustomDocument` | Documento custom | Mantenere come da standard Wagtail |
| `CustomImage` | Immagine con campo credit | Mantenere campo credit |
| `CustomRendition` | Rendition per CustomImage | Relazione ForeignKey |

#### 9. Modelli Utente (custom_user/models.py)

| Modello | Funzionalità | Note Ricostruzione |
|---------|--------------|-------------------|
| `User` | Utente con email come identificatore | Mantenere logica email-based |
| `UserManager` | Manager custom per User | Mantenere create_user/create_superuser |

### Nuova Struttura Proposta

```
mccastellazzob/                    # Root progetto Django
├── pyproject.toml                 # Configurazione unificata
├── manage.py
├── conftest.py                    # Fixtures pytest globali
├── mccastellazzob/                # Package principale
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # Settings base
│   │   ├── dev.py                # Settings sviluppo (Docker)
│   │   ├── prod.py               # Settings produzione
│   │   └── test.py               # Settings test
│   ├── urls.py
│   └── wsgi.py
├── apps/                          # App Django organizzate
│   ├── __init__.py
│   ├── core/                      # Utility condivise
│   │   ├── __init__.py
│   │   ├── mixins.py             # Mixin OpenStreetMap, JSON-LD
│   │   ├── schema.py             # Generazione schema.org
│   │   └── validators.py         # Validatori custom
│   ├── website/                   # App principale
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/               # Modelli separati per tipo
│   │   │   ├── __init__.py
│   │   │   ├── pages.py          # ArticlePage, EventPage, etc.
│   │   │   └── snippets.py       # Navbar, Footer
│   │   ├── blocks.py
│   │   ├── views.py
│   │   ├── context_processors.py
│   │   ├── templatetags/
│   │   │   ├── __init__.py
│   │   │   └── website_tags.py
│   │   ├── templates/
│   │   └── static/
│   ├── media/                     # Custom media (ex custom_media)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── models.py
│   └── users/                     # Custom user (ex custom_user)
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       └── admin.py
├── tests/                         # Test separati per app
│   ├── __init__.py
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   ├── snippets.py
│   │   └── users.py
│   ├── test_models/
│   ├── test_views/
│   ├── test_blocks/
│   └── test_integration/
├── templates/                     # Template globali
│   └── coderedcms/               # Override template CRX
├── static/                        # Static files globali
└── media/                         # Upload directory
```

### Principi di Ricostruzione

#### 1. Separazione Responsabilità
- Mixin `OpenStreetMapMixin` per logica OSM condivisa
- Classe `SchemaOrgGenerator` per generazione JSON-LD
- Validatori separati in modulo dedicato

#### 2. Type Hints Ovunque
- Tutti i metodi con annotazioni di tipo
- Uso di `typing.TYPE_CHECKING` per import circolari
- Validazione con mypy in CI

#### 3. Docstring Standard
- Formato Google o NumPy per docstring
- Documentazione automatica con Sphinx (opzionale)

#### 4. Import Organizzati
- Ordinamento con isort/ruff
- Raggruppamento: stdlib → third-party → local

#### 5. Pattern Puliti
- No manipolazione dinamica panel con `.remove()`
- Definizione esplicita `content_panels` completa
- Uso di classi base custom invece di ereditarietà fragile

#### 6. Sicurezza
- Validazione input in tutte le view
- Escape output in template
- Rate limiting su form e ricerca

### Migrazioni Database

Le migrazioni esistenti in `/src/mccastellazzob/*/migrations/` **NON saranno riutilizzate**.

**Strategia migrazioni**:
1. Esportare dati da database attuale
2. Creare nuove migrazioni dal codice ricostruito
3. Importare dati nel nuovo schema
4. Verificare integrità referenziale

### File da Mantenere As-Is

| File | Motivazione |
|------|-------------|
| `media/*` | File upload degli utenti |
| `static/*` | Asset statici (CSS, JS, immagini) |
| `.well-known/*` | Configurazioni domain verification |
| `templates/coderedcms/*` | Template override esistenti |
| `templates/website/*` | Template custom esistenti |

### File da Eliminare

| File/Directory | Motivazione |
|----------------|-------------|
| `__pycache__/` | Cache Python |
| `*.pyc` | Bytecode compilato |
| `.cr.ini` | Configurazione obsoleta |
| `migrations/` (tutti) | Ricreare da zero |

---

## �🔍 ANALISI COMPATIBILITÀ CODICE CUSTOM

### 1. Modelli Custom (website/models.py)

#### Navbar e Footer con TranslatableMixin

**Stato**: 🟢 COMPATIBILE

**Analisi**:
- `TranslatableMixin` è stabile e mantiene la stessa API in Wagtail 7.0
- La dichiarazione `unique_together = [('translation_key', 'locale')]` è ancora supportata
- Si raccomanda di valutare la migrazione futura a `UniqueConstraint` (non obbligatoria)

**Elementi da verificare post-migrazione**:
- I modelli Navbar e Footer esistenti continuino a funzionare
- Le relazioni con le traduzioni siano intatte
- I pannelli di amministrazione siano accessibili

**Note Wagtail 7.0**:
- Nuovo supporto per `UniqueConstraint` su modelli rendition (opzionale)
- Nessun breaking change su TranslatableMixin

---

### 2. View Custom (website/views.py)

#### localized_search

**Stato**: 🟢 COMPATIBILE CON VERIFICA

**Analisi**:
La funzione `localized_search` utilizza:
- `Locale.objects.get(language_code=...)` - API stabile
- `Page.objects.live().search(query)` - API stabile
- Filtraggio per locale - Pattern standard

**Potenziali impatti CVE**:
- La CVE GHSA-jmp3-39vp-fwg8 (ReDoS) riguarda il parsing delle query di ricerca
- La funzione `localized_search` potrebbe essere stata vulnerabile
- L'aggiornamento risolve automaticamente questo problema

**Elementi da verificare post-migrazione**:
- La ricerca funzioni correttamente in tutte e 3 le lingue (IT, EN, FR)
- Le performance di ricerca siano comparabili o migliori
- Nessun errore su query complesse o malformate

**Novità Wagtail 7.0**:
- Miglioramento del tokenizer Elasticsearch (default a "standard")
- Supporto migliorato per subquery con lookup "in" e "exact" su Elasticsearch

---

### 3. Context Processors (website/context_processors.py)

#### current_language

**Stato**: 🟢 COMPATIBILE

**Analisi**:
- Utilizza `get_language()` da `django.utils.translation` - API Django stabile
- Pattern semplice senza dipendenze Wagtail specifiche
- Nessun cambiamento richiesto

---

### 4. Template Tags (website/templatetags/website_tags.py)

#### get_website_navbars e get_website_footers

**Stato**: 🟢 COMPATIBILE

**Analisi**:
- Query standard su modelli snippet
- Filtraggio per locale tramite API stabile
- Pattern comune e documentato

**Elementi da verificare post-migrazione**:
- I template tags restituiscano correttamente i dati
- Il filtraggio per locale funzioni
- Nessun errore nei template

---

### 5. Configurazione URL (mccastellazzob/urls.py)

#### i18n_patterns

**Stato**: 🟢 COMPATIBILE

**Analisi**:
- `i18n_patterns` con `prefix_default_language=False` è pattern standard Django
- La configurazione attuale (IT senza prefisso, EN/FR con prefisso) è stabile
- Nessun breaking change in Django 5.2 o Wagtail 7.0

---

### 6. Impostazioni (settings/base.py)

#### Configurazione CRX

**Stato**: 🟡 DA VERIFICARE

**Elementi specifici**:

| Setting | Stato | Azione |
|---------|-------|--------|
| `CRX_DISABLE_NAVBAR = True` | 🟢 Compatibile | Nessuna |
| `CRX_DISABLE_FOOTER = True` | 🟢 Compatibile | Nessuna |
| `WAGTAIL_I18N_ENABLED = True` | 🟢 Compatibile | Nessuna |
| `WAGTAIL_CONTENT_LANGUAGES` | 🟢 Compatibile | Nessuna |

**Setting da rinominare (deprecazione)**:

| Setting Attuale | Nuovo Nome | Urgenza |
|-----------------|------------|---------|
| `TAG_LIMIT` (se usato) | `WAGTAIL_TAG_LIMIT` | 🟡 Medio termine |
| `TAG_SPACES_ALLOWED` (se usato) | `WAGTAIL_TAG_SPACES_ALLOWED` | 🟡 Medio termine |

**Setting rimossi in Wagtail 7.0** (verificare se presenti):

| Setting | Sostituzione |
|---------|--------------|
| `WAGTAIL_AUTO_UPDATE_PREVIEW` | `WAGTAIL_AUTO_UPDATE_PREVIEW_INTERVAL = 0` |
| `PASSWORD_REQUIRED_TEMPLATE` | `WAGTAIL_PASSWORD_REQUIRED_TEMPLATE` |
| `DOCUMENT_PASSWORD_REQUIRED_TEMPLATE` | `WAGTAILDOCS_PASSWORD_REQUIRED_TEMPLATE` |
| `WAGTAIL_USER_EDIT_FORM` | Personalizzazione via `UserViewSet.get_form_class()` |
| `WAGTAIL_USER_CREATION_FORM` | Personalizzazione via `UserViewSet.get_form_class()` |
| `WAGTAIL_USER_CUSTOM_FIELDS` | Personalizzazione via `UserViewSet.get_form_class()` |

---

## 📚 BREAKING CHANGES CODEREDCMS 6.0

### Cambiamenti Principali

CRX 6.0 è compatibile con:
- Wagtail 7.0 - 7.1 (LTS)
- Django 5.2 LTS
- Python 3.10 - 3.13

### Elementi da Verificare

1. **Template CRX**: Verificare che i template custom non usino elementi deprecati
2. **Classi Page CRX**: Verificare compatibilità con le pagine ereditate da CodeRedCMS
3. **StreamField blocks**: Verificare che i blocchi custom funzionino correttamente

### Upgrade Path Consigliato da CRX

Seguire la documentazione ufficiale CRX per upgrade considerations:
- Prima aggiornare Wagtail seguendo le note di rilascio Wagtail 7.0
- Poi aggiornare CodeRedCMS a 6.0.0

---

## 📚 BREAKING CHANGES WAGTAIL 7.0

### Cambiamenti che Potrebbero Impattare il Progetto

#### 1. Validazione Differita per Bozze

**Impatto**: 🟢 BENEFICO

Wagtail 7.0 introduce la validazione differita: i campi obbligatori non sono più richiesti quando si salva come bozza. Questo è un miglioramento per l'esperienza utente.

**Azione richiesta**:
- Se alcuni campi DEVONO essere sempre obbligatori (anche in bozza), aggiungere `required_on_save = True`
- Generalmente non richiede modifiche

#### 2. Page.save() Non Chiama Più full_clean per Bozze

**Impatto**: 🟢 BASSO

Se il codice crea pagine bozza programmaticamente e richiede validazione completa, deve ora chiamare esplicitamente `full_clean()`.

**Azione richiesta**:
- Verificare se esistono script o importazioni che creano pagine bozza
- Se sì, aggiungere chiamate esplicite a `full_clean()` dove necessario

#### 3. Menu Snippets Mostra Solo Modelli Senza Menu Item

**Impatto**: 🟢 NESSUNO

I modelli Navbar e Footer usano implementazione custom, non sono nel menu Snippets standard.

#### 4. Rimozione Attributo classnames

**Impatto**: 🟡 DA VERIFICARE

Se sono presenti personalizzazioni di menu con `classnames`, rinominare in `classname`.

**Classi interessate**:
- `admin.menu.MenuItem`
- `admin.ui.sidebar.ActionMenuItem`
- `admin.ui.sidebar.LinkMenuItem`
- `admin.ui.sidebar.PageExplorerMenuItem`
- `contrib.settings.registry.SettingMenuItem`
- `wagtail.images.formats.Format`

---

## 📝 PIANO DI MIGRAZIONE

### FASE 1: PREPARAZIONE (Pre-migrazione)

#### 1.1 Backup Completo
- [ ] Eseguire backup completo del database PostgreSQL
- [ ] Eseguire backup della cartella media
- [ ] Eseguire backup del codice sorgente
- [ ] Verificare che i backup siano ripristinabili

#### 1.2 Ambiente di Test
- [ ] Creare branch Git dedicato per la migrazione
- [ ] Preparare ambiente Docker con nuove versioni
- [ ] Importare copia del database di produzione
- [ ] Verificare che l'ambiente di test funzioni con le versioni attuali

#### 1.3 Inventario Dipendenze
- [ ] Documentare tutte le dipendenze in requirements.txt
- [ ] Verificare compatibilità di ogni pacchetto con Django 5.2 e Wagtail 7.0
- [ ] Identificare pacchetti che richiedono aggiornamento

---

### FASE 2: AGGIORNAMENTO DIPENDENZE

#### 2.1 Ordine di Aggiornamento

1. **Django** → 5.2 LTS
2. **Wagtail** → 7.0 LTS (o 7.1 se disponibile)
3. **CodeRedCMS** → 6.0.0
4. **Altre dipendenze** → versioni compatibili

#### 2.2 Aggiornamento requirements.txt

Modifiche da apportare:
```
# DA:
coderedcms==5.0.*
wagtail==6.4.*
Django>=5.1,<5.2

# A:
coderedcms==6.0.*
wagtail>=7.0,<7.2
Django>=5.2,<6.0
```

#### 2.3 Verifica Impostazioni

- [ ] Controllare settings/base.py per setting deprecati
- [ ] Rinominare TAG_LIMIT → WAGTAIL_TAG_LIMIT (se presente)
- [ ] Rinominare TAG_SPACES_ALLOWED → WAGTAIL_TAG_SPACES_ALLOWED (se presente)
- [ ] Verificare e aggiornare altri setting se necessario

---

### FASE 3: MIGRAZIONI DATABASE

#### 3.1 Esecuzione Migrazioni
- [ ] Eseguire `python manage.py makemigrations` (se necessario)
- [ ] Eseguire `python manage.py migrate`
- [ ] Verificare che non ci siano errori

#### 3.2 Verifica Integrità Dati
- [ ] Verificare che le pagine esistenti siano accessibili
- [ ] Verificare che le traduzioni (IT, EN, FR) siano intatte
- [ ] Verificare che Navbar e Footer funzionino in tutte le lingue
- [ ] Verificare che le immagini e i documenti siano accessibili

---

### FASE 4: TEST AUTOMATIZZATI (TDD)

> ⚠️ **I TEST SONO OBBLIGATORI PRIMA DEL DEPLOY**

#### 4.1 Esecuzione Suite di Test
- [ ] Eseguire `pytest` con coverage minimo 80%
- [ ] Tutti i test devono passare (zero failures)
- [ ] Verificare report coverage

#### 4.2 Test Frontend
- [ ] Navigazione homepage in italiano (senza prefisso)
- [ ] Navigazione pagine in inglese (/en/...)
- [ ] Navigazione pagine in francese (/fr/...)
- [ ] Cambio lingua tramite language switcher
- [ ] Visualizzazione Navbar localizzata
- [ ] Visualizzazione Footer localizzato
- [ ] Funzionalità di ricerca in tutte le lingue
- [ ] Visualizzazione immagini e gallery
- [ ] Form di contatto (se presente)

#### 4.3 Test Backend Admin
- [ ] Login all'admin Wagtail
- [ ] Creazione/modifica pagine
- [ ] Gestione traduzioni pagine
- [ ] Gestione Navbar (snippet)
- [ ] Gestione Footer (snippet)
- [ ] Upload immagini
- [ ] Upload documenti
- [ ] Pubblicazione e scheduling

#### 4.4 Test Performance
- [ ] Tempo di caricamento homepage
- [ ] Tempo di risposta ricerca
- [ ] Verifica assenza errori console browser
- [ ] Verifica assenza errori log server

---

### FASE 5: SECURITY SCAN

> ⚠️ **SCAN OBBLIGATORI PRIMA DEL DEPLOY**

#### 5.1 pip-audit
- [ ] Eseguire `pip-audit` su requirements
- [ ] Zero vulnerabilità critiche o alte
- [ ] Documentare eventuali vulnerabilità accettate (con giustificazione)

#### 5.2 bandit
- [ ] Eseguire `bandit -r src/` 
- [ ] Zero issue di severità HIGH
- [ ] Review issue MEDIUM e documentare eccezioni

---

### FASE 6: MIGRAZIONE PRODUZIONE

#### 6.1 Pre-requisiti CI/CD
- [ ] Pipeline GitHub Actions verde (tutti i check passano)
- [ ] Coverage test ≥ 80%
- [ ] pip-audit: zero vulnerabilità critiche
- [ ] bandit: zero issue HIGH

#### 5.1 Preparazione
- [ ] Pipeline CI/CD verde (OBBLIGATORIO)
- [ ] Pianificare finestra di manutenzione
- [ ] Comunicare ai gestori del sito
- [ ] Preparare script di rollback
- [ ] Verificare accesso SSH al server

#### 5.2 Esecuzione
- [ ] Attivare pagina di manutenzione
- [ ] Backup finale database produzione
- [ ] Pull del codice aggiornato
- [ ] Aggiornamento virtualenv con nuove dipendenze
- [ ] Esecuzione migrazioni database
- [ ] Collectstatic
- [ ] Restart servizi (gunicorn)
- [ ] Verifica funzionamento
- [ ] Disattivare pagina di manutenzione

#### 5.3 Monitoraggio Post-Deploy
- [ ] Monitorare log errori per 24-48 ore
- [ ] Verificare funzionalità critiche
- [ ] Essere pronti a rollback se necessario

---

## ⚠️ PIANO DI ROLLBACK

In caso di problemi critici durante la migrazione:

### Rollback Immediato

1. **Ripristino database**: Utilizzare il backup pre-migrazione
2. **Ripristino codice**: Git checkout al commit precedente
3. **Ripristino virtualenv**: Reinstallare requirements.txt precedente
4. **Restart servizi**: Riavviare gunicorn/nginx

### Comandi di Rollback

```bash
# 1. Stop servizi
sudo systemctl stop gunicornmccastellazzob.service

# 2. Ripristino database (esempio)
pg_restore -d mccastellazzob_db backup_pre_migrazione.dump

# 3. Ripristino codice
git checkout main  # o branch stabile precedente

# 4. Ripristino dipendenze
pip install -r requirements.txt

# 5. Restart servizi
sudo systemctl start gunicornmccastellazzob.service
```

---

## 📋 CHECKLIST FINALE

### Pre-Migrazione
- [ ] Backup database completo e testato
- [ ] Backup media files
- [ ] Backup codice (Git)
- [ ] Ambiente test funzionante
- [ ] Tutte le dipendenze verificate

### Durante Migrazione
- [ ] Aggiornamento requirements.txt
- [ ] Esecuzione pip install
- [ ] Esecuzione migrazioni Django
- [ ] Verifica setting deprecati

### Post-Migrazione
- [ ] Test frontend tutte le lingue
- [ ] Test admin Wagtail
- [ ] Test ricerca
- [ ] Test upload media
- [ ] Monitoraggio errori

### Produzione
- [ ] Deploy completato
- [ ] Monitoraggio 24-48 ore
- [ ] Documentazione aggiornata
- [ ] Team informato

---

## 📞 RISORSE E RIFERIMENTI

### Documentazione Ufficiale
- [CodeRedCMS 6.0 Release Notes](https://docs.coderedcorp.com/wagtail-crx/releases/)
- [Wagtail 7.0 Release Notes](https://docs.wagtail.org/en/stable/releases/7.0.html)
- [Django 5.2 Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [Wagtail Upgrade Guide](https://docs.wagtail.org/en/stable/releases/upgrading.html)

### Security Advisories
- [Wagtail Security Advisories](https://github.com/wagtail/wagtail/security/advisories)

### Repository Progetto
- [GitHub mccastellazzob](https://github.com/bertalan/mccastellazzob)

### Community
- [Wagtail Slack](https://wagtail.org/slack/)
- [CodeRedCMS GitHub](https://github.com/coderedcorp/coderedcms)

---

## 🧪 TEST-DRIVEN DEVELOPMENT (TDD)

### Filosofia TDD per la Migrazione

> **REGOLA FONDAMENTALE**: Nessun codice di migrazione viene scritto senza test che lo preceda.

Il ciclo TDD da seguire:
1. **RED**: Scrivere un test che fallisce
2. **GREEN**: Scrivere il codice minimo per far passare il test
3. **REFACTOR**: Migliorare il codice mantenendo i test verdi

### Struttura Directory Test

```
src/mccastellazzob/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest condivise
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── page_factories.py    # Factory per pagine CRX
│   │   ├── snippet_factories.py # Factory per Navbar/Footer
│   │   └── user_factories.py    # Factory per utenti
│   ├── test_models.py           # Test modelli custom
│   ├── test_views.py            # Test view (localized_search)
│   ├── test_templatetags.py     # Test template tags
│   ├── test_i18n.py             # Test internazionalizzazione
│   └── test_integration.py      # Test integrazione end-to-end
```

### Factory Boy - Factories Richieste

#### NavbarFactory
- Crea istanze Navbar con TranslatableMixin
- Supporta creazione traduzioni IT/EN/FR
- Gestisce menu_items e link

#### FooterFactory  
- Crea istanze Footer con TranslatableMixin
- Supporta creazione traduzioni IT/EN/FR
- Gestisce sezioni footer

#### PageFactory (da wagtail-factories)
- Estende WagtailPageFactory
- Crea pagine CRX con contenuto localizzato
- Supporta StreamField popolati

### Test Suite Minima Obbligatoria

#### Test Modelli (test_models.py)
| Test | Descrizione |
|------|-------------|
| `test_navbar_creation` | Creazione Navbar base |
| `test_navbar_translation` | Navbar con traduzioni IT/EN/FR |
| `test_navbar_unique_constraint` | Vincolo translation_key + locale |
| `test_footer_creation` | Creazione Footer base |
| `test_footer_translation` | Footer con traduzioni IT/EN/FR |

#### Test View (test_views.py)
| Test | Descrizione |
|------|-------------|
| `test_localized_search_italian` | Ricerca in italiano |
| `test_localized_search_english` | Ricerca in inglese |
| `test_localized_search_french` | Ricerca in francese |
| `test_localized_search_empty_query` | Query vuota |
| `test_localized_search_no_results` | Nessun risultato |
| `test_localized_search_special_chars` | Caratteri speciali (CVE fix) |

#### Test Template Tags (test_templatetags.py)
| Test | Descrizione |
|------|-------------|
| `test_get_website_navbars_italian` | Navbar per IT |
| `test_get_website_navbars_english` | Navbar per EN |
| `test_get_website_footers_italian` | Footer per IT |
| `test_get_website_footers_english` | Footer per EN |

#### Test i18n (test_i18n.py)
| Test | Descrizione |
|------|-------------|
| `test_italian_no_prefix` | IT senza prefisso URL |
| `test_english_with_prefix` | EN con prefisso /en/ |
| `test_french_with_prefix` | FR con prefisso /fr/ |
| `test_language_switching` | Cambio lingua |
| `test_context_processor_language` | current_language context |

### Configurazione pytest

File: `pytest.ini` o sezione in `pyproject.toml`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = mccastellazzob.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=website
    --cov=mccastellazzob
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
filterwarnings =
    ignore::DeprecationWarning
```

### Coverage Minima

| Area | Coverage Minimo |
|------|-----------------|
| `website/models.py` | 90% |
| `website/views.py` | 85% |
| `website/templatetags/` | 80% |
| `website/context_processors.py` | 100% |
| **TOTALE** | **≥ 80%** |

---

## 🔄 CI/CD PIPELINE - GITHUB ACTIONS

### Workflow Principale

File: `.github/workflows/ci.yml`

Il workflow eseguirà i seguenti job ad ogni push/PR:

#### Job 1: Lint & Format
- ruff (linting)
- black --check (formatting)
- isort --check (import sorting)

#### Job 2: Type Check
- mypy (analisi statica tipi)

#### Job 3: Security Scan
- pip-audit (CVE dipendenze)
- bandit (vulnerabilità codice)

#### Job 4: Test
- pytest con coverage
- Report coverage su PR
- Fail se coverage < 80%

#### Job 5: Build Docker (opzionale)
- Build immagine Docker
- Test container

### Branch Protection Rules

Configurare su GitHub:
- `main` branch protetto
- Richiede PR per merge
- Richiede review approvata
- Richiede CI verde (tutti i check passano)
- No force push

### Secrets GitHub

| Secret | Descrizione |
|--------|-------------|
| `SENTRY_DSN` | DSN per error tracking (opzionale) |
| `CODECOV_TOKEN` | Token per coverage report (opzionale) |

---

## 📁 NUOVI FILE DA CREARE

### File di Configurazione

| File | Scopo |
|------|-------|
| `pyproject.toml` | Configurazione unificata progetto |
| `.pre-commit-config.yaml` | Hook pre-commit |
| `.github/workflows/ci.yml` | Pipeline CI/CD |
| `.bandit.yaml` | Configurazione bandit |
| `src/mccastellazzob/tests/conftest.py` | Fixtures pytest |
| `src/mccastellazzob/tests/factories/*.py` | Factory boy factories |

### Struttura pyproject.toml

```toml
[project]
name = "mccastellazzob"
version = "2.0.0"
requires-python = ">=3.10"
dependencies = [
    "coderedcms>=6.0,<7.0",
    "wagtail>=7.0,<7.2",
    "Django>=5.2,<6.0",
    # ... altre dipendenze
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "pytest-cov>=4.1",
    "factory-boy>=3.3",
    "wagtail-factories>=4.1",
    "ruff>=0.1",
    "black>=24.0",
    "mypy>=1.8",
    "pre-commit>=3.6",
    "pip-audit>=2.7",
    "bandit>=1.7",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "mccastellazzob.settings.test"
python_files = ["test_*.py"]
addopts = "--cov=website --cov-fail-under=80"

[tool.coverage.run]
source = ["website", "mccastellazzob"]
omit = ["*/migrations/*", "*/tests/*"]
```

---

> **NOTA IMPORTANTE**: Questo documento è stato creato come proposta di migrazione.
> Non eseguire alcuna modifica al codice prima dell'approvazione esplicita.
> 
> Per procedere con l'implementazione, confermare l'approvazione e indicare
> eventuali priorità o modifiche al piano proposto.

---

## 📋 CHECKLIST APPROVAZIONE

Prima di procedere con l'implementazione, confermare:

### Metodologia
- [ ] **TDD obbligatorio** con factory_boy ✅
- [ ] **pip-audit** per CVE scanning ✅
- [ ] **bandit** per security analysis ✅
- [ ] **GitHub Actions** CI/CD ✅
- [ ] **pre-commit hooks** ✅
- [ ] **pyproject.toml** invece di requirements.txt ✅
- [ ] **ruff + black** per code quality ✅
- [ ] Coverage minimo 80% ✅

### Repository
- [ ] GitHub: https://github.com/bertalan/mccastellazzob ✅
- [ ] Branch protection su `main`
- [ ] Require PR reviews

### Opzionali (da confermare)
- [ ] Sentry per error tracking
- [ ] mypy per type checking strict
- [ ] Structured logging JSON

---

**STATO**: ⏳ IN ATTESA DI APPROVAZIONE

Dopo l'approvazione procederò con:
1. Creazione file di configurazione (pyproject.toml, pre-commit, CI/CD)
2. Setup struttura test con factory_boy
3. Scrittura test suite secondo TDD
4. Aggiornamento dipendenze
5. Esecuzione migrazione
