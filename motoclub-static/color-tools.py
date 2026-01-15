#!/usr/bin/env python3
"""
Color JSON Validator and Converter
Strumento per validare, convertire e manipolare i file colors.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


class ColorValidator:
    """Valida e manipola file JSON di configurazione colori"""
    
    REQUIRED_KEYS = {
        'version', 'profiles', 'active'
    }
    
    PROFILE_KEYS = {
        'name', 'colors'
    }
    
    COLOR_CATEGORIES = {
        'primary', 'secondary', 'neutral', 'gradients', 'shadows', 'ui'
    }
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data: Dict[str, Any] = {}
    
    def load(self) -> bool:
        """Carica il file JSON"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✓ File caricato: {self.file_path}")
            return True
        except FileNotFoundError:
            print(f"✗ File non trovato: {self.file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Errore JSON: {e}")
            return False
    
    def validate(self) -> bool:
        """Valida la struttura del file"""
        if not self.data:
            print("✗ Nessun dato caricato")
            return False
        
        # Verifica chiavi principali
        missing = self.REQUIRED_KEYS - set(self.data.keys())
        if missing:
            print(f"✗ Chiavi mancanti: {missing}")
            return False
        
        # Verifica profili
        profiles = self.data.get('profiles', {})
        if not profiles:
            print("✗ Nessun profilo definito")
            return False
        
        # Valida ogni profilo
        for profile_name, profile_data in profiles.items():
            if not self._validate_profile(profile_name, profile_data):
                return False
        
        # Verifica che il profilo attivo esista
        active = self.data.get('active')
        if active not in profiles:
            print(f"✗ Profilo attivo '{active}' non trovato")
            return False
        
        print(f"✓ Validazione completata: {len(profiles)} profili validi")
        return True
    
    def _validate_profile(self, name: str, data: Dict) -> bool:
        """Valida un singolo profilo"""
        missing = self.PROFILE_KEYS - set(data.keys())
        if missing:
            print(f"✗ Profilo '{name}': chiavi mancanti {missing}")
            return False
        
        colors = data.get('colors', {})
        if not colors:
            print(f"✗ Profilo '{name}': nessun colore definito")
            return False
        
        return True
    
    def list_profiles(self):
        """Elenca tutti i profili disponibili"""
        profiles = self.data.get('profiles', {})
        active = self.data.get('active')
        
        print(f"\n📋 Profili disponibili ({len(profiles)}):\n")
        for name, profile in profiles.items():
            marker = "→" if name == active else " "
            print(f"{marker} {name}")
            print(f"  Nome: {profile.get('name', 'N/A')}")
            if 'description' in profile:
                print(f"  Descrizione: {profile['description']}")
            
            # Conta colori per categoria
            colors = profile.get('colors', {})
            for category in ['primary', 'secondary', 'ui']:
                if category in colors:
                    count = len(colors[category])
                    print(f"  {category.capitalize()}: {count} colori")
            print()
    
    def extract_colors(self, profile_name: str) -> Dict[str, str]:
        """Estrae tutti i colori di un profilo in formato piatto"""
        profiles = self.data.get('profiles', {})
        profile = profiles.get(profile_name)
        
        if not profile:
            print(f"✗ Profilo '{profile_name}' non trovato")
            return {}
        
        colors_flat = {}
        colors = profile.get('colors', {})
        
        for category, values in colors.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, str) and value.startswith('#'):
                        colors_flat[f"{category}_{key}"] = value
        
        return colors_flat
    
    def export_css_variables(self, profile_name: str, output_file: str):
        """Esporta i colori come variabili CSS"""
        colors = self.extract_colors(profile_name)
        
        if not colors:
            print(f"✗ Nessun colore da esportare")
            return
        
        css_content = f"/* Colori profilo: {profile_name} */\n:root {{\n"
        
        for name, value in colors.items():
            css_var = name.replace('_', '-')
            css_content += f"    --{css_var}: {value};\n"
        
        css_content += "}\n"
        
        output_path = Path(output_file)
        output_path.write_text(css_content, encoding='utf-8')
        print(f"✓ Variabili CSS esportate in: {output_path}")
    
    def convert_to_scss(self, profile_name: str, output_file: str):
        """Converte i colori in variabili SCSS"""
        colors = self.extract_colors(profile_name)
        
        if not colors:
            print(f"✗ Nessun colore da convertire")
            return
        
        scss_content = f"// Colori profilo: {profile_name}\n\n"
        
        for name, value in colors.items():
            scss_var = name.replace('_', '-')
            scss_content += f"${scss_var}: {value};\n"
        
        output_path = Path(output_file)
        output_path.write_text(scss_content, encoding='utf-8')
        print(f"✓ Variabili SCSS esportate in: {output_path}")
    
    def create_profile(self, name: str, base_profile: str = None):
        """Crea un nuovo profilo da zero o copiando uno esistente"""
        profiles = self.data.get('profiles', {})
        
        if name in profiles:
            print(f"✗ Profilo '{name}' già esistente")
            return False
        
        if base_profile:
            if base_profile not in profiles:
                print(f"✗ Profilo base '{base_profile}' non trovato")
                return False
            
            # Copia profilo esistente
            new_profile = json.loads(json.dumps(profiles[base_profile]))
            new_profile['name'] = name
            print(f"✓ Profilo '{name}' creato da '{base_profile}'")
        else:
            # Crea profilo vuoto
            new_profile = {
                "name": name,
                "description": "Profilo personalizzato",
                "colors": {
                    "primary": {},
                    "secondary": {},
                    "neutral": {},
                    "gradients": {},
                    "shadows": {},
                    "ui": {}
                }
            }
            print(f"✓ Profilo vuoto '{name}' creato")
        
        profiles[name] = new_profile
        self.data['profiles'] = profiles
        return True
    
    def set_active(self, profile_name: str):
        """Imposta il profilo attivo"""
        profiles = self.data.get('profiles', {})
        
        if profile_name not in profiles:
            print(f"✗ Profilo '{profile_name}' non trovato")
            return False
        
        self.data['active'] = profile_name
        print(f"✓ Profilo attivo: {profile_name}")
        return True
    
    def save(self, output_file: str = None):
        """Salva il file JSON"""
        output_path = Path(output_file) if output_file else self.file_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"✓ File salvato: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Errore salvataggio: {e}")
            return False


def main():
    """CLI principale"""
    if len(sys.argv) < 2:
        print("Uso: python color-tools.py <colors.json> [comando] [opzioni]")
        print("\nComandi disponibili:")
        print("  validate              - Valida il file JSON")
        print("  list                  - Elenca i profili")
        print("  export-css <profile>  - Esporta come CSS variables")
        print("  export-scss <profile> - Esporta come SCSS variables")
        print("  create <name> [base]  - Crea nuovo profilo")
        print("  activate <profile>    - Imposta profilo attivo")
        return
    
    file_path = sys.argv[1]
    validator = ColorValidator(file_path)
    
    if not validator.load():
        return
    
    if len(sys.argv) < 3:
        # Default: valida e lista
        validator.validate()
        validator.list_profiles()
        return
    
    command = sys.argv[2]
    
    if command == 'validate':
        validator.validate()
    
    elif command == 'list':
        if validator.validate():
            validator.list_profiles()
    
    elif command == 'export-css' and len(sys.argv) >= 4:
        profile = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) >= 5 else f"{profile}-variables.css"
        if validator.validate():
            validator.export_css_variables(profile, output)
    
    elif command == 'export-scss' and len(sys.argv) >= 4:
        profile = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) >= 5 else f"{profile}-variables.scss"
        if validator.validate():
            validator.convert_to_scss(profile, output)
    
    elif command == 'create' and len(sys.argv) >= 4:
        name = sys.argv[3]
        base = sys.argv[4] if len(sys.argv) >= 5 else None
        if validator.validate():
            if validator.create_profile(name, base):
                validator.save()
    
    elif command == 'activate' and len(sys.argv) >= 4:
        profile = sys.argv[3]
        if validator.validate():
            if validator.set_active(profile):
                validator.save()
    
    else:
        print(f"✗ Comando non riconosciuto: {command}")


if __name__ == '__main__':
    main()
