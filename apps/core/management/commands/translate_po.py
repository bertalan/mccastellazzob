"""
MC Castellazzo - Comando per tradurre i file .po
=================================================
Traduce automaticamente le stringhe UI nei file .po
"""
import os
import re
import time
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Traduce automaticamente le stringhe UI nei file .po"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--lang',
            type=str,
            help='Lingua specifica da tradurre (en, de, fr, es). Se omesso, traduce tutte.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra cosa verrebbe tradotto senza salvare.',
        )
    
    def handle(self, *args, **options):
        from apps.core.machine_translator import DeepTranslatorMachineTranslator
        
        locale_dir = Path(settings.BASE_DIR) / 'locale'
        target_lang = options.get('lang')
        dry_run = options.get('dry_run', False)
        
        # Determina quali lingue tradurre
        if target_lang:
            languages = [target_lang]
        else:
            languages = ['en', 'de', 'fr', 'es']
        
        translator = DeepTranslatorMachineTranslator()
        
        for lang in languages:
            po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
            
            if not po_file.exists():
                self.stdout.write(self.style.WARNING(f"File non trovato: {po_file}"))
                continue
            
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(self.style.SUCCESS(f"Traduzione {lang.upper()}"))
            self.stdout.write(f"{'='*60}")
            
            translated_count = self.translate_po_file(po_file, lang, translator, dry_run)
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ {translated_count} stringhe tradotte per {lang}")
            )
    
    def translate_po_file(self, po_file, target_lang, translator, dry_run):
        """Traduce un file .po."""
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern per trovare msgid e msgstr
        pattern = r'(msgid\s+"([^"]+)")\s*(msgstr\s+"([^"]*)")'
        
        translated_count = 0
        
        def replace_translation(match):
            nonlocal translated_count
            
            full_match = match.group(0)
            msgid_line = match.group(1)
            msgid_text = match.group(2)
            msgstr_line = match.group(3)
            msgstr_text = match.group(4)
            
            # Salta se già tradotto o se è vuoto
            if msgstr_text.strip():
                return full_match
            
            if not msgid_text.strip():
                return full_match
            
            # Salta stringhe troppo corte o tecniche
            if len(msgid_text) < 3:
                return full_match
            
            # Traduci
            try:
                time.sleep(0.3)  # Rate limiting
                translated = translator._translate_text(msgid_text, 'it', target_lang)
                
                if translated and translated != msgid_text:
                    translated_count += 1
                    self.stdout.write(f"  {msgid_text[:50]}... → {translated[:50]}...")
                    
                    if dry_run:
                        return full_match
                    
                    return f'{msgid_line}\nmsgstr "{translated}"'
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Errore: {msgid_text[:30]}... - {e}"))
            
            return full_match
        
        # Sostituisci le traduzioni
        new_content = re.sub(pattern, replace_translation, content, flags=re.MULTILINE)
        
        # Salva il file
        if not dry_run and translated_count > 0:
            with open(po_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return translated_count
