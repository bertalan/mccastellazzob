/**
 * Color Configuration Manager
 * Gestisce i profili colore e le preferenze utente salvate nei cookie
 */

const ColorConfig = {
    // Profili predefiniti
    defaultProfiles: {
        'light': {
            name: 'Chiaro (Default)',
            colors: {
                gold: '#D4AF37',
                goldDark: '#B8941F',
                navy: '#1B263B',
                navyLight: '#2D3E5C',
                amaranth: '#9B1D64',
                amaranthDark: '#7A164F',
                cream: '#FEFCF6',
                warmGray: '#F5F3EE',
                textPrimary: '#1B263B',
                textSecondary: '#4B5563',
                cardBg: '#FFFFFF',
                bodyBg: '#FEFCF6'
            }
        },
        'dark': {
            name: 'Scuro',
            colors: {
                gold: '#D4AF37',
                goldDark: '#B8941F',
                navy: '#0D1321',
                navyLight: '#1B263B',
                amaranth: '#9B1D64',
                amaranthDark: '#7A164F',
                cream: '#1B263B',
                warmGray: '#2D3E5C',
                textPrimary: '#FFFFFF',
                textSecondary: '#9CA3AF',
                cardBg: '#2D3E5C',
                bodyBg: '#0D1321'
            }
        },
        'classic': {
            name: 'Classico',
            colors: {
                gold: '#C9A227',
                goldDark: '#A68B1F',
                navy: '#2C3E50',
                navyLight: '#34495E',
                amaranth: '#8E1651',
                amaranthDark: '#6B1141',
                cream: '#F8F5F0',
                warmGray: '#EBE8E3',
                textPrimary: '#2C3E50',
                textSecondary: '#5D6D7E',
                cardBg: '#FFFFFF',
                bodyBg: '#F8F5F0'
            }
        },
        'racing': {
            name: 'Racing',
            colors: {
                gold: '#FF6B00',
                goldDark: '#CC5500',
                navy: '#1A1A2E',
                navyLight: '#16213E',
                amaranth: '#E94560',
                amaranthDark: '#B83650',
                cream: '#F5F5F5',
                warmGray: '#E8E8E8',
                textPrimary: '#1A1A2E',
                textSecondary: '#4A4A5A',
                cardBg: '#FFFFFF',
                bodyBg: '#F5F5F5'
            }
        },
        'vintage': {
            name: 'Vintage',
            colors: {
                gold: '#8B7355',
                goldDark: '#6B5642',
                navy: '#3D3229',
                navyLight: '#5C4A3D',
                amaranth: '#8B4513',
                amaranthDark: '#6B3410',
                cream: '#FAF0E6',
                warmGray: '#E8DDD0',
                textPrimary: '#3D3229',
                textSecondary: '#6B5B4F',
                cardBg: '#FFFAF5',
                bodyBg: '#FAF0E6'
            }
        }
    },

    // Stato corrente
    currentProfile: 'light',
    customProfiles: {},

    // Inizializza il sistema
    init() {
        this.loadFromCookie();
        this.applyCurrentProfile();
        this.createPanel();
        this.bindEvents();
    },

    // Carica configurazione dai cookie
    loadFromCookie() {
        const saved = this.getCookie('mcColorConfig');
        if (saved) {
            try {
                const config = JSON.parse(saved);
                this.currentProfile = config.currentProfile || 'light';
                this.customProfiles = config.customProfiles || {};
            } catch (e) {
                console.error('Errore nel caricamento configurazione colori:', e);
            }
        }
    },

    // Salva configurazione nei cookie
    saveToCookie() {
        const config = {
            currentProfile: this.currentProfile,
            customProfiles: this.customProfiles
        };
        this.setCookie('mcColorConfig', JSON.stringify(config), 365);
    },

    // Gestione cookie
    setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
    },

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return decodeURIComponent(parts.pop().split(';').shift());
        }
        return null;
    },

    // Ottieni tutti i profili (default + custom)
    getAllProfiles() {
        return { ...this.defaultProfiles, ...this.customProfiles };
    },

    // Ottieni colori del profilo corrente
    getCurrentColors() {
        const profiles = this.getAllProfiles();
        return profiles[this.currentProfile]?.colors || this.defaultProfiles.light.colors;
    },

    // Applica profilo corrente
    applyCurrentProfile() {
        const colors = this.getCurrentColors();
        this.applyColors(colors);
    },

    // Applica colori al DOM
    applyColors(colors) {
        const root = document.documentElement;
        
        // Imposta variabili CSS custom
        root.style.setProperty('--color-gold', colors.gold);
        root.style.setProperty('--color-gold-dark', colors.goldDark);
        root.style.setProperty('--color-navy', colors.navy);
        root.style.setProperty('--color-navy-light', colors.navyLight);
        root.style.setProperty('--color-amaranth', colors.amaranth);
        root.style.setProperty('--color-amaranth-dark', colors.amaranthDark);
        root.style.setProperty('--color-cream', colors.cream);
        root.style.setProperty('--color-warm-gray', colors.warmGray);
        root.style.setProperty('--color-text-primary', colors.textPrimary);
        root.style.setProperty('--color-text-secondary', colors.textSecondary);
        root.style.setProperty('--color-card-bg', colors.cardBg);
        root.style.setProperty('--color-body-bg', colors.bodyBg);

        // Aggiorna Tailwind config dinamicamente
        if (typeof tailwind !== 'undefined' && tailwind.config) {
            tailwind.config.theme.extend.colors = {
                ...tailwind.config.theme.extend.colors,
                'gold': colors.gold,
                'gold-dark': colors.goldDark,
                'navy': colors.navy,
                'navy-light': colors.navyLight,
                'amaranth': colors.amaranth,
                'amaranth-dark': colors.amaranthDark,
                'cream': colors.cream,
                'warm-gray': colors.warmGray,
            };
        }

        // Applica direttamente agli elementi con classi Tailwind
        document.body.style.backgroundColor = colors.bodyBg;
        
        // Aggiorna elementi specifici
        document.querySelectorAll('.bg-cream').forEach(el => el.style.backgroundColor = colors.cream);
        document.querySelectorAll('.bg-warm-gray').forEach(el => el.style.backgroundColor = colors.warmGray);
        document.querySelectorAll('.bg-navy').forEach(el => el.style.backgroundColor = colors.navy);
        document.querySelectorAll('.bg-navy-light').forEach(el => el.style.backgroundColor = colors.navyLight);
        document.querySelectorAll('.bg-gold').forEach(el => el.style.backgroundColor = colors.gold);
        document.querySelectorAll('.bg-gold-dark').forEach(el => el.style.backgroundColor = colors.goldDark);
        document.querySelectorAll('.bg-amaranth').forEach(el => el.style.backgroundColor = colors.amaranth);
        document.querySelectorAll('.bg-amaranth-dark').forEach(el => el.style.backgroundColor = colors.amaranthDark);
        document.querySelectorAll('.bg-white').forEach(el => el.style.backgroundColor = colors.cardBg);
        
        document.querySelectorAll('.text-navy').forEach(el => el.style.color = colors.textPrimary);
        document.querySelectorAll('.text-gold').forEach(el => el.style.color = colors.gold);
        document.querySelectorAll('.text-amaranth').forEach(el => el.style.color = colors.amaranth);
        document.querySelectorAll('.text-gray-600').forEach(el => el.style.color = colors.textSecondary);
        
        document.querySelectorAll('.border-gold').forEach(el => el.style.borderColor = colors.gold);
        document.querySelectorAll('.border-navy').forEach(el => el.style.borderColor = colors.navy);
    },

    // Cambia profilo
    setProfile(profileId) {
        this.currentProfile = profileId;
        this.applyCurrentProfile();
        this.saveToCookie();
        this.updatePanelUI();
    },

    // Salva profilo personalizzato
    saveCustomProfile(name, colors) {
        const id = 'custom_' + Date.now();
        this.customProfiles[id] = {
            name: name,
            colors: { ...colors }
        };
        this.currentProfile = id;
        this.saveToCookie();
        this.applyCurrentProfile();
        this.updatePanelUI();
        return id;
    },

    // Elimina profilo personalizzato
    deleteCustomProfile(id) {
        if (this.customProfiles[id]) {
            delete this.customProfiles[id];
            if (this.currentProfile === id) {
                this.currentProfile = 'light';
                this.applyCurrentProfile();
            }
            this.saveToCookie();
            this.updatePanelUI();
        }
    },

    // Crea il pannello di configurazione
    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'colorConfigPanel';
        panel.className = 'fixed inset-0 z-[9999] hidden';
        panel.innerHTML = `
            <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" id="colorPanelOverlay"></div>
            <div class="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl overflow-y-auto transform translate-x-full transition-transform duration-300" id="colorPanelContent">
                <div class="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between z-10">
                    <h2 class="text-xl font-bold text-gray-900 font-heading">
                        <i class="fas fa-palette mr-2 text-gold"></i>
                        Personalizza Colori
                    </h2>
                    <button id="closeColorPanel" class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 transition flex items-center justify-center" aria-label="Chiudi pannello">
                        <i class="fas fa-times text-gray-600"></i>
                    </button>
                </div>
                
                <div class="p-4 space-y-6">
                    <!-- Profili Predefiniti -->
                    <section>
                        <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Profili Predefiniti</h3>
                        <div class="grid grid-cols-2 gap-3" id="defaultProfilesGrid"></div>
                    </section>
                    
                    <!-- Profili Personalizzati -->
                    <section id="customProfilesSection">
                        <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">I Tuoi Profili</h3>
                        <div class="space-y-2" id="customProfilesList"></div>
                    </section>
                    
                    <!-- Editor Colori -->
                    <section class="border-t border-gray-200 pt-6">
                        <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Crea Nuovo Profilo</h3>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nome Profilo</label>
                            <input type="text" id="newProfileName" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold focus:border-gold" placeholder="Il mio profilo">
                        </div>
                        
                        <div class="space-y-3" id="colorPickers">
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Oro (Primario)</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="gold" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="gold" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#D4AF37">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Oro Scuro</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="goldDark" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="goldDark" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#B8941F">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Navy (Secondario)</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="navy" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="navy" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#1B263B">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Navy Chiaro</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="navyLight" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="navyLight" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#2D3E5C">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Amaranto (Accento)</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="amaranth" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="amaranth" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#9B1D64">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Amaranto Scuro</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="amaranthDark" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="amaranthDark" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#7A164F">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Sfondo Pagina</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="bodyBg" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="bodyBg" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#FEFCF6">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Sfondo Card</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="cardBg" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="cardBg" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#FFFFFF">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Sfondo Sezioni</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="warmGray" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="warmGray" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#F5F3EE">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Testo Principale</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="textPrimary" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="textPrimary" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#1B263B">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Testo Secondario</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="textSecondary" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="textSecondary" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#4B5563">
                                </div>
                            </div>
                            <div class="color-picker-row">
                                <label class="text-sm text-gray-600">Crema</label>
                                <div class="flex gap-2">
                                    <input type="color" data-color="cream" class="color-input w-12 h-10 rounded cursor-pointer border-2 border-gray-200">
                                    <input type="text" data-color-text="cream" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono" placeholder="#FEFCF6">
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex gap-3 mt-6">
                            <button id="previewColors" class="flex-1 bg-gray-100 text-gray-700 font-bold py-3 rounded-lg hover:bg-gray-200 transition">
                                <i class="fas fa-eye mr-2"></i>Anteprima
                            </button>
                            <button id="saveProfile" class="flex-1 bg-gold text-navy font-bold py-3 rounded-lg hover:bg-gold-dark transition">
                                <i class="fas fa-save mr-2"></i>Salva Profilo
                            </button>
                        </div>
                    </section>
                    
                    <!-- Reset -->
                    <section class="border-t border-gray-200 pt-6">
                        <button id="resetToDefault" class="w-full bg-gray-100 text-gray-600 font-medium py-3 rounded-lg hover:bg-gray-200 transition">
                            <i class="fas fa-undo mr-2"></i>Ripristina Predefinito
                        </button>
                    </section>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Crea il pulsante di apertura
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'colorConfigToggle';
        toggleBtn.className = 'fixed bottom-6 right-6 z-[9998] w-14 h-14 bg-gold text-navy rounded-full shadow-lg hover:bg-gold-dark transition flex items-center justify-center';
        toggleBtn.setAttribute('aria-label', 'Apri pannello colori');
        toggleBtn.innerHTML = '<i class="fas fa-palette text-xl"></i>';
        document.body.appendChild(toggleBtn);
        
        this.updatePanelUI();
    },

    // Aggiorna UI del pannello
    updatePanelUI() {
        // Profili predefiniti
        const defaultGrid = document.getElementById('defaultProfilesGrid');
        if (defaultGrid) {
            defaultGrid.innerHTML = Object.entries(this.defaultProfiles).map(([id, profile]) => `
                <button class="profile-btn p-3 rounded-xl border-2 transition ${this.currentProfile === id ? 'border-gold bg-gold/10' : 'border-gray-200 hover:border-gold/50'}" data-profile="${id}">
                    <div class="flex gap-1 mb-2">
                        <span class="w-4 h-4 rounded-full" style="background:${profile.colors.gold}"></span>
                        <span class="w-4 h-4 rounded-full" style="background:${profile.colors.navy}"></span>
                        <span class="w-4 h-4 rounded-full" style="background:${profile.colors.amaranth}"></span>
                        <span class="w-4 h-4 rounded-full" style="background:${profile.colors.bodyBg}; border: 1px solid #ddd;"></span>
                    </div>
                    <span class="text-sm font-medium text-gray-700">${profile.name}</span>
                    ${this.currentProfile === id ? '<i class="fas fa-check text-gold ml-2"></i>' : ''}
                </button>
            `).join('');
        }

        // Profili personalizzati
        const customList = document.getElementById('customProfilesList');
        const customSection = document.getElementById('customProfilesSection');
        
        if (customList && customSection) {
            const customEntries = Object.entries(this.customProfiles);
            
            if (customEntries.length === 0) {
                customSection.style.display = 'none';
            } else {
                customSection.style.display = 'block';
                customList.innerHTML = customEntries.map(([id, profile]) => `
                    <div class="flex items-center gap-2 p-3 rounded-xl border-2 transition ${this.currentProfile === id ? 'border-gold bg-gold/10' : 'border-gray-200'}">
                        <button class="profile-btn flex-1 flex items-center gap-2" data-profile="${id}">
                            <div class="flex gap-1">
                                <span class="w-3 h-3 rounded-full" style="background:${profile.colors.gold}"></span>
                                <span class="w-3 h-3 rounded-full" style="background:${profile.colors.navy}"></span>
                                <span class="w-3 h-3 rounded-full" style="background:${profile.colors.amaranth}"></span>
                            </div>
                            <span class="text-sm font-medium text-gray-700">${profile.name}</span>
                            ${this.currentProfile === id ? '<i class="fas fa-check text-gold"></i>' : ''}
                        </button>
                        <button class="delete-profile-btn w-8 h-8 rounded-full bg-red-100 hover:bg-red-200 text-red-600 transition flex items-center justify-center" data-delete="${id}" aria-label="Elimina ${profile.name}">
                            <i class="fas fa-trash text-xs"></i>
                        </button>
                    </div>
                `).join('');
            }
        }

        // Popola color picker con colori correnti
        this.populateColorPickers();
    },

    // Popola i color picker
    populateColorPickers() {
        const colors = this.getCurrentColors();
        
        Object.entries(colors).forEach(([key, value]) => {
            const picker = document.querySelector(`[data-color="${key}"]`);
            const text = document.querySelector(`[data-color-text="${key}"]`);
            
            if (picker) picker.value = value;
            if (text) text.value = value;
        });
    },

    // Ottieni colori dal form
    getColorsFromForm() {
        const colors = {};
        document.querySelectorAll('[data-color]').forEach(picker => {
            colors[picker.dataset.color] = picker.value;
        });
        return colors;
    },

    // Bind eventi
    bindEvents() {
        // Toggle pannello
        document.getElementById('colorConfigToggle')?.addEventListener('click', () => this.openPanel());
        document.getElementById('closeColorPanel')?.addEventListener('click', () => this.closePanel());
        document.getElementById('colorPanelOverlay')?.addEventListener('click', () => this.closePanel());
        
        // Selezione profilo
        document.addEventListener('click', (e) => {
            const profileBtn = e.target.closest('.profile-btn');
            if (profileBtn) {
                this.setProfile(profileBtn.dataset.profile);
            }
            
            const deleteBtn = e.target.closest('.delete-profile-btn');
            if (deleteBtn) {
                if (confirm('Eliminare questo profilo?')) {
                    this.deleteCustomProfile(deleteBtn.dataset.delete);
                }
            }
        });
        
        // Sync color picker con input text
        document.querySelectorAll('[data-color]').forEach(picker => {
            picker.addEventListener('input', (e) => {
                const key = e.target.dataset.color;
                const text = document.querySelector(`[data-color-text="${key}"]`);
                if (text) text.value = e.target.value;
            });
        });
        
        document.querySelectorAll('[data-color-text]').forEach(text => {
            text.addEventListener('input', (e) => {
                const key = e.target.dataset.colorText;
                const picker = document.querySelector(`[data-color="${key}"]`);
                if (picker && /^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
                    picker.value = e.target.value;
                }
            });
        });
        
        // Anteprima
        document.getElementById('previewColors')?.addEventListener('click', () => {
            this.applyColors(this.getColorsFromForm());
        });
        
        // Salva profilo
        document.getElementById('saveProfile')?.addEventListener('click', () => {
            const name = document.getElementById('newProfileName')?.value.trim();
            if (!name) {
                alert('Inserisci un nome per il profilo');
                return;
            }
            this.saveCustomProfile(name, this.getColorsFromForm());
            document.getElementById('newProfileName').value = '';
            alert('Profilo salvato!');
        });
        
        // Reset
        document.getElementById('resetToDefault')?.addEventListener('click', () => {
            this.setProfile('light');
        });

        // Chiudi con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closePanel();
        });
    },

    // Apri pannello
    openPanel() {
        const panel = document.getElementById('colorConfigPanel');
        const content = document.getElementById('colorPanelContent');
        
        if (panel && content) {
            panel.classList.remove('hidden');
            setTimeout(() => {
                content.classList.remove('translate-x-full');
            }, 10);
        }
    },

    // Chiudi pannello
    closePanel() {
        const panel = document.getElementById('colorConfigPanel');
        const content = document.getElementById('colorPanelContent');
        
        if (panel && content) {
            content.classList.add('translate-x-full');
            setTimeout(() => {
                panel.classList.add('hidden');
            }, 300);
        }
    }
};

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => ColorConfig.init());
