/**
 * Color Manager - Sistema di gestione colori per il sito Moto Club
 * Permette l'importazione/esportazione di profili colore da file JSON
 */

class ColorManager {
    constructor() {
        this.currentProfile = null;
        this.profiles = {};
        this.colorsFile = '/colors.json';
    }

    /**
     * Inizializza il color manager
     */
    async init() {
        try {
            await this.loadFromJSON();
            this.applyActiveProfile();
            this.createUI();
        } catch (error) {
            console.error('Errore inizializzazione color manager:', error);
            this.loadFallbackColors();
        }
    }

    /**
     * Carica i colori dal file JSON
     */
    async loadFromJSON() {
        try {
            const response = await fetch(this.colorsFile);
            if (!response.ok) throw new Error('File non trovato');
            
            const data = await response.json();
            this.profiles = data.profiles;
            this.currentProfile = data.active || 'motoclub-warm';
            
            console.log('✓ Profili colore caricati:', Object.keys(this.profiles));
            return data;
        } catch (error) {
            console.error('Errore caricamento colors.json:', error);
            throw error;
        }
    }

    /**
     * Esporta la configurazione corrente come JSON
     */
    exportToJSON() {
        const config = {
            version: "1.0.0",
            profiles: this.profiles,
            active: this.currentProfile,
            exported: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(config, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `motoclub-colors-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✓ Configurazione esportata');
    }

    /**
     * Importa una configurazione da file JSON
     */
    importFromJSON() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = async (e) => {
            try {
                const file = e.target.files[0];
                const text = await file.text();
                const config = JSON.parse(text);
                
                // Valida la struttura
                if (!config.profiles || typeof config.profiles !== 'object') {
                    throw new Error('Formato file non valido');
                }
                
                // Merge con i profili esistenti
                this.profiles = { ...this.profiles, ...config.profiles };
                
                if (config.active && this.profiles[config.active]) {
                    this.currentProfile = config.active;
                    this.applyProfile(config.active);
                }
                
                console.log('✓ Configurazione importata:', Object.keys(config.profiles));
                alert(`Importati ${Object.keys(config.profiles).length} profili!`);
                
                // Aggiorna UI
                this.updateProfileSelector();
            } catch (error) {
                console.error('Errore importazione:', error);
                alert('Errore: ' + error.message);
            }
        };
        
        input.click();
    }

    /**
     * Applica il profilo attivo
     */
    applyActiveProfile() {
        if (this.profiles[this.currentProfile]) {
            this.applyProfile(this.currentProfile);
        } else {
            console.warn('Profilo non trovato, uso fallback');
            this.loadFallbackColors();
        }
    }

    /**
     * Applica un profilo specifico
     */
    applyProfile(profileName) {
        const profile = this.profiles[profileName];
        if (!profile) {
            console.error('Profilo non trovato:', profileName);
            return;
        }

        this.currentProfile = profileName;
        const colors = profile.colors;
        const root = document.documentElement;

        // Colori primari
        root.style.setProperty('--gold', colors.primary.gold);
        root.style.setProperty('--gold-dark', colors.primary.goldDark);
        root.style.setProperty('--bordeaux', colors.primary.bordeaux);

        // Colori secondari
        root.style.setProperty('--navy', colors.secondary.navy);
        root.style.setProperty('--amaranth', colors.secondary.amaranth);
        root.style.setProperty('--cream', colors.secondary.cream);

        // Colori neutri
        Object.entries(colors.neutral).forEach(([key, value]) => {
            const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase();
            root.style.setProperty(`--${cssVar}`, value);
        });

        // Gradienti (se presenti)
        if (colors.gradients) {
            root.style.setProperty('--gradient-primary', colors.gradients.primary);
            root.style.setProperty('--gradient-hero', colors.gradients.hero);
            root.style.setProperty('--gradient-card', colors.gradients.card);
            root.style.setProperty('--gradient-navbar', colors.gradients.navbar);
        }

        // Ombre
        root.style.setProperty('--shadow-gold', colors.shadows.gold);
        root.style.setProperty('--shadow-bordeaux', colors.shadows.bordeaux);

        // UI Elements
        if (colors.ui) {
            Object.entries(colors.ui).forEach(([key, value]) => {
                const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase();
                root.style.setProperty(`--ui-${cssVar}`, value);
            });
        }

        // Aggiorna elementi specifici
        this.updateNavbar(colors);
        this.updateHero(colors);
        this.updateFooter(colors);
        this.updateButtons(colors);
        this.updateHighlights(colors);

        console.log(`✓ Applicato profilo: ${profile.name}`);
    }

    /**
     * Aggiorna stile navbar
     */
    updateNavbar(colors) {
        const navbar = document.getElementById('navbar');
        if (navbar && colors.ui && colors.ui.navbarBg) {
            navbar.style.backgroundColor = colors.ui.navbarBg;
        }

        // Logo text
        const logoText = document.getElementById('logo-text');
        if (logoText && colors.ui && colors.ui.navbarText) {
            logoText.style.color = colors.ui.navbarText;
        }

        // Nav links
        const navLinks = document.querySelectorAll('nav a:not(.bg-bordeaux)');
        navLinks.forEach(link => {
            if (colors.ui && colors.ui.navbarText) {
                link.style.color = colors.ui.navbarText;
            }
        });
    }

    /**
     * Aggiorna hero section
     */
    updateHero(colors) {
        const hero = document.getElementById('hero');
        if (hero && colors.ui && colors.ui.heroBg) {
            hero.style.backgroundColor = colors.ui.heroBg;
        }
    }

    /**
     * Aggiorna footer
     */
    updateFooter(colors) {
        const footer = document.getElementById('footer');
        if (footer && colors.ui && colors.ui.footerBg) {
            footer.style.backgroundColor = colors.ui.footerBg;
        }
    }

    /**
     * Aggiorna bottoni
     */
    updateButtons(colors) {
        const buttons = document.querySelectorAll('.btn-primary, .cta-button, .bg-bordeaux');
        buttons.forEach(btn => {
            if (colors.ui && colors.ui.button) {
                btn.style.backgroundColor = colors.ui.button;
                if (colors.ui.buttonText) {
                    btn.style.color = colors.ui.buttonText;
                }
            });
        });
    }

    /**
     * Aggiorna elementi in evidenza
     */
    updateHighlights(colors) {
        // Titoli sezioni
        document.querySelectorAll('.section-title::after').forEach(el => {
            el.style.background = colors.gradients.primary;
        });

        // Cards e elementi con ombre dorate
        document.querySelectorAll('.card, .event-card, .member-card').forEach(el => {
            el.addEventListener('mouseenter', () => {
                el.style.boxShadow = colors.shadows.gold;
            });
            el.addEventListener('mouseleave', () => {
                el.style.boxShadow = '';
            });
        });
    }

    /**
     * Crea pannello di controllo UI
     */
    createUI() {
        const panel = document.createElement('div');
        panel.id = 'color-manager-panel';
        panel.style.cssText = `
            position: fixed;
            top: 180px;
            right: 30px;
            z-index: 999;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            min-width: 200px;
            display: none;
        `;

        panel.innerHTML = `
            <h4 style="margin: 0 0 1rem 0; font-size: 0.9rem; color: #333;">Gestione Colori</h4>
            <select id="profile-selector" style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; border: 1px solid #ddd; border-radius: 0.5rem;">
                ${Object.entries(this.profiles).map(([key, profile]) => 
                    `<option value="${key}" ${key === this.currentProfile ? 'selected' : ''}>${profile.name}</option>`
                ).join('')}
            </select>
            <button id="export-colors" style="width: 100%; padding: 0.5rem; margin-bottom: 0.25rem; background: var(--gold); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                📤 Esporta
            </button>
            <button id="import-colors" style="width: 100%; padding: 0.5rem; background: var(--bordeaux); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                📥 Importa
            </button>
        `;

        document.body.appendChild(panel);

        // Toggle button
        const toggle = document.createElement('button');
        toggle.id = 'color-manager-toggle';
        toggle.innerHTML = '🎨';
        toggle.style.cssText = `
            position: fixed;
            top: 180px;
            right: 30px;
            z-index: 999;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--gold) 0%, var(--bordeaux) 100%);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        `;

        toggle.addEventListener('click', () => {
            const isVisible = panel.style.display === 'block';
            panel.style.display = isVisible ? 'none' : 'block';
            toggle.style.transform = isVisible ? 'scale(1)' : 'scale(0.9)';
        });

        document.body.appendChild(toggle);

        // Event listeners
        document.getElementById('profile-selector').addEventListener('change', (e) => {
            this.applyProfile(e.target.value);
        });

        document.getElementById('export-colors').addEventListener('click', () => {
            this.exportToJSON();
        });

        document.getElementById('import-colors').addEventListener('click', () => {
            this.importFromJSON();
        });
    }

    /**
     * Aggiorna il selettore profili
     */
    updateProfileSelector() {
        const selector = document.getElementById('profile-selector');
        if (selector) {
            selector.innerHTML = Object.entries(this.profiles).map(([key, profile]) => 
                `<option value="${key}" ${key === this.currentProfile ? 'selected' : ''}>${profile.name}</option>`
            ).join('');
        }
    }

    /**
     * Carica colori di fallback
     */
    loadFallbackColors() {
        console.warn('Caricamento colori di fallback...');
        this.profiles = {
            'motoclub-warm': {
                name: 'Moto Club Warm',
                colors: {
                    primary: { gold: '#ffd700', goldDark: '#f6c401', bordeaux: '#ab0031' },
                    secondary: { navy: '#1B263B', amaranth: '#9B1D64', cream: '#FEFCF6' },
                    neutral: {
                        white: '#FFFFFF',
                        black: '#0A0E14',
                        gray50: '#F9FAFB',
                        gray100: '#F3F4F6',
                        gray200: '#E5E7EB',
                        gray300: '#D1D5DB',
                        gray700: '#374151',
                        gray800: '#1F2937',
                        gray900: '#111827'
                    },
                    gradients: {
                        primary: 'linear-gradient(135deg, #ab0031 0%, #f6c401 50%, #ffd700 100%)',
                        hero: 'linear-gradient(135deg, rgba(171, 0, 49, 0.95) 0%, rgba(246, 196, 1, 0.85) 50%, rgba(255, 215, 0, 0.75) 100%)',
                        card: 'linear-gradient(145deg, rgba(171, 0, 49, 0.6) 0%, rgba(246, 196, 1, 0.4) 100%)',
                        navbar: 'linear-gradient(135deg, rgba(171, 0, 49, 0.95) 0%, rgba(27, 38, 59, 0.95) 100%)'
                    },
                    shadows: {
                        gold: '0 10px 30px rgba(255, 215, 0, 0.3)',
                        bordeaux: '0 8px 25px rgba(171, 0, 49, 0.25)'
                    },
                    ui: {
                        navbar: '#ffd700',
                        navbarHover: '#f6c401',
                        button: '#ab0031',
                        buttonHover: '#8b002a',
                        accent: '#f6c401',
                        highlight: '#ffd700'
                    }
                }
            }
        };
        this.currentProfile = 'motoclub-warm';
        this.applyActiveProfile();
    }
}

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    window.colorManager = new ColorManager();
    window.colorManager.init();
});

// Esporta per uso in console
window.ColorManager = ColorManager;
