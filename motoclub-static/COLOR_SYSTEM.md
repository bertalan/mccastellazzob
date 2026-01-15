# Sistema di Gestione Colori - Moto Club Castellazzo Bormida

## 📋 Panoramica

Sistema completo per la gestione, esportazione e importazione dei profili colore del sito web. Permette di passare facilmente da un tema all'altro e di personalizzare la palette di colori.

## 🎨 Colori Attuali - Profilo Caldo

Basato sui colori ufficiali del logo del Moto Club:

### Colori Primari
- **Oro brillante**: `#ffd700` - Usato per navbar, elementi dorati e accenti
- **Oro scuro**: `#f6c401` - Usato per hover e variazioni
- **Bordeaux**: `#ab0031` - Usato per bottoni, elementi in evidenza

### Colori Secondari
- **Navy**: `#1B263B` - Sfondo scuro, contrasto
- **Amaranth**: `#9B1D64` - Accenti alternativi

### Applicazioni
- **Navbar**: Gradiente bordeaux-navy con testo dorato
- **Bottoni CTA**: Bordeaux con effetto hover dorato
- **Card in hover**: Ombra dorata `--shadow-gold`
- **Timeline**: Marker bordeaux con testo dorato
- **Scrollbar**: Gradiente con i colori principali

## 📁 File del Sistema

### 1. `colors.json`
File principale di configurazione con tutti i profili colore disponibili.

```json
{
  "version": "1.0.0",
  "profiles": {
    "motoclub-warm": { ... },
    "classic": { ... }
  },
  "active": "motoclub-warm"
}
```

**Struttura di un profilo:**
```json
{
  "name": "Nome Profilo",
  "description": "Descrizione",
  "colors": {
    "primary": { "gold", "goldDark", "bordeaux" },
    "secondary": { "navy", "amaranth", "cream" },
    "neutral": { "white", "black", "gray*" },
    "gradients": { "primary", "hero", "card", "navbar" },
    "shadows": { "gold", "bordeaux" },
    "ui": { "navbar", "button", "accent", "highlight" }
  }
}
```

### 2. `js/color-manager.js`
Script JavaScript per la gestione dinamica dei colori.

**Funzionalità:**
- ✅ Caricamento automatico da `colors.json`
- ✅ Applicazione profili tramite CSS variables
- ✅ Esportazione configurazione in JSON
- ✅ Importazione profili personalizzati
- ✅ UI di controllo integrata
- ✅ Fallback colors se il file non è disponibile

### 3. `css/style.css`
File CSS con le variabili di colore aggiornate.

**Variabili CSS principali:**
```css
:root {
  --gold: #ffd700;
  --gold-dark: #f6c401;
  --bordeaux: #ab0031;
  --gradient-primary: linear-gradient(135deg, ...);
  --gradient-navbar: linear-gradient(135deg, ...);
  --shadow-gold: 0 10px 30px rgba(255, 215, 0, 0.3);
  --shadow-bordeaux: 0 8px 25px rgba(171, 0, 49, 0.25);
}
```

## 🚀 Utilizzo

### Installazione

1. Assicurati che i file siano nella posizione corretta:
```
motoclub-static/
├── colors.json
├── js/
│   └── color-manager.js
└── css/
    └── style.css
```

2. Includi lo script nel tuo HTML:
```html
<script src="js/color-manager.js"></script>
```

### Uso tramite UI

1. Clicca sull'icona 🎨 in alto a destra
2. Seleziona un profilo dal menu dropdown
3. I colori si applicano automaticamente

### Esportare i Colori

1. Clicca sul pulsante "📤 Esporta"
2. Salva il file JSON generato
3. Il file contiene tutti i profili e la configurazione corrente

### Importare i Colori

1. Clicca sul pulsante "📥 Importa"
2. Seleziona un file JSON con profili colore
3. I nuovi profili vengono aggiunti al menu

### Uso Programmatico

```javascript
// Accedi al manager globale
const cm = window.colorManager;

// Applica un profilo
cm.applyProfile('motoclub-warm');

// Ottieni i colori correnti
const colors = cm.getCurrentColors();

// Esporta configurazione
cm.exportToJSON();

// Carica da JSON
await cm.loadFromJSON();
```

## 🎯 Creare un Nuovo Profilo

1. **Tramite JSON:**

Crea/modifica `colors.json`:
```json
{
  "profiles": {
    "mio-profilo": {
      "name": "Il Mio Profilo",
      "description": "Descrizione personalizzata",
      "colors": {
        "primary": {
          "gold": "#FFAA00",
          "goldDark": "#DD8800",
          "bordeaux": "#CC0044"
        },
        // ... altri colori
      }
    }
  }
}
```

2. **Tramite JavaScript:**

```javascript
const myProfile = {
  name: "Custom Profile",
  colors: { /* ... */ }
};

colorManager.profiles['custom'] = myProfile;
colorManager.applyProfile('custom');
colorManager.exportToJSON(); // Salva
```

## 🎨 Profili Disponibili

### 1. Moto Club Warm (Default)
- Profilo caldo ispirato al logo ufficiale
- Oro brillante e bordeaux intenso
- Ideale per eventi e comunicazioni dinamiche

### 2. Classic Original
- Profilo originale con colori classici
- Oro meno brillante, più elegante
- Ideale per pagine istituzionali

## 🔧 Personalizzazione Avanzata

### Modificare la Navbar

Nel file `color-manager.js`, metodo `updateNavbar()`:
```javascript
updateNavbar(colors) {
  const header = document.getElementById('header');
  header.style.background = colors.gradients.navbar;
  // Personalizza qui
}
```

### Aggiungere Nuove Variabili CSS

1. Aggiungi al profilo in `colors.json`:
```json
"colors": {
  "custom": {
    "myColor": "#123456"
  }
}
```

2. Applica in `color-manager.js`:
```javascript
root.style.setProperty('--my-color', colors.custom.myColor);
```

3. Usa nel CSS:
```css
.my-element {
  color: var(--my-color);
}
```

## 📊 Migliori Pratiche

1. **Contrasto**: Mantieni sempre un contrasto sufficiente per l'accessibilità
2. **Coerenza**: Usa i colori UI definiti per bottoni e elementi interattivi
3. **Performance**: Le variabili CSS sono applicate istantaneamente
4. **Backup**: Esporta la configurazione prima di modifiche importanti
5. **Testing**: Testa i profili su tutti i dispositivi

## 🐛 Troubleshooting

### I colori non si applicano
- Verifica che `colors.json` sia accessibile
- Controlla la console per errori
- Il fallback verrà caricato automaticamente

### Il pannello non appare
- Verifica che lo script sia caricato dopo il DOM
- Controlla che non ci siano conflitti CSS

### L'importazione fallisce
- Verifica la struttura del JSON
- Assicurati che il file sia valido

## 📝 Note Tecniche

- **CSS Variables**: Supporto moderno (IE11 non supportato)
- **Storage**: Nessun localStorage, solo file JSON
- **Performance**: Nessun impatto, applicazione istantanea
- **Compatibilità**: Chrome, Firefox, Safari, Edge moderni

## 🔄 Workflow Consigliato

1. Sviluppo locale: modifica `colors.json`
2. Test: usa l'UI per provare i profili
3. Esporta: salva la configurazione testata
4. Deploy: carica il nuovo `colors.json`
5. Share: condividi i profili con il team

## 📞 Supporto

Per problemi o domande:
- Controlla la console del browser per errori
- Verifica che tutti i file siano nella posizione corretta
- Consulta questo README per le funzionalità disponibili

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: Gennaio 2026  
**Moto Club Castellazzo Bormida** - Dal 1933
