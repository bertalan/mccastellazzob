# Security Audit Report V2 — MC Castellazzo
**Data:** 2 maggio 2026  
**Metodologia:** OWASP Top 10 (2021), analisi statica indipendente  
**Scope:** Django 5.2 / Wagtail 7.x — settings, views, models, templates, forms, Docker  
**Stato:** Solo analisi — nessuna modifica al codice  
**Note:** Audit condotto in parallelo a `SECURITY_AUDIT.md` per verifica completezza (sub-agent indipendente, senza accesso preventivo al primo report)

---

## Executive Summary

Il progetto presenta fondamenta di sicurezza solide (ORM parametrizzato, CSRF attivo, HSTS in prod, password validators, allauth con configurazione moderna). Sono stati identificati **20 finding** (rispetto ai 16 della prima audit) — **3 nuovi finding non presenti nel report originale**:

| Severity | Count |
|---|---|
| 🔴 Critical | 1 |
| 🟠 High | 7 |
| 🟡 Medium | 7 |
| 🟢 Low / Info | 5 |

---

## Differenze rispetto ad audit precedente

### Finding NUOVI identificati in V2 (assenti in V1)

- **NEW-1** · Configurazione esplicita cookie/session mancante (`SESSION_COOKIE_SAMESITE`, `SESSION_COOKIE_AGE`, `PASSWORD_RESET_TIMEOUT`, `SESSION_COOKIE_HTTPONLY`)
- **NEW-2** · BulkUpload form senza limite di dimensione + `PIL.Image.open()` senza protezione decompression bomb
- **NEW-3** · Potenziale email header injection nel form contatti (`reply_to` da input utente non sanitizzato)

### Finding NON confermati

Nessuno: tutti i 16 finding di V1 sono stati confermati anche da V2.

### Aspetti analizzati che V1 NON aveva esplicitamente verificato

- ✅ Admin URL custom (`/django-admin/` invece di `/admin/`) — security by obscurity, OK
- ✅ `CODERED_PROTECTED_MEDIA_*` configurato per document privati
- ✅ Honeypot + timestamp check su form contatti
- ✅ Auth backends standard (no custom backends rischiosi)
- ✅ Nessun `pickle`/`yaml.load` insicuro
- ✅ Nessun raw SQL pericoloso

---

## Findings Dettagliati

### 🔴 CRITICAL

#### V2-001 · SECRET_KEY con fallback statico
**= V1 SEC-001**  
**File:** `mccastellazzob/settings/base.py:18`  
**OWASP:** A02 – Cryptographic Failures

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-production")
```

Già documentato in V1. Confermato.

---

### 🟠 HIGH

#### V2-002 · DEBUG=True default in docker.py
**= V1 SEC-002** · `docker.py:8` · A05

#### V2-003 · IDOR su `get_image_metadata`
**= V1 SEC-003** · `admin_views.py:166` · A01

#### V2-004 · Permission check mancante in `auto_translate_page_view`
**= V1 SEC-004** · `views.py:101` · A01

#### V2-005 · XSS via interpolazione JS in maps.py
**= V1 SEC-005** · `maps.py:85` · A03

#### V2-006 · Password Docker hardcoded `admin123`
**= V1 SEC-006** · `docker/entrypoint.sh` · A07

#### 🆕 V2-007 · Configurazione cookie/session NON esplicita (NEW)
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `mccastellazzob/settings/base.py` (assenza)  
**Severità:** High

Configurazioni mancanti:
```python
# Mai impostati in base.py né prod.py:
# SESSION_COOKIE_SAMESITE   → default Django: "Lax" (OK ma non esplicito)
# SESSION_COOKIE_HTTPONLY   → default Django 4.1+: True (OK ma non esplicito)
# SESSION_COOKIE_AGE        → default: 1209600 (14 giorni) — TROPPO LUNGO
# PASSWORD_RESET_TIMEOUT    → default: 259200 (3 giorni) — TROPPO LUNGO
# CSRF_COOKIE_SAMESITE      → non configurato
# CSRF_COOKIE_HTTPONLY      → default: False (intenzionale per AJAX, OK)
```

**Impatto:** Token reset password validi 3 giorni allargano la finestra per brute force; sessioni di 14 giorni amplificano session hijacking; nessuna garanzia esplicita di SameSite.

**Remediation:**
```python
# base.py
SESSION_COOKIE_HTTPONLY = True       # esplicito
SESSION_COOKIE_SAMESITE = "Lax"      # esplicito
SESSION_COOKIE_AGE = 60 * 60 * 8     # 8 ore
PASSWORD_RESET_TIMEOUT = 60 * 60     # 1 ora
CSRF_COOKIE_SAMESITE = "Lax"
```

---

#### 🆕 V2-008 · BulkUpload — assenza limite dimensione + decompression bomb (NEW)
**OWASP:** A04 – Insecure Design / A05 – Security Misconfiguration  
**File:** `apps/core/forms.py:113-141` + `apps/core/image_optimizer.py:32-35`  
**Severità:** High

```python
# forms.py — BulkUploadForm.clean_images()
def clean_images(self):
    images = self.cleaned_data.get("images", [])
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    for image in images:
        if hasattr(image, "content_type"):
            if image.content_type not in allowed_types:
                raise forms.ValidationError(...)
    return images  # ← Nessun controllo dimensione
```

```python
# image_optimizer.py
def optimize_image(image_buffer: io.BytesIO) -> io.BytesIO:
    image_buffer.seek(0)
    img = Image.open(image_buffer)  # ← decompression bomb non gestita
```

**Impatto:**
1. Editor compromesso può caricare file da N GB → riempire disco
2. Decompression bomb (es. PNG 1KB che si decomprime in RAM a 10GB) → OOM kill del worker gunicorn

**Remediation:**
```python
# forms.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
for image in images:
    if image.size > MAX_FILE_SIZE:
        raise forms.ValidationError(_("File %s troppo grande (max 10 MB)") % image.name)

# image_optimizer.py — limita pixel totali
from PIL import Image as PILImage
PILImage.MAX_IMAGE_PIXELS = 50_000_000  # ~50 megapixel
# In Pillow >=10, file oltre questa soglia fanno raise DecompressionBombError
```

Si noti che `BulkUploadView` ha già `DATA_UPLOAD_MAX_NUMBER_FILES` e Django ha `FILE_UPLOAD_MAX_MEMORY_SIZE` di default, ma nessun limite per-file esplicito.

---

#### 🆕 V2-009 · Email header injection potenziale nel form contatti (NEW)
**OWASP:** A03 – Injection  
**File:** `apps/website/models/about.py:649-681`  
**Severità:** High (riducibile a Medium se Django >=4 valida l'header)

```python
def send_contact_email(self, form_data, attachments=None):
    body = f"""
Nome: {form_data.get('nome', '')} {form_data.get('cognome', '')}
Email: {form_data.get('email', '')}
Telefono: {form_data.get('telefono', 'Non fornito')}
Argomento: {form_data.get('oggetto', '')}

Messaggio:
{form_data.get('messaggio', '')}
    """
    reply_to = form_data.get('email', '')
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[to_email],
        reply_to=[reply_to] if reply_to else None,
    )
```

**Impatto:**
- `reply_to` è preso direttamente dall'input utente. Django `EmailMessage` valida che non contenga `\n`, ma è meglio essere espliciti
- Campi `nome`, `cognome`, `oggetto`, `messaggio` finiscono nel **body** (text/plain): se contengono CRLF non possono iniettare header (sono nel body, non nei header), ma se in futuro si passa a HTML con interpolazione nel subject → rischio reale

**Remediation:**
```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

reply_to = form_data.get("email", "").strip()
try:
    validate_email(reply_to)
except ValidationError:
    reply_to = None

# Sanitizza tutti i campi che entrano nei header (subject)
def _strip_header_chars(s: str) -> str:
    return re.sub(r"[\r\n]", "", s)[:200]

subject_safe = _strip_header_chars(form_data.get("oggetto", ""))
```

---

### 🟡 MEDIUM

#### V2-010 · RawHTMLBlock visibile a tutti gli editor
**= V1 SEC-008** · `apps/website/blocks.py` (heritato CodeRed) · A03

#### V2-011 · SSRF su URL esterne (Nominatim, MyMemory)
**= V1 SEC-009** · `maps.py:25`, `machine_translator.py` · A10

#### V2-012 · Email verification opzionale + no rate limit auth
**= V1 SEC-010** · `base.py:260` · A07

#### V2-013 · Dettagli eccezione esposti negli error message
**= V1 SEC-011** · `admin_views.py:140` · A09

#### V2-014 · Nessun audit log per operazioni sensibili
**= V1 SEC-012** · `admin_views.py`, `views.py` · A09

#### V2-015 · No rate limit su `auto_translate_page_view`
**= V1 SEC-007** · `views.py` · A04 (degradato da High a Medium: richiede già auth staff)

#### V2-016 · Uso esteso di `|safe` su campi editor (16 occorrenze)
**OWASP:** A03 – Injection (condizionato)  
**Severità:** Medium  
**Files:** 16 template `.jinja2` (vedi sotto)

Wagtail sanitizza `RichTextField` automaticamente, quindi `|safe` su questi campi è di fatto sicuro. Tuttavia alcuni `|safe` sono applicati a campi che NON sono RichText:

| File:Linea | Campo | Tipo Modello | Rischio |
|---|---|---|---|
| `contact_page.jinja2:224` | `page.address\|replace(", ", "<br>")\|safe` | CharField | **Medium** — admin può inserire HTML |
| `cta_block.jinja2:6` | `value.title\|replace(...)\|safe` | CharBlock | **Medium** — admin può inserire HTML |
| `member_block.jinja2:19` | `value.bio` | RichTextBlock? | Low (dipende dal block) |
| `event_card_block.jinja2:35` | `value.description` | RichTextBlock | Low |
| `home_page.jinja2:168` | `page.description` | RichTextField | Low |
| (altri 11) | RichTextField | Low |

**Remediation:** Sostituire i `replace()` con `|striptags|escape` e poi rebuild HTML, oppure usare un `mark_safe()` controllato server-side dopo escape esplicito:

```jinja2
{# contact_page.jinja2 #}
{{ page.address|escape|replace(", ", "<br>")|safe }}
{# ↑ ora sicuro: escape PRIMA del replace #}
```

---

### 🟢 LOW / INFO

#### V2-017 · CSP assente
**= V1 SEC-013** · A05

#### V2-018 · No CVE check automatico
**= V1 SEC-014** · `pyproject.toml` · A06

#### V2-019 · ALLOWED_HOSTS fallback
**= V1 SEC-015** · `base.py:20` · A05

#### V2-020 · Permissions-Policy / Cross-Origin headers mancanti
**OWASP:** A05 – Security Misconfiguration  
**Severità:** Info  
**File:** `mccastellazzob/settings/prod.py`

Mancano header moderni:
- `Permissions-Policy` (controlla camera/microphone/geolocation)
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Embedder-Policy`
- `Cross-Origin-Resource-Policy`

Django 4.2+ supporta `SECURE_REFERRER_POLICY` (già configurato ✅) ma non i COOP/COEP nativi. Si possono aggiungere via middleware custom o `django-csp` extra.

---

## Aspetti VERIFICATI come SICURI ✅

1. ORM Django: nessun `.raw()` / `.extra()` rischioso
2. CSRF middleware attivo, no `@csrf_exempt` su endpoint scrivibili
3. Admin URL non standard (`/django-admin/`)
4. HSTS, SSL redirect, X-Frame-Options DENY in `prod.py`
5. SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE in `prod.py`
6. 4 password validators attivi
7. Nessun `pickle` / `yaml.load` (solo `safe_load` se presente)
8. Nessuna API key hardcoded; `.env` in `.gitignore`
9. Jinja2 autoescape ON per default
10. Wagtail RichTextField sanitization automatica (TinyMCE allowlist)
11. BulkUpload valida MIME (anche se non size)
12. Honeypot + timestamp check su form contatti
13. Auth backends standard (allauth + ModelBackend)
14. CODERED_PROTECTED_MEDIA configurato per document privati
15. WhiteNoise con manifest static storage
16. CSRF_TRUSTED_ORIGINS configurato in prod
17. SECURE_REFERRER_POLICY configurato

---

## Copertura OWASP Top 10 2021

| # | Categoria | V2 Findings | Status |
|---|---|---|---|
| **A01** | Broken Access Control | V2-003, V2-004 | 🟠 |
| **A02** | Cryptographic Failures | V2-001 | 🔴 |
| **A03** | Injection | V2-005, V2-009, V2-010, V2-016 | 🟠 |
| **A04** | Insecure Design | V2-008, V2-015 | 🟡 |
| **A05** | Security Misconfiguration | V2-002, V2-017, V2-019, V2-020 | 🟠 |
| **A06** | Vulnerable Components | V2-018 | 🟢 |
| **A07** | Identification & Authentication | V2-006, V2-007, V2-012 | 🟠 |
| **A08** | Software & Data Integrity | — | ✅ |
| **A09** | Logging & Monitoring | V2-013, V2-014 | 🟡 |
| **A10** | SSRF | V2-011 | 🟡 |

**Tutti i 10 capitoli OWASP coperti.**

---

## Tabella di confronto V1 ↔ V2

| V1 ID | V2 ID | Confermato | Note |
|---|---|---|---|
| SEC-001 | V2-001 | ✅ | Critical, identico |
| SEC-002 | V2-002 | ✅ | High, identico |
| SEC-003 | V2-003 | ✅ | High, identico |
| SEC-004 | V2-004 | ✅ | High, identico |
| SEC-005 | V2-005 | ✅ | High, identico |
| SEC-006 | V2-006 | ✅ | High, identico |
| SEC-007 | V2-015 | ✅ | Degradato a Medium (auth staff già presente) |
| SEC-008 | V2-010 | ✅ | Medium, identico |
| SEC-009 | V2-011 | ✅ | Medium, identico |
| SEC-010 | V2-012 | ✅ | Medium, identico |
| SEC-011 | V2-013 | ✅ | Medium, identico |
| SEC-012 | V2-014 | ✅ | Medium, identico |
| SEC-013 | V2-017 | ✅ | Low, identico |
| SEC-014 | V2-018 | ✅ | Low, identico |
| SEC-015 | V2-019 | ✅ | Low, identico |
| — | **V2-007** 🆕 | NEW | Cookie/session config esplicita |
| — | **V2-008** 🆕 | NEW | File upload size + decompression bomb |
| — | **V2-009** 🆕 | NEW | Email header injection |
| — | **V2-016** 🆕 | NEW | `\|safe` su CharField (non solo RichText) |
| — | **V2-020** 🆕 | NEW | Permissions-Policy / COOP / COEP headers |

**5 finding aggiuntivi in V2.**

---

## Verdetto sulla completezza di V1

V1 (`SECURITY_AUDIT.md`) **è solido sui fondamentali OWASP** e copre correttamente i finding più critici (SECRET_KEY, IDOR, XSS, Docker password, missing permission check).

**Lacune di V1 individuate da V2:**

1. **File upload — solo MIME, non size né decompression bomb** (V2-008): un classico OWASP A04. Importante per editor con account compromesso.
2. **Email header injection nel form contatti** (V2-009): superficie pubblica! Chiunque può triggerare il form. Più critico per un sito istituzionale.
3. **Configurazione cookie/session esplicita** (V2-007): hardening configurazione.
4. **`|safe` su CharField (non RichText)** (V2-016): un caso specifico di XSS che V1 trattava solo via `RawHTMLBlock`.
5. **HTTP headers moderni** (V2-020): Permissions-Policy, COOP, COEP — nice to have.

**Suggerimento:** integrare i 5 finding nuovi nel documento V1, oppure mantenere V2 come revisione canonica.
