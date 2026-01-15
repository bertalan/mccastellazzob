"""
MC Castellazzo - Import Static Content Script
=============================================
Script per trasferire contenuti dal sito statico a Wagtail.
"""
from django.core.management.base import BaseCommand
from apps.website.models import HomePage
from wagtail.models import Locale
from bs4 import BeautifulSoup
from pathlib import Path
import json


class Command(BaseCommand):
    help = 'Importa contenuti dal sito statico motoclub-static/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula importazione senza salvare'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('\n📦 Importazione contenuti sito statico...\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  Modalità DRY-RUN attiva\n'))

        # Path al sito statico
        static_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / 'motoclub-static'
        
        if not static_dir.exists():
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Directory non trovata: {static_dir}'
                )
            )
            return

        self.stdout.write(f'📁 Directory statica: {static_dir}\n')

        # Importa contenuti
        self._import_homepage_content(static_dir, dry_run)
        
        self.stdout.write(self.style.SUCCESS('\n✨ Importazione completata!\n'))

    def _import_homepage_content(self, static_dir, dry_run):
        """Importa contenuti della homepage."""
        self.stdout.write('🏠 Homepage...')
        
        # Leggi index.html
        index_file = static_dir / 'index.html'
        if not index_file.exists():
            self.stdout.write(self.style.WARNING('   ⚠️  index.html non trovato'))
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Estrai contenuti
        hero_title = None
        hero_subtitle = None
        
        # Cerca hero section (è un header, non section)
        hero = soup.find('header', id='hero')
        if hero:
            h1 = hero.find('h1')
            if h1:
                # Prendi tutto il testo, incluso "Castellazzo Bormida" in gold
                hero_title = ' '.join(h1.get_text(separator=' ', strip=True).split())
            
            # Cerca il paragrafo con la descrizione
            p = hero.find('p', class_='text-xl')
            if p:
                hero_subtitle = ' '.join(p.get_text(separator=' ', strip=True).split())

        self.stdout.write(f'   📝 Titolo: {hero_title[:50] if hero_title else "N/A"}...')
        self.stdout.write(f'   📝 Sottotitolo: {hero_subtitle[:50] if hero_subtitle else "N/A"}...')

        if not dry_run:
            # Aggiorna homepage
            locale_it = Locale.objects.get(language_code='it')
            home = HomePage.objects.filter(locale=locale_it).first()
            
            if home:
                updated = False
                
                if hero_title and not home.hero_title:
                    home.hero_title = hero_title
                    updated = True
                
                if hero_subtitle and not home.hero_subtitle:
                    home.hero_subtitle = hero_subtitle
                    updated = True
                
                if updated:
                    home.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS('   ✅ Homepage aggiornata'))
                else:
                    self.stdout.write('   ℹ️  Nessun aggiornamento necessario')
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  HomePage non trovata'))
