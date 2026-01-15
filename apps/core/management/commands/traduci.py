"""
MC Castellazzo - Comando Unificato per Traduzioni
==================================================
Un unico comando per:
1. Estrarre stringhe (inclusi .jinja2)
2. Tradurre automaticamente
3. Compilare i file .mo

Compatibile con Django, Wagtail e CodeRedCMS.

Uso:
    python manage.py traduci              # Tutte le lingue
    python manage.py traduci --lang es    # Solo spagnolo
    python manage.py traduci --dry-run    # Solo mostra cosa farebbe
    python manage.py traduci --skip-extract  # Salta estrazione, solo traduzione
"""
import time
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = "Comando unificato: estrae, traduce e compila le stringhe per l'i18n"
    
    # Cartelle da ignorare durante l'estrazione
    IGNORE_DIRS = [
        'staticfiles',
        'media', 
        'vecchio',
        'motoclub-static',
        'node_modules',
        '.venv',
        'venv',
    ]
    
    # Estensioni da scansionare (include .jinja2!)
    EXTENSIONS = ['html', 'txt', 'py', 'jinja2']
    
    # Lingue target
    LANGUAGES = ['en', 'de', 'fr', 'es']
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--lang',
            type=str,
            help='Lingua specifica (en, de, fr, es). Se omesso, tutte.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra cosa verrebbe fatto senza applicare.',
        )
        parser.add_argument(
            '--skip-extract',
            action='store_true', 
            help='Salta estrazione, esegui solo traduzione e compilazione.',
        )
        parser.add_argument(
            '--skip-translate',
            action='store_true',
            help='Salta traduzione automatica.',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Output dettagliato.',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        skip_extract = options.get('skip_extract', False)
        skip_translate = options.get('skip_translate', False)
        verbose = options.get('verbose', False)
        target_lang = options.get('lang')
        
        languages = [target_lang] if target_lang else self.LANGUAGES
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🌍 MC CASTELLAZZO - TRADUZIONE AUTOMATICA"))
        self.stdout.write("=" * 60 + "\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  Modalità DRY-RUN: nessuna modifica verrà applicata\n"))
        
        # Step 1: Estrazione stringhe
        if not skip_extract:
            self.step_extract(languages, dry_run, verbose)
        else:
            self.stdout.write(self.style.WARNING("⏭️  Estrazione saltata (--skip-extract)\n"))
        
        # Step 2: Traduzione automatica
        if not skip_translate:
            self.step_translate(languages, dry_run, verbose)
        else:
            self.stdout.write(self.style.WARNING("⏭️  Traduzione saltata (--skip-translate)\n"))
        
        # Step 3: Compilazione
        if not dry_run:
            self.step_compile(verbose)
        else:
            self.stdout.write(self.style.WARNING("⏭️  Compilazione saltata (dry-run)\n"))
        
        # Riepilogo
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ COMPLETATO!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nLingue processate: {', '.join(languages)}")
        self.stdout.write("Riavvia il server per vedere le modifiche.\n")
    
    def step_extract(self, languages, dry_run, verbose):
        """Step 1: Estrae le stringhe dai sorgenti."""
        self.stdout.write(self.style.HTTP_INFO("\n📝 STEP 1: Estrazione stringhe\n"))
        
        if dry_run:
            self.stdout.write(f"  Estensioni: {', '.join(self.EXTENSIONS)}")
            self.stdout.write(f"  Cartelle ignorate: {', '.join(self.IGNORE_DIRS)}")
            self.stdout.write(f"  Lingue: {', '.join(languages)}")
            return
        
        try:
            # Chiama makemessages con le estensioni corrette
            call_command(
                'makemessages',
                all=True,
                extension=self.EXTENSIONS,
                ignore=self.IGNORE_DIRS,
                verbosity=2 if verbose else 1,
            )
            self.stdout.write(self.style.SUCCESS("  ✓ Stringhe estratte con successo"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Errore estrazione: {e}"))
    
    def step_translate(self, languages, dry_run, verbose):
        """Step 2: Traduce automaticamente le stringhe."""
        self.stdout.write(self.style.HTTP_INFO("\n🔄 STEP 2: Traduzione automatica\n"))
        
        try:
            from apps.core.machine_translator import DeepTranslatorMachineTranslator
            translator = DeepTranslatorMachineTranslator()
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Errore import translator: {e}"))
            return
        
        locale_dir = Path(settings.BASE_DIR) / 'locale'
        
        for lang in languages:
            po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
            
            if not po_file.exists():
                self.stdout.write(self.style.WARNING(f"  ⚠️  File non trovato: {po_file}"))
                continue
            
            self.stdout.write(f"\n  📄 Traduzione {lang.upper()}:")
            
            translated = self._translate_po_file(po_file, lang, translator, dry_run, verbose)
            
            if translated > 0:
                self.stdout.write(self.style.SUCCESS(f"     ✓ {translated} nuove traduzioni"))
            else:
                self.stdout.write(f"     - Nessuna nuova stringa da tradurre")
    
    def _translate_po_file(self, po_file, target_lang, translator, dry_run, verbose):
        """Traduce un singolo file .po."""
        import re
        
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Usa polib per parsing corretto dei file .po
        try:
            import polib
        except ImportError:
            self.stdout.write(self.style.ERROR("  ✗ polib non installato. Installa con: pip install polib"))
            return 0
        
        po = polib.pofile(str(po_file))
        translated_count = 0
        
        for entry in po:
            # Salta entries senza msgid o con msgstr già popolato
            if not entry.msgid or entry.msgstr:
                continue
            
            # Salta header (msgid vuoto)
            if entry.msgid == '':
                continue
            
            # Salta stringhe troppo corte o solo simboli
            if len(entry.msgid) < 2 or entry.msgid.strip() in ['', '-', '.', ',']:
                continue
            
            try:
                # Traduce (source=italiano, target=lingua destinazione)
                translated = translator._translate_text(entry.msgid, 'it', target_lang)
                
                if translated:
                    # Salva sempre la traduzione, anche se uguale all'originale
                    # (molte parole sono uguali tra lingue: Foto, Documento, etc.)
                    if verbose or dry_run:
                        # Tronca per display
                        src_display = entry.msgid[:50] + "..." if len(entry.msgid) > 50 else entry.msgid
                        tgt_display = translated[:50] + "..." if len(translated) > 50 else translated
                        same_note = " (stesso)" if translated == entry.msgid else ""
                        self.stdout.write(f"     {src_display} → {tgt_display}{same_note}")
                    
                    if not dry_run:
                        entry.msgstr = translated
                    
                    translated_count += 1
                    
                    # Rate limiting
                    time.sleep(0.3)
                    
            except Exception as e:
                if verbose:
                    self.stdout.write(self.style.WARNING(f"     ⚠️  Errore: {entry.msgid[:30]}... - {e}"))
        
        # Salva
        if not dry_run and translated_count > 0:
            po.save(str(po_file))
        
        return translated_count
    
    def step_compile(self, verbose):
        """Step 3: Compila i file .mo."""
        self.stdout.write(self.style.HTTP_INFO("\n⚙️  STEP 3: Compilazione .mo\n"))
        
        try:
            call_command('compilemessages', verbosity=2 if verbose else 1)
            self.stdout.write(self.style.SUCCESS("  ✓ File .mo compilati"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Errore compilazione: {e}"))
