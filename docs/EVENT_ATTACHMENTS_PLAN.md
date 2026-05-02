# Event Attachments (GPX) — Design & Implementation Plan

Data: 2026-05-02
Stato: Decisioni approvate, implementazione da eseguire
Scope: aggiunta sistema allegati su `EventDetailPage`, primo caso d'uso = file GPX (multipli)

## Decisioni

| Aspetto | Scelta |
|---|---|
| Tipo di blocco | Riuso `DocumentBlock` esistente, esteso con sottoclasse `EventAttachmentBlock` per validazione |
| Validazione file | Estensioni accettate `.gpx`, `.kml`, `.pdf` + dimensione max 5 MB |
| Filename storage | Default Wagtail (filename originale + hash breve nell'URL del file) |
| UI | Card per ogni allegato: icona per tipo, titolo, descrizione, dimensione, bottone Download |
| Traducibilità | `title` e `description` dentro StreamField → tradotti da `wagtail-localize` |
| Etichetta sezione | "Allegati" (traducibile) |
| Schema.org | `subjectOf` popolato per ogni estensione mappata: GPX/KML → `DataDownload`, PDF → `DigitalDocument`. Estensioni non mappate → escluse. |

## Architettura

### Modello — `apps/website/models/events.py`
- Nuovo `StreamField` `attachments` su `EventDetailPage`:
  ```python
  attachments = StreamField(
      [("attachment", EventAttachmentBlock())],
      blank=True,
      use_json_field=True,
      verbose_name=_("Allegati"),
  )
  ```
- Aggiungere `FieldPanel("attachments")` in `content_panels`.
- Migrazione Wagtail/Django generata (è StreamField → semplice).

### Blocco — `apps/website/blocks.py`
- Nuova classe `EventAttachmentBlock(DocumentBlock)` con override `clean()`:
  - controllo estensione `.gpx` (case-insensitive)
  - controllo `document.file.size <= 5 * 1024 * 1024`
  - errore localizzato e bloccante in admin Wagtail
- `Meta.label = _("Allegato evento")`
- Template dedicato: `website/blocks/event_attachment_block.jinja2` (rendering card)

### Template card — `templates/website/blocks/event_attachment_block.jinja2`
- Card con:
  - icona GPX (FontAwesome `fa-route` o `fa-map-marked-alt`)
  - titolo (escapato)
  - descrizione (escapata)
  - dimensione formattata (KB/MB)
  - link download `<a href="{{ value.document.url }}" download>`
- Tutto compatibile con la sezione `<aside>` esistente del template evento.

### Pagina evento — `templates/website/pages/event_detail_page.jinja2`
- Aggiunta sezione "Allegati" (rendering condizionale: solo se `page.attachments` non vuoto).
- Posizionamento: dopo `description`, prima della galleria.
- Header tradotto via `_("Allegati")`.

### Schema.org — `apps/website/models/events.py::get_json_ld_data`
- Mappa estensione → schema.org type (estendibile per nuovi formati senza toccare la logica):
  ```python
  ATTACHMENT_SCHEMA_MAP = {
      "gpx": {
          "type": "DataDownload",
          "encodingFormat": "application/gpx+xml",
      },
      # Predisposto per il futuro (NON attivo finché non confermato):
      # "kml": {"type": "DataDownload", "encodingFormat": "application/vnd.google-earth.kml+xml"},
      # "pdf": {"type": "DigitalDocument", "encodingFormat": "application/pdf"},
  }
  ```
- Funzione helper:
  ```python
  def _attachment_to_schema(att):
      doc = att.value.get("document")
      if not doc:
          return None
      ext = doc.filename.lower().rsplit(".", 1)[-1] if "." in doc.filename else ""
      mapping = ATTACHMENT_SCHEMA_MAP.get(ext)
      if not mapping:
          return None  # estensione non mappata → non finisce nel JSON-LD
      return {
          "@type": mapping["type"],
          "encodingFormat": mapping["encodingFormat"],
          "name": att.value.get("title") or doc.title,
          "description": att.value.get("description", ""),
          "contentUrl": doc.file.url,
      }
  ```
- Aggiunta `subjectOf` (lista) al data JSON-LD solo se almeno un allegato risulta mappato. Risultato finale: contiene **solo le tracce GPX** (e in futuro, abilitando le righe commentate, eventuali PDF/KML), mai allegati di formato sconosciuto.

## Sicurezza

- Validazione lato server (mai fidarsi del solo MIME del browser):
  - controllo estensione `.gpx` esplicito
  - controllo dimensione 5 MB hard-cap
  - opzionale (Phase 2): parse minimo del file per verificare presenza di `<gpx` come root tag XML, prevenendo upload PDF rinominati
- Nessun rendering inline del contenuto del file (il GPX viene solo offerto come download).
- Niente `mark_safe` su campi del block: tutti i campi rimangono in autoescape Jinja2.

## Traduzione

- `wagtail-localize` rileva automaticamente CharBlock/TextBlock dentro StreamField traducibili.
- Per consistenza: il file (`document`) NON va tradotto — manteniamo singolo file condiviso tra lingue (cambia solo title/description).
  - Comportamento default `wagtail-localize`: i `DocumentChooserBlock` non sono campi testo, quindi non rientrano nella traduzione automatica testuale, vengono replicati così come sono.
- Stringhe statiche di template (etichetta "Allegati", "Download", "Dimensione") vanno in `gettext` per finire nei file `.po`.

## Migration Strategy

1. Aggiunta `attachments` come StreamField `blank=True` → migrazione non-distruttiva.
2. Nessun dato esistente da migrare (campo nuovo).
3. Test su DB di dev → esecuzione `makemigrations` + `migrate`.

## Acceptance Criteria

- Editor può aggiungere N allegati a un EventDetailPage (testato con 2 GPX).
- Caricamento file non-GPX bloccato con errore chiaro in admin.
- Caricamento >5 MB bloccato con errore chiaro.
- Pagina pubblica mostra card per ogni allegato con titolo, descrizione, link download.
- Versione DE/EN/FR/ES mostra titolo e descrizione tradotti, stesso file.
- JSON-LD include `subjectOf` con `@type: DataDownload` solo per estensioni `.gpx`; allegati di altre estensioni non compaiono nel JSON-LD.
- Filename URL contiene hash anti-collisione Wagtail (verificato visivamente).

## Open / Future

- Phase 2 opzionale: preview track GPX su Leaflet (`leaflet-gpx`) — solo se richiesto dopo il primo rilascio.
- Phase 2 opzionale: validazione XML root `<gpx>` per blindare contro file rinominati.
- Phase 2 opzionale: estensione ad altri formati (KML, PDF percorso) → introdurre `kind` enum e card icon per tipo.

## Step di esecuzione (quando si parte)

1. Aggiungere `EventAttachmentBlock` in `apps/website/blocks.py` + esporre nell'`__all__` se serve.
2. Aggiungere `attachments` su `EventDetailPage` + panel + import.
3. Creare template `event_attachment_block.jinja2`.
4. Aggiungere sezione "Allegati" in `event_detail_page.jinja2`.
5. Estendere `get_json_ld_data` con MediaObject condizionali.
6. `makemigrations website && migrate` su DB locale.
7. Test manuale su `/django-admin/` con 2 GPX.
8. `makemessages` per nuove stringhe + traduzioni di base.
9. Commit + PR dedicata.
