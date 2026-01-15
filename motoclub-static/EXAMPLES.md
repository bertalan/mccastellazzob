# Esempi di Utilizzo - Sistema Gestione Colori

## 🔧 CLI - Color Tools Script

### Validare il file colors.json
```bash
python3 color-tools.py colors.json validate
```

### Elencare tutti i profili
```bash
python3 color-tools.py colors.json list
```
Output:
```
✓ Validazione completata: 2 profili validi

📋 Profili disponibili (2):

→ motoclub-warm
  Nome: Moto Club Warm
  Descrizione: Profilo caldo con oro e bordeaux dal logo ufficiale
  Primary: 3 colori
  Secondary: 3 colori
  Ui: 6 colori
```

### Esportare variabili CSS
```bash
python3 color-tools.py colors.json export-css motoclub-warm warm-colors.css
```

### Esportare variabili SCSS
```bash
python3 color-tools.py colors.json export-scss classic classic-colors.scss
```

### Creare un nuovo profilo
```bash
# Profilo vuoto
python3 color-tools.py colors.json create custom

# Copia da profilo esistente
python3 color-tools.py colors.json create custom-warm motoclub-warm
```

### Cambiare profilo attivo
```bash
python3 color-tools.py colors.json activate classic
```

---

## 🌐 JavaScript API

### Inizializzazione
```javascript
// Automatico al caricamento pagina
document.addEventListener('DOMContentLoaded', () => {
    window.colorManager = new ColorManager();
    window.colorManager.init();
});
```

### Cambiare profilo
```javascript
colorManager.applyProfile('motoclub-warm');
```

### Ottenere i colori correnti
```javascript
const colors = colorManager.getCurrentColors();
console.log(colors.primary.gold); // #ffd700
```

### Esportare configurazione
```javascript
colorManager.exportToJSON();
// Scarica: motoclub-colors-[timestamp].json
```

### Importare configurazione
```javascript
colorManager.importFromJSON();
// Apre dialog di selezione file
```

### Accedere ai profili
```javascript
// Tutti i profili
const profiles = colorManager.getAllProfiles();

// Profilo corrente
const current = colorManager.currentProfile;
```

---

## 🎨 CSS Variables

### Usare i colori nel CSS
```css
.my-element {
    /* Colori primari */
    color: var(--gold);
    background: var(--bordeaux);
    border-color: var(--gold-dark);
    
    /* Gradienti */
    background: var(--gradient-primary);
    background: var(--gradient-navbar);
    
    /* Ombre */
    box-shadow: var(--shadow-gold);
    box-shadow: var(--shadow-bordeaux);
}

.navbar {
    background: var(--gradient-navbar);
}

.btn-primary {
    background: var(--bordeaux);
    color: white;
}

.btn-primary:hover {
    background: var(--gold-dark);
    box-shadow: var(--shadow-gold);
}
```

### Override inline
```html
<div style="color: var(--gold); background: var(--bordeaux);">
    Testo dorato su sfondo bordeaux
</div>
```

---

## 📝 Modificare colors.json

### Aggiungere un nuovo colore
```json
{
  "profiles": {
    "motoclub-warm": {
      "colors": {
        "primary": {
          "gold": "#ffd700",
          "goldDark": "#f6c401",
          "bordeaux": "#ab0031",
          "newColor": "#123456"  // ← Nuovo colore
        }
      }
    }
  }
}
```

### Creare un gradiente personalizzato
```json
{
  "gradients": {
    "custom": "linear-gradient(135deg, #ab0031 0%, #ffd700 100%)",
    "radial": "radial-gradient(circle, #f6c401 0%, #ab0031 100%)"
  }
}
```

### Aggiungere un nuovo profilo completo
```json
{
  "profiles": {
    "my-profile": {
      "name": "Il Mio Profilo",
      "description": "Descrizione personalizzata",
      "colors": {
        "primary": {
          "gold": "#FFAA00",
          "goldDark": "#DD8800",
          "bordeaux": "#CC0044"
        },
        "ui": {
          "navbar": "#FFAA00",
          "button": "#CC0044"
        }
      }
    }
  },
  "active": "my-profile"
}
```

---

## 🔄 Workflow Completo

### 1. Sviluppo locale
```bash
# Modifica colors.json
nano colors.json

# Valida
python3 color-tools.py colors.json validate

# Esporta CSS per anteprima
python3 color-tools.py colors.json export-css motoclub-warm preview.css
```

### 2. Test nel browser
```javascript
// Console del browser
colorManager.applyProfile('motoclub-warm');
```

### 3. Esporta e salva
```javascript
// Nel browser
colorManager.exportToJSON();
```

### 4. Deploy
```bash
# Copia il file testato
cp colors.json /path/to/production/

# Ricarica la pagina
# Il nuovo profilo si applica automaticamente
```

---

## 🎯 Casi d'Uso Comuni

### Tema stagionale
```json
{
  "profiles": {
    "summer": {
      "colors": {
        "primary": {
          "gold": "#FFD700",
          "bordeaux": "#FF6B00"
        }
      }
    },
    "winter": {
      "colors": {
        "primary": {
          "gold": "#C0C0C0",
          "bordeaux": "#0066CC"
        }
      }
    }
  }
}
```

### Tema evento speciale
```json
{
  "profiles": {
    "raduno-2026": {
      "name": "Raduno 2026",
      "colors": {
        "primary": {
          "gold": "#ffd700",
          "bordeaux": "#ab0031"
        },
        "ui": {
          "navbar": "#ffd700",
          "button": "#ab0031"
        }
      }
    }
  }
}
```

### A/B Testing
```javascript
// Assegna profilo random
const profiles = ['motoclub-warm', 'classic'];
const random = profiles[Math.floor(Math.random() * profiles.length)];
colorManager.applyProfile(random);
```

---

## 🐛 Debug

### Verificare colori applicati
```javascript
// Console
const root = document.documentElement;
console.log(getComputedStyle(root).getPropertyValue('--gold'));
// Output: #ffd700
```

### Ispezionare profilo corrente
```javascript
console.log(colorManager.currentProfile);
console.log(colorManager.getCurrentColors());
```

### Controllare fallback
```javascript
// Se colors.json non carica, vengono usati i colori fallback
console.log(colorManager.profiles);
```

---

## 📦 Integrazione in Template Django/Jinja

```jinja2
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header id="header">
        <!-- Navbar con colori dinamici -->
    </header>
    
    <script src="{% static 'js/color-manager.js' %}"></script>
    <script>
        // Applica profilo da variabile backend
        document.addEventListener('DOMContentLoaded', () => {
            {% if user_color_preference %}
            colorManager.applyProfile('{{ user_color_preference }}');
            {% endif %}
        });
    </script>
</body>
</html>
```

---

## 📊 Performance

- **Caricamento iniziale**: ~100ms
- **Cambio profilo**: Istantaneo (<10ms)
- **Dimensione file**: ~3KB (colors.json)
- **Browser support**: Moderni (Chrome, Firefox, Safari, Edge)

---

## ✅ Checklist

Prima del deploy:

- [ ] Validare colors.json con lo script
- [ ] Testare tutti i profili nel browser
- [ ] Verificare contrasto colori (accessibilità)
- [ ] Esportare backup della configurazione
- [ ] Testare su dispositivi mobili
- [ ] Verificare che il fallback funzioni

---

**Moto Club Castellazzo Bormida** - Sistema Colori v1.0.0
