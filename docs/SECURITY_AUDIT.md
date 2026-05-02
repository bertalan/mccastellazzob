# Security Audit Report — MC Castellazzo
**Data:** 2 maggio 2026  
**Metodologia:** OWASP Top 10 (2021), analisi statica del codice sorgente  
**Scope:** Django 5.2 / Wagtail 7.x, settings, views, models, templates, Docker  
**Stato:** Solo analisi — nessuna modifica al codice  

---

## Executive Summary

Il progetto presenta **buone pratiche di base**: CSRF attivo, ORM parametrizzato, HSTS in produzione, password validation, session cookie secure. Tuttavia sono stati identificati **16 finding** che spaziano da un Critico (fallback SECRET_KEY) a diversi High su IDOR, SSRF, XSS e configurazione Docker.

| Severity | Count |
|---|---|
| 🔴 Critical | 1 |
| 🟠 High | 6 |
| 🟡 Medium | 6 |
| 🟢 Low / Info | 3 |

---

## Positivi riscontrati

- ✅ CSRF middleware attivo e applicato su tutti i form
- ✅ Nessun raw SQL — solo ORM Django (query parametrizzate)
- ✅ Password validation: 4 validator attivi (min length, common, numeric, similarity)
- ✅ Produzione: `SECURE_HSTS_SECONDS=31536000`, `SECURE_HSTS_PRELOAD=True`, `SECURE_SSL_REDIRECT=True`
- ✅ `X_FRAME_OPTIONS = "DENY"` in produzione
- ✅ `SESSION_COOKIE_SECURE = True` in produzione
- ✅ Jinja2 con autoescape attivo per default
- ✅ `@staff_member_required` e `@permission_required` usati sulle view admin

---

## Findings Dettagliati

---

### 🔴 CRITICAL

#### SEC-001 — Fallback SECRET_KEY con valore statico
**OWASP:** A02 – Cryptographic Failures  
**File:** `mccastellazzob/settings/base.py:18`

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-production")
```

Se la variabile d'ambiente `SECRET_KEY` non è impostata, Django utilizza la stringa letterale `"changeme-in-production"`. Questo invalida tutte le firme crittografiche di Django (session cookies, CSRF tokens, password reset links, signed URLs). Un attaccante che conosca questa chiave può forgiare sessioni e token.

**Raccomandazione:** Rimuovere il fallback. Far crashare il processo di startup se `SECRET_KEY` non è presente:
```python
SECRET_KEY = os.environ["SECRET_KEY"]  # raise KeyError se mancante
```

---

### 🟠 HIGH

#### SEC-002 — DEBUG default a `True` in Docker settings
**OWASP:** A05 – Security Misconfiguration  
**File:** `mccastellazzob/settings/docker.py`

```python
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
```

Le impostazioni Docker hanno `DEBUG=True` come default. In caso di deploy Docker senza impostare esplicitamente `DEBUG=False` nell'ambiente, Django mostra stack trace completi, variabili d'ambiente, configurazione SQL a qualsiasi utente che genera un errore 500.

**Raccomandazione:** Invertire il default: `os.environ.get("DEBUG", "False")`.

---

#### SEC-003 — IDOR su `get_image_metadata` (solo `@login_required`)
**OWASP:** A01 – Broken Access Control  
**File:** `apps/core/admin_views.py:166-174`

```python
@login_required
@require_GET
def get_image_metadata(request, image_id):
    ...
    image = Image.objects.get(pk=image_id)
```

L'endpoint è protetto da `@login_required` ma **non verifica che l'utente autenticato abbia il permesso di vedere quella specifica immagine**. Qualsiasi utente autenticato (anche un semplice membro registrato) può enumerare tutti gli ID immagine e leggere metadati (titolo, dimensioni, URL) di immagini caricate da altri.

**Raccomandazione:** Aggiungere il filtro per collection permission di Wagtail:
```python
from wagtail.images.permissions import permission_policy
permission_policy.check_permission(request.user, 'choose')
```

---

#### SEC-004 — Mancanza di verifica permessi pagina in `auto_translate_page_view`
**OWASP:** A01 – Broken Access Control  
**File:** `apps/core/views.py:101-102`

```python
@staff_member_required
def auto_translate_page_view(request, page_id):
```

Un utente staff può inviare qualsiasi `page_id` e far tradurre pagine su cui non ha permesso di edit. Manca la verifica `page.permissions_for_user(request.user).can_edit()` prima di procedere.

**Raccomandazione:**
```python
page = get_object_or_404(Page, id=page_id).specific
perms = page.permissions_for_user(request.user)
if not perms.can_edit():
    raise PermissionDenied
```

---

#### SEC-005 — XSS via interpolazione non sicura in JavaScript (maps.py)
**OWASP:** A03 – Injection  
**File:** `apps/core/maps.py:85`

```python
marker_popup = f'.bindPopup("{marker_text}")' if marker_text else ""
```

Il valore `marker_text` viene interpolato direttamente in una stringa JavaScript senza escaping. Se `marker_text` contiene `"` o `\`, si rompe la stringa JS. Se il valore proviene da contenuto CMS editabile, un editor compromesso o malintenzionato può iniettare codice JavaScript.

**Raccomandazione:** Usare `json.dumps(marker_text)` per garantire escaping sicuro:
```python
import json
marker_popup = f'.bindPopup({json.dumps(marker_text)})' if marker_text else ""
```

---

#### SEC-006 — Password superuser Docker con default hardcoded
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `docker/entrypoint.sh`

```python
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')
```

Se `SUPERUSER_PASSWORD` non è impostata nell'ambiente Docker, il superuser viene creato con password `admin123`. In ambienti di staging/test dimenticati online questo è un vettore di attacco immediato.

**Raccomandazione:** Rimuovere il default e far fallire esplicitamente se la variabile non è impostata, oppure generare una password casuale che viene stampata una sola volta nei log.

---

#### SEC-007 — Nessun rate limiting su endpoint di traduzione automatica
**OWASP:** A04 – Insecure Design  
**File:** `apps/core/views.py`, `apps/core/machine_translator.py:238`

```python
# Ritardo tra le richieste per evitare rate limiting (in secondi)
```

Il ritardo da 0.5s è lato server e facilmente aggirabile con richieste parallele. Un utente staff può innescare centinaia di chiamate API verso servizi esterni (Google Translate, DeepL, MyMemory) in pochi secondi, causando:
- Sospensione account API
- Costi inattesi (se API a pagamento)
- DoS dell'endpoint di traduzione

**Raccomandazione:** Aggiungere `django-ratelimit` sulla view di traduzione.

---

### 🟡 MEDIUM

#### SEC-008 — `RawHTMLBlock` in StreamField (XSS potenziale)
**OWASP:** A03 – Injection  
**File:** `apps/website/blocks.py` (usato in NewsPage body)

`RawHTMLBlock` permette agli editor CMS di inserire HTML grezzo, inclusi tag `<script>`. Mentre gli editor sono utenti fidati, un account compromesso o un attacco di session hijacking su un editor potrebbe iniettare codice malevolo permanente nel sito.

**Raccomandazione:** Limitare il blocco agli utenti con permesso `superuser` via `wagtail_hooks`, o sostituirlo con `EmbedBlock` + whitelist.

---

#### SEC-009 — URL esterne non validate in `machine_translator.py` e `maps.py`
**OWASP:** A10 – SSRF  
**File:** `apps/core/machine_translator.py`, `apps/core/maps.py:25`

```python
requests.get(f"{base_url}/search", params={"q": address, ...})
```

`base_url` (es. `LIBRETRANSLATE_URL`, `NOMINATIM_URL`) arriva dai settings, ma se questi valori fossero compromessi (es. via variabile d'ambiente manipolata) potrebbero essere utilizzati per fare richieste verso servizi interni della rete del server. Nessuna whitelist di schemi/host.

**Raccomandazione:** Validare che `base_url` usi schema `https://` e appartengano a domini attesi; usare timeout espliciti su tutte le chiamate.

---

#### SEC-010 — Email verification opzionale + nessun rate limiting su signup/reset
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `mccastellazzob/settings/base.py:260`

```python
ACCOUNT_EMAIL_VERIFICATION = "optional"
```

Gli utenti possono registrarsi senza verificare l'email. Combinato con l'assenza di rate limiting (nessun `django-axes` né `django-ratelimit` configurato), i form di registrazione, login e password-reset sono vulnerabili a:
- Brute force sulle password
- Email enumeration via timing attack sul reset
- Registrazioni massive di account fasulli

**Raccomandazione:** Impostare `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` e configurare `django-axes` per lockout automatico.

---

#### SEC-011 — Dettagli eccezione esposti nei messaggi utente
**OWASP:** A09 – Security Logging and Monitoring  
**File:** `apps/core/admin_views.py:140`

```python
messages.error(request, _("Errore durante il caricamento: %(error)s") % {"error": str(e)})
```

`str(e)` può contenere path interni del filesystem, nomi di variabili, o informazioni sull'infrastruttura (es. `FileNotFoundError: /www/wwwroot/...`). Queste informazioni aiutano un attaccante a mappare l'ambiente.

**Raccomandazione:** Loggare `str(e)` solo nel logger server-side; mostrare all'utente un messaggio generico con un ID di correlazione.

---

#### SEC-012 — Nessun audit log per operazioni sensibili
**OWASP:** A09 – Security Logging and Monitoring  
**File:** `apps/core/admin_views.py`, `apps/core/views.py`

Le operazioni di bulk upload e traduzione automatica non producono una traccia di audit (chi, cosa, quando). In caso di incidente (upload di file malevoli, traduzione non autorizzata) non è possibile ricostruire la sequenza degli eventi.

**Raccomandazione:** Usare `LogEntry` di Django admin o un modello `AuditLog` custom per tracciare almeno: user, action, object_id, timestamp, IP.

---

### 🟢 LOW / INFO

#### SEC-013 — Content Security Policy (CSP) assente
**OWASP:** A05 – Security Misconfiguration  
**File:** `mccastellazzob/settings/prod.py`

Nessuna header `Content-Security-Policy` configurata. In assenza di CSP, qualsiasi XSS eseguito (es. tramite `RawHTMLBlock`) può caricare script da domini esterni.

**Raccomandazione:** Aggiungere `django-csp` con una policy restrictiva e modalità report-only iniziale.

---

#### SEC-014 — Nessun controllo automatico CVE sulle dipendenze
**OWASP:** A06 – Vulnerable Components  
**File:** `pyproject.toml`

Le dipendenze sono pinned a range di versione (`Django>=5.2,<5.3`) ma non esiste un meccanismo automatico (pre-commit hook, CI/CD) per rilevare CVE nuovi.

**Raccomandazione:** Aggiungere `pip-audit` o `safety` in un workflow CI/CD o pre-commit.

---

#### SEC-015 — `ALLOWED_HOSTS` con fallback a `localhost` in base.py
**OWASP:** A05 – Security Misconfiguration  
**File:** `mccastellazzob/settings/base.py:20`

```python
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

Il fallback non causa problemi diretti in produzione (dove `ALLOWED_HOSTS` è impostato correttamente), ma se un deploy intermedio dimenticasse la variabile, Django accetterebbe richieste con qualsiasi Host header (HTTP Host header injection).

**Raccomandazione:** Aggiungere un check esplicito che in production `DEBUG=False` implichi `ALLOWED_HOSTS` non-default.

---

## Piano di Remediation

| Priorità | ID | Effort |
|---|---|---|
| **Fase 1 — Subito** | SEC-001, SEC-002, SEC-006 | 1-2h |
| **Fase 2 — Settimana** | SEC-003, SEC-004, SEC-005, SEC-007 | 4-8h |
| **Fase 3 — Sprint** | SEC-008, SEC-009, SEC-010, SEC-011, SEC-012 | 1-2 giorni |
| **Fase 4 — Backlog** | SEC-013, SEC-014, SEC-015 | 2-4h |

---

## Nota

Questo documento è **solo un'analisi read-only** del codice sorgente. Nessuna modifica è stata apportata al codice. Tutti i finding sono basati su ispezione diretta dei file sorgente e modellazione delle minacce OWASP Top 10 (2021).

---

## Proposta di Remediation — Modifiche Concrete

Per ogni finding viene indicato: file da modificare, diff minimale proposto, e dipendenze aggiuntive se necessarie.  
**Nessuna modifica è ancora stata applicata al codice.**

---

### GRUPPO A — Configurazione (effort: 30 min totali)

#### A1 · SEC-001 — Rimuovere fallback SECRET_KEY
**File:** `mccastellazzob/settings/base.py:18`

```diff
- SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-production")
+ SECRET_KEY = os.environ["SECRET_KEY"]  # KeyError deliberato: env var obbligatoria
```

`prod.py` usa già `os.environ["SECRET_KEY"]` correttamente — questa modifica allinea `base.py`.  
Il fallback è già inutile in dev se si usa `.env` (già presente tramite `python-dotenv`).

---

#### A2 · SEC-002 — Invertire default DEBUG in docker.py
**File:** `mccastellazzob/settings/docker.py:8`

```diff
- DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
+ DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
```

Richiede aggiungere `DEBUG=True` nel `docker-compose.override.yml` di sviluppo locale (già presente).

---

#### A3 · SEC-006 — Rimuovere password hardcoded da entrypoint Docker
**File:** `docker/entrypoint.sh`

```diff
- password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')
+ password = os.environ.get('SUPERUSER_PASSWORD')
+ if not password:
+     import sys
+     print('ERROR: SUPERUSER_PASSWORD env var is required', file=sys.stderr)
+     sys.exit(1)
```

Alternativa più ergonomica: generare una password casuale alla prima esecuzione e stamparla nei log (una sola volta).

---

#### A4 · SEC-015 — ALLOWED_HOSTS fallback in base.py
**File:** `mccastellazzob/settings/base.py:20`

Non serve modificarlo perché `prod.py` e `docker.py` sovrascrivono già `ALLOWED_HOSTS`. La patch sicura è aggiungere un guard in `base.py` al posto del fallback largo:

```diff
- ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
+ _allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
+ ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]
```

Il comportamento è identico ma evita host vuoti se la variabile ha spazi.

---

### GRUPPO B — Access Control (effort: 2-3h)

#### B1 · SEC-003 — IDOR su `get_image_metadata`
**File:** `apps/core/admin_views.py:166`

Aggiungere il check permission di Wagtail prima di servire i dati:

```diff
 @login_required
 @require_GET
 def get_image_metadata(request, image_id):
+    from wagtail.images.permissions import permission_policy
+    if not permission_policy.user_has_any_permission(request.user, ["add", "change", "choose"]):
+        return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
     try:
         image = Image.objects.get(pk=image_id)
```

Questo limita l'endpoint agli utenti che hanno almeno un permesso immagine Wagtail (editor CMS), non a qualsiasi utente registrato.

---

#### B2 · SEC-004 — Mancanza permission check in `auto_translate_page_view`
**File:** `apps/core/views.py:101`

Dopo il `get_object_or_404`, aggiungere:

```diff
 page = get_object_or_404(Page, id=page_id).specific
+perms = page.permissions_for_user(request.user)
+if not perms.can_edit():
+    messages.error(request, "Non hai i permessi per modificare questa pagina.")
+    return redirect("wagtailadmin_explore", page.get_parent().id)
 current_locale = page.locale
```

---

### GRUPPO C — XSS / Injection (effort: 1h)

#### C1 · SEC-005 — XSS in interpolazione JavaScript di maps.py
**File:** `apps/core/maps.py:85`

```diff
+import json
 ...
- marker_popup = f'.bindPopup("{marker_text}")' if marker_text else ""
+ marker_popup = f'.bindPopup({json.dumps(marker_text)})' if marker_text else ""
```

`json.dumps()` gestisce automaticamente escaping di `"`, `\`, caratteri di controllo e Unicode. Una riga, zero dipendenze aggiuntive.

---

#### C2 · SEC-008 — RawHTMLBlock visibile a tutti gli editor
**File:** `apps/website/blocks.py` (e `apps/website/models/news.py`)

Il `RawHTMLBlock` ereditato da CodeRedCMS non può essere rimosso senza migration. La mitigazione pratica è nasconderlo agli editor non-superuser tramite un hook Wagtail:

```python
# apps/core/wagtail_hooks.py  (aggiunta al file esistente)
from wagtail import hooks

@hooks.register("construct_page_action_menu")
def hide_raw_html_for_non_superusers(menu_items, request, context):
    pass  # non serve qui

# Hook corretto: limitare il blocco nell'editor — non esiste un hook diretto.
# Alternativa: sovrascrivere il blocco con una versione che verifica request.user.is_superuser
# durante il rendering del form (si fa nel Panel, non nel Block).
```

La soluzione più robusta è sostituire il `RawHTMLBlock` CodeRed con un blocco custom che in `get_prep_value()` sanitizza l'HTML con `bleach` o `nh3` (libreria Rust-based):

```python
# apps/website/blocks.py
import nh3  # pip install nh3

class SafeHTMLBlock(RawHTMLBlock):
    """RawHTMLBlock con sanitizzazione nh3 — rimuove script e attributi pericolosi."""
    ALLOWED_TAGS = {"p","b","i","u","a","ul","ol","li","br","h2","h3","h4","blockquote","code","pre","table","thead","tbody","tr","td","th","img","iframe"}

    def get_prep_value(self, value):
        return nh3.clean(str(value), tags=self.ALLOWED_TAGS) if value else value
```

**Nota:** `nh3` richiede aggiunta a `pyproject.toml`: `"nh3>=0.2,<1.0"`.

---

### GRUPPO D — Rate Limiting e Brute Force (effort: 2h + 1 dipendenza)

#### D1 · SEC-007 — Rate limit su `auto_translate_page_view`
**Dipendenza da aggiungere:** `django-ratelimit>=4.1,<5.0` in `pyproject.toml`

```diff
# mccastellazzob/settings/base.py (dopo MIDDLEWARE)
+RATELIMIT_USE_CACHE = "default"
```

```diff
# apps/core/views.py
+from ratelimit.decorators import ratelimit

+@ratelimit(key="user", rate="10/h", method="POST", block=True)
 @staff_member_required
 def auto_translate_page_view(request, page_id):
```

10 traduzioni/ora per utente è sufficiente per uso legittimo. Blocca abusi API.

---

#### D2 · SEC-010 — Brute force su login / signup / password reset
**Stessa dipendenza:** `django-ratelimit`

```diff
# mccastellazzob/settings/base.py
 ACCOUNT_EMAIL_VERIFICATION = "optional"
+# Rate limiting login: max 5 tentativi / 15 min per IP
+ACCOUNT_RATE_LIMITS = {
+    "login_failed": "5/15m",
+    "signup": "10/h",
+    "password_reset": "5/h",
+}
```

`django-allauth >= 65` supporta nativamente `ACCOUNT_RATE_LIMITS` — nessun middleware extra.

---

### GRUPPO E — SSRF (effort: 30 min)

#### E1 · SEC-009 — Validazione URL esterne in machine_translator e maps
**File:** `apps/core/translation.py`, `apps/core/maps.py`

Aggiungere una funzione helper di validazione riusabile:

```python
# apps/core/utils.py  (file nuovo, ~10 righe)
from urllib.parse import urlparse

ALLOWED_EXTERNAL_SCHEMES = {"https"}
ALLOWED_TRANSLATION_HOSTS = {"libretranslate.com", "localhost", "127.0.0.1"}
ALLOWED_NOMINATIM_HOSTS = {"nominatim.openstreetmap.org"}

def validate_external_url(url: str, allowed_hosts: set) -> str:
    """Valida schema e host; raise ValueError se non consentito."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_EXTERNAL_SCHEMES:
        raise ValueError(f"Schema non consentito: {parsed.scheme!r}")
    if parsed.hostname not in allowed_hosts:
        raise ValueError(f"Host non consentito: {parsed.hostname!r}")
    return url
```

Da chiamare all'avvio (es. in `AppConfig.ready()`) con i valori dai settings, non a ogni richiesta.

---

### GRUPPO F — Logging e Information Disclosure (effort: 1h)

#### F1 · SEC-011 — Dettagli eccezione esposti nei messaggi
**File:** `apps/core/admin_views.py:140`

```diff
-messages.error(request, _("Errore durante il caricamento: %(error)s") % {"error": str(e)})
+logger.exception("Bulk upload error for user %s", request.user.pk)
+messages.error(request, _("Errore durante il caricamento. Contatta l'amministratore."))
```

`logger.exception()` include automaticamente il traceback nel log server-side.

---

#### F2 · SEC-012 — Assenza audit log per operazioni sensibili

Nessuna dipendenza extra: Django include già `LogEntry` in `django.contrib.admin`:

```python
# Aggiungere dopo ogni operazione sensibile (bulk upload, traduzione automatica)
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType

LogEntry.objects.log_action(
    user_id=request.user.pk,
    content_type_id=ContentType.objects.get_for_model(page).pk,
    object_id=page.pk,
    object_repr=str(page),
    action_flag=CHANGE,
    change_message=f"Auto-translated to {target_lang}",
)
```

---

### GRUPPO G — CSP e Dipendenze (effort: 1h + 1 dipendenza)

#### G1 · SEC-013 — Content Security Policy assente
**Dipendenza:** `django-csp>=3.8,<4.0` in `pyproject.toml`

```diff
# mccastellazzob/settings/base.py — MIDDLEWARE
  "wagtail.contrib.redirects.middleware.RedirectMiddleware",
+ "csp.middleware.CSPMiddleware",
]

# mccastellazzob/settings/prod.py (in aggiunta)
+CSP_DEFAULT_SRC = ("'self'",)
+CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "unpkg.com", "cdn.jsdelivr.net")
+CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "unpkg.com", "cdn.jsdelivr.net", "fonts.googleapis.com")
+CSP_IMG_SRC = ("'self'", "data:", "*.tile.openstreetmap.org", "*.openstreetmap.org")
+CSP_FONT_SRC = ("'self'", "fonts.gstatic.com", "cdnjs.cloudflare.com")
+CSP_FRAME_SRC = ("'self'", "www.youtube.com", "player.vimeo.com")
+CSP_REPORT_URI = "/csp-report/"  # endpoint di raccolta violations (opzionale)
```

Avviare in **report-only** prima del go-live per identificare violazioni senza bloccare nulla:
```python
CSP_REPORT_ONLY = True  # rimuovere dopo verifica
```

---

#### G2 · SEC-014 — Nessun CVE check automatico

Aggiungere a `pyproject.toml` nelle dipendenze dev:

```diff
 dev = [
+    "pip-audit>=2.7,<3.0",
     "pytest>=8.0,<9.0",
```

E aggiungere al `.pre-commit-config.yaml` (se esistente) o creare:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pip-audit
        name: pip-audit (CVE check)
        entry: pip-audit
        language: system
        pass_filenames: false
        always_run: true
```

Oppure, senza pre-commit, basta eseguire periodicamente: `pip-audit`.

---

### Riepilogo modifiche per file

| File | Modifiche |
|---|---|
| `mccastellazzob/settings/base.py` | A1, A4, D2, G1 |
| `mccastellazzob/settings/docker.py` | A2 |
| `mccastellazzob/settings/prod.py` | G1 (CSP headers) |
| `docker/entrypoint.sh` | A3 |
| `apps/core/admin_views.py` | B1, F1, F2 |
| `apps/core/views.py` | B2, D1, F2 |
| `apps/core/maps.py` | C1 |
| `apps/website/blocks.py` | C2 (SafeHTMLBlock) |
| `apps/core/utils.py` | E1 (file nuovo) |
| `pyproject.toml` | C2 (nh3), D1 (django-ratelimit), G1 (django-csp), G2 (pip-audit) |

### Nuove dipendenze necessarie

| Pacchetto | Versione | Motivo |
|---|---|---|
| `django-ratelimit` | `>=4.1,<5.0` | D1, D2 (rate limit traduzione) — opzionale: allauth ha già il suo |
| `nh3` | `>=0.2,<1.0` | C2 (sanitizzazione RawHTMLBlock) |
| `django-csp` | `>=3.8,<4.0` | G1 (Content Security Policy) |
| `pip-audit` | `>=2.7,<3.0` (dev only) | G2 (CVE check) |

**Nota:** `django-allauth` gestisce già il rate limit su login/signup/reset via `ACCOUNT_RATE_LIMITS` dalla versione 65 — nessuna dipendenza extra per D2.
