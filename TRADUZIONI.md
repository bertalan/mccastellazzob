# 🌍 Guida alla Traduzione Automatica

Questa guida spiega come tradurre automaticamente i contenuti del sito MC Castellazzo nelle diverse lingue supportate (Italiano, Inglese, Tedesco, Francese, Spagnolo).

## 🚀 Traduzione Rapida con Pulsante

### Metodo 1: Tradurre una singola pagina

1. **Accedi al backend Wagtail**: `/admin/`
2. **Vai alla pagina** che vuoi tradurre
3. Clicca su **"Azioni"** (o menu in alto a destra)
4. Seleziona **"Traduci"** o **"Translate"**
5. Scegli la **lingua di destinazione** (es. English, Deutsch, Français, Español)
6. Clicca **"Sincronizza questa pagina"** per creare la versione tradotta
7. Nella pagina di traduzione, cerca il pulsante **"Traduci con Google Translate (Gratuito)"**
8. Clicca il pulsante per **tradurre automaticamente** tutto il contenuto
9. **Rivedi** le traduzioni e apporta eventuali correzioni
10. **Pubblica** la pagina tradotta

### Metodo 2: Tradurre più pagine insieme

1. Vai a **"Pagine"** nel menu principale
2. Seleziona la **pagina padre** (es. Home)
3. Clicca **"Azioni"** → **"Traduci in blocco"** (Bulk Translate)
4. Seleziona le pagine da tradurre
5. Scegli le lingue di destinazione
6. Avvia la traduzione automatica

---

## 📋 Workflow Consigliato

### Per nuovi contenuti

```
1. Scrivi il contenuto in ITALIANO (lingua principale)
2. Pubblica la pagina italiana
3. Clicca "Traduci" e seleziona tutte le altre lingue
4. Usa "Traduci automaticamente" per ogni lingua
5. Rivedi e correggi eventuali errori
6. Pubblica le versioni tradotte
```

### Per aggiornamenti

```
1. Modifica la pagina ITALIANA
2. Pubblica le modifiche
3. Vai alle versioni tradotte
4. Clicca "Sincronizza" per aggiornare
5. Ritraduce solo i contenuti modificati
6. Pubblica
```

---

## 🎯 Lingue Supportate

| Codice | Lingua | Stato |
|--------|--------|-------|
| `it` | 🇮🇹 Italiano | Lingua principale |
| `en` | 🇬🇧 English | Traduzione automatica |
| `de` | 🇩🇪 Deutsch | Traduzione automatica |
| `fr` | 🇫🇷 Français | Traduzione automatica |
| `es` | 🇪🇸 Español | Traduzione automatica |

---

## ⚙️ Comandi da Terminale

### Verificare stato traduzioni

```bash
# Con Docker
docker compose run --rm web python manage.py shell -c "
from wagtail.models import Page, Locale
for locale in Locale.objects.all():
    count = Page.objects.filter(locale=locale).count()
    print(f'{locale.language_code}: {count} pagine')
"
```

### Sincronizzare albero pagine

```bash
# Sincronizza la struttura delle pagine tra le lingue
docker compose run --rm web python manage.py sync_page_translation_tree
```

### Controllare pagine mancanti

```bash
# Mostra pagine non ancora tradotte
docker compose run --rm web python manage.py shell -c "
from wagtail.models import Page, Locale
from wagtail_localize.models import TranslationSource

it_locale = Locale.objects.get(language_code='it')
it_pages = Page.objects.filter(locale=it_locale, depth__gt=1).live()

for page in it_pages:
    print(f'• {page.title}')
    for locale in Locale.objects.exclude(language_code='it'):
        try:
            translated = page.get_translation(locale)
            status = '✅' if translated.live else '📝'
            print(f'  {status} {locale.language_code}')
        except Page.DoesNotExist:
            print(f'  ❌ {locale.language_code} - Mancante')
"
```

---

## 🔧 Configurazione Tecnica

Il sistema usa:

- **wagtail-localize**: Gestione traduzioni Wagtail
- **deep-translator**: Traduzione Google Translate gratuita (senza API key)

### File di configurazione

```python
# mccastellazzob/settings/base.py
WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "apps.core.machine_translator.DeepTranslatorMachineTranslator",
    "OPTIONS": {
        "DELAY": 0.5,  # Ritardo tra richieste (evita rate limiting)
    },
}
```

### Codice traduttore

Il traduttore custom si trova in: `apps/core/machine_translator.py`

---

## ⚠️ Note Importanti

### Qualità delle traduzioni

- Le traduzioni automatiche sono un **punto di partenza**
- **Rivedi sempre** le traduzioni prima di pubblicare
- Presta attenzione a:
  - Nomi propri (persone, luoghi, eventi)
  - Terminologia specifica del motoclub
  - Date e numeri
  - Link e URL

### Rate Limiting

- Google Translate ha limiti di richieste
- Il sistema attende 0.5 secondi tra ogni traduzione
- Per contenuti molto lunghi, la traduzione può richiedere alcuni minuti

### Backup

- Le traduzioni sono salvate nel database
- Puoi sempre ripristinare una versione precedente dalla cronologia Wagtail

---

## 🆘 Risoluzione Problemi

### "Traduzione non disponibile"

```bash
# Verifica che deep-translator sia installato
docker compose run --rm web pip show deep-translator
```

### "Errore di traduzione"

1. Controlla la connessione internet
2. Attendi qualche minuto (rate limiting)
3. Riprova la traduzione

### "Pulsante traduzione non appare"

1. Assicurati che la pagina sia pubblicata in italiano
2. Verifica che la lingua di destinazione sia attiva
3. Controlla i log: `docker compose logs web`

---

## 📞 Supporto

Per problemi tecnici, controlla i log:

```bash
docker compose logs -f web | grep -i translat
```

O contatta lo sviluppatore con una descrizione del problema.
