# Moto Club Castellazzo Bormida - Sito Statico

## Panoramica Progetto

Sito multi-pagina per il Moto Club Castellazzo Bormida (fondato 1933).
Stack: HTML5 + Tailwind CSS (CDN) + JavaScript vanilla.

> **🚀 Integrazione Wagtail/CoderedCMS**  
> Per trasferire questa grafica al progetto Django/Wagtail, consulta la guida completa:  
> 👉 [WAGTAIL_INTEGRATION.md](WAGTAIL_INTEGRATION.md)

---

## Identità Visiva

### Profilo Caldo (Attivo)

| Colore | HEX | Uso |
|--------|-----|-----|
| Oro Brillante | `#ffd700` | Navbar, accenti, testo logo |
| Oro Scuro | `#f6c401` | Hover states |
| Bordeaux | `#ab0031` | Bottoni CTA, elementi in evidenza |
| Navy | `#1B263B` | Sfondo principale, footer |
| Amaranto | `#9B1D64` | Accenti secondari |

### Profilo Classic (Alternativo)

| Colore | HEX | Uso |
|--------|-----|-----|
| Oro | `#D4AF37` | Primario, CTA, accenti |
| Navy | `#1B263B` | Sfondo principale |
| Amaranto | `#9B1D64` | Accenti secondari |

Font: Montserrat (heading) + Inter (body) via Google Fonts.

## Struttura File

```
motoclub-static/
├── index.html                    # Homepage ✅
├── chi-siamo.html                # Storia e valori
├── consiglio.html                # Membri direttivo
├── eventi.html                   # Calendario eventi
├── galleria.html                 # Galleria foto
├── contatti.html                 # Form + mappa
├── css/
│   ├── style.css                 # Stili base con variabili CSS
│   └── animations.css            # Keyframes
├── js/
│   ├── main.js                   # Funzionalità condivise
│   └── color-manager.js          # Sistema gestione colori
├── images/
│   └── MotoClubCastellazzoBormida-logo.webp  # Logo ufficiale
├── colors.json                   # Profili colore
├── COLOR_SYSTEM.md               # Documentazione sistema colori
├── QUICK_START.md                # Quick reference
├── SUMMARY.md                    # Riepilogo implementazione
└── WAGTAIL_INTEGRATION.md        # 🚀 Guida integrazione Wagtail
```

## Dati Contenuto

### Statistiche Club
- **93** anni di storia (dal 1933)
- **250** membri attivi
- **52** eventi annuali
- **120K** km percorsi annualmente

### Consiglio Direttivo
| Ruolo | Nome |
|-------|------|
| Presidente | Mario Rossi |
| Vice Presidente | Giuseppe Bianchi |
| Segretario | Anna Verdi |
| Tesoriere | Marco Neri |
| Resp. Eventi | Laura Gialli |
| Resp. Comunicazione | Paolo Blu |

### Prossimo Evento
- **Nome**: Gran Raduno Primaverile 2026
- **Data**: 15 Marzo 2026, ore 09:00
- **Luogo**: Castellazzo Bormida

### Contatti
- **Indirizzo**: Via Roma 45, 15073 Castellazzo Bormida (AL)
- **Coordinate mappa**: 44.8983, 8.5914
- **Telefono**: +39 0131 278945
- **Email**: info@mccastellazzob.com
- **Orari segreteria**: Mar-Gio 18-20, Sab 10-12

## Specifiche per Pagina

### chi-siamo.html
- Hero con titolo "La Nostra Storia"
- Sezione intro: fondazione 1933, crescita, presente
- Timeline verticale (4-5 milestone: 1933, 1950, 1980, 2000, oggi)
- Sezione "I Nostri Valori" (3 card: Passione, Amicizia, Avventura)
- CTA finale per contatto

### consiglio.html
- Hero con titolo "Il Consiglio Direttivo"
- Grid 3 colonne (2 su tablet, 1 su mobile)
- Card membri con: foto placeholder, nome, ruolo, breve bio
- Effetto hover: scala o flip
- Sezione contatto rapido

### eventi.html
- Hero con titolo "I Nostri Eventi"
- Evento in evidenza (prossimo) con countdown
- Grid eventi futuri (card con data, titolo, descrizione, luogo)
- Sezione "Tipi di Eventi" (Raduni, Escursioni, Gare, Sociali)
- CTA iscrizione

### galleria.html
- Hero con titolo "Galleria Fotografica"
- Filtri categoria: Tutti, Raduni, Escursioni, Gare, Eventi Sociali
- Grid masonry/responsive con immagini placeholder
- Lightbox modale per visualizzazione grande
- 12-16 immagini placeholder con alt text descrittivi

### contatti.html
- Hero con titolo "Contattaci"
- Layout 2 colonne: form | info contatto
- Form: nome, email, telefono, messaggio, checkbox privacy
- Validazione HTML5 + JS
- Mappa Leaflet con marker sede
- Info: indirizzo, telefono, email, orari, social

## Requisiti WCAG 2.2 (Livello AA)

### Percepibile
- [ ] Contrast ratio minimo 4.5:1 per testo normale, 3:1 per testo grande
- [ ] Alt text descrittivi su tutte le immagini
- [ ] Non usare solo colore per comunicare info
- [ ] Testo ridimensionabile fino a 200% senza perdita contenuto

### Utilizzabile
- [ ] Navigazione completa da tastiera (Tab, Enter, Escape)
- [ ] Focus visibile su tutti elementi interattivi (outline 2px minimo)
- [ ] Skip link "Vai al contenuto" come primo elemento
- [ ] Target touch minimo 44x44px
- [ ] Nessun contenuto lampeggiante >3 flash/sec

### Comprensibile
- [ ] Lang attribute `<html lang="it">`
- [ ] Label esplicite su tutti i form input
- [ ] Messaggi errore chiari e suggerimenti correzione
- [ ] Navigazione consistente tra pagine

### Robusto
- [ ] HTML valido e semantico (header, nav, main, footer, article, section)
- [ ] ARIA landmarks dove necessario
- [ ] Role e aria-label su elementi interattivi custom
- [ ] Testare con screen reader (VoiceOver)

### Attributi Richiesti
```html
<!-- Skip link -->
<a href="#main-content" class="sr-only focus:not-sr-only">Vai al contenuto principale</a>

<!-- Immagini -->
<img src="..." alt="Descrizione significativa" loading="lazy">

<!-- Form -->
<label for="email">Email <span aria-hidden="true">*</span></label>
<input type="email" id="email" name="email" required aria-required="true">

<!-- Bottoni icona -->
<button aria-label="Apri menu di navigazione">
  <i class="fas fa-bars" aria-hidden="true"></i>
</button>

<!-- Landmark -->
<main id="main-content" role="main">
<nav aria-label="Navigazione principale">
```

## Librerie CDN

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<!-- AOS Animate -->
<link rel="stylesheet" href="https://unpkg.com/aos@2.3.1/dist/aos.css">
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>

<!-- Leaflet (solo contatti) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

## Template Base Pagina

Ogni pagina deve seguire questa struttura:

1. **Head**: meta, title unico, CDN links
2. **Skip link**: primo elemento body
3. **Navbar**: identica a index.html (link attivo evidenziato)
4. **Hero section**: titolo pagina, sottotitolo, breadcrumb opzionale
5. **Main content**: `<main id="main-content">`
6. **CTA section**: call-to-action verso altra pagina
7. **Footer**: identico a index.html

## Note Sviluppo

- Usare immagini da Unsplash per placeholder (URL diretti)
- Countdown target: `new Date('2026-03-15T09:00:00')`
- Mappa centrata su: `[44.8983, 8.5914]`, zoom 15
- Testare responsive: 375px, 768px, 1024px, 1440px
- Validare HTML: validator.w3.org
- Test accessibilità: WAVE, axe DevTools
