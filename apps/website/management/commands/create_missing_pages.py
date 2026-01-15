"""
Management command per creare le pagine mancanti dal contenuto di motoclub-static.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
from pathlib import Path
from wagtail.models import Locale, Page
from apps.website.models import (
    HomePage, 
    BoardPage, 
    GalleryPage, 
    ContactPage,
    AboutPage,
    PrivacyPage
)
import json


class Command(BaseCommand):
    help = 'Crea le pagine mancanti importando contenuti da motoclub-static'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Esegui senza salvare nel database',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('\n📦 Creazione pagine mancanti...\n')
        
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

        # Get locale italiano
        locale_it = Locale.objects.get(language_code='it')
        
        # Get homepage come parent
        homepage = HomePage.objects.filter(locale=locale_it).first()
        
        if not homepage:
            self.stdout.write(self.style.ERROR('❌ Homepage non trovata'))
            return

        # Crea le pagine
        self._create_consiglio_page(static_dir, homepage, locale_it, dry_run)
        self._create_galleria_page(static_dir, homepage, locale_it, dry_run)
        self._create_contatti_page(static_dir, homepage, locale_it, dry_run)
        self._create_privacy_page(static_dir, homepage, locale_it, dry_run)
        
        self.stdout.write(self.style.SUCCESS('\n✨ Creazione completata!\n'))

    def _create_consiglio_page(self, static_dir, homepage, locale, dry_run):
        """Crea la pagina Il Consiglio."""
        self.stdout.write('👤 Il Consiglio...')
        
        # Controlla se esiste già
        chi_siamo = Page.objects.filter(slug='chi-siamo', locale=locale).first()
        if not chi_siamo:
            self.stdout.write(self.style.WARNING('   ⚠️  Pagina Chi Siamo non trovata, uso homepage come parent'))
            chi_siamo = homepage
            
        existing = Page.objects.filter(slug='consiglio', locale=locale).first()
        if existing:
            self.stdout.write('   ℹ️  Pagina già esistente')
            return

        # Leggi HTML
        consiglio_file = static_dir / 'consiglio.html'
        if not consiglio_file.exists():
            self.stdout.write(self.style.WARNING('   ⚠️  File consiglio.html non trovato'))
            return

        with open(consiglio_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Estrai contenuto
        title = "Il Consiglio Direttivo"
        
        # Cerca la descrizione nella meta
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        intro = meta_desc['content'] if meta_desc else "<p>Conosci i membri che guidano il club con passione e dedizione.</p>"

        if not dry_run:
            page = BoardPage(
                title=title,
                slug='consiglio',
                locale=locale,
                show_in_menus=True,
                intro=intro,
            )
            chi_siamo.add_child(instance=page)
            page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Creata: /chi-siamo/consiglio/ (ID: {page.id})'))
        else:
            self.stdout.write('   📝 Sarebbe stata creata: /chi-siamo/consiglio/')

    def _create_galleria_page(self, static_dir, homepage, locale, dry_run):
        """Crea la pagina Galleria."""
        self.stdout.write('📷 Galleria...')
        
        existing = Page.objects.filter(slug='galleria', locale=locale).first()
        if existing:
            self.stdout.write('   ℹ️  Pagina già esistente')
            return

        # Leggi HTML
        galleria_file = static_dir / 'galleria.html'
        if not galleria_file.exists():
            self.stdout.write(self.style.WARNING('   ⚠️  File galleria.html non trovato'))
            return

        with open(galleria_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Estrai contenuto
        title = "Galleria Fotografica"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        intro = meta_desc['content'] if meta_desc else "<p>Le nostre avventure su due ruote immortalate in immagini.</p>"

        if not dry_run:
            page = GalleryPage(
                title=title,
                slug='galleria',
                locale=locale,
                show_in_menus=True,
                intro=intro,
            )
            homepage.add_child(instance=page)
            page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Creata: /galleria/ (ID: {page.id})'))
        else:
            self.stdout.write('   📝 Sarebbe stata creata: /galleria/')

    def _create_contatti_page(self, static_dir, homepage, locale, dry_run):
        """Crea la pagina Contatti."""
        self.stdout.write('📧 Contatti...')
        
        # Controlla se esiste già
        chi_siamo = Page.objects.filter(slug='chi-siamo', locale=locale).first()
        if not chi_siamo:
            self.stdout.write(self.style.WARNING('   ⚠️  Pagina Chi Siamo non trovata, uso homepage come parent'))
            chi_siamo = homepage
            
        existing = Page.objects.filter(slug='contatti', locale=locale).first()
        if existing:
            self.stdout.write('   ℹ️  Pagina già esistente')
            return

        # Leggi HTML
        contatti_file = static_dir / 'contatti.html'
        if not contatti_file.exists():
            self.stdout.write(self.style.WARNING('   ⚠️  File contatti.html non trovato'))
            return

        with open(contatti_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Estrai contenuto
        title = "Contatti"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        intro = meta_desc['content'] if meta_desc else "<p>Entra in contatto con il Moto Club Castellazzo Bormida.</p>"

        if not dry_run:
            page = ContactPage(
                title=title,
                slug='contatti',
                locale=locale,
                show_in_menus=True,
                intro=intro,
                email='info@mccastellazzo.it',
                phone='+39 0123 456789',
                address='Castellazzo Bormida, Piemonte, Italia',
            )
            chi_siamo.add_child(instance=page)
            page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Creata: /contatti/ (ID: {page.id})'))
        else:
            self.stdout.write('   📝 Sarebbe stata creata: /contatti/')

    def _create_privacy_page(self, static_dir, homepage, locale, dry_run):
        """Crea la pagina Privacy."""
        self.stdout.write('🔒 Privacy Policy...')
        
        existing = Page.objects.filter(slug='privacy', locale=locale).first()
        if existing:
            self.stdout.write('   ℹ️  Pagina già esistente')
            return

        title = "Privacy Policy"
        intro = "<p>Informativa sulla privacy e trattamento dei dati personali secondo GDPR.</p>"
        body = """
        <h2>Informativa Privacy</h2>
        <p>Il Moto Club Castellazzo Bormida tratta i dati personali nel rispetto del Regolamento UE 2016/679 (GDPR).</p>
        
        <h3>Titolare del trattamento</h3>
        <p>Moto Club Castellazzo Bormida<br>
        Email: info@mccastellazzo.it</p>
        
        <h3>Finalità del trattamento</h3>
        <p>I dati personali sono raccolti per:</p>
        <ul>
            <li>Gestione iscrizioni e tesseramenti</li>
            <li>Organizzazione eventi</li>
            <li>Comunicazioni istituzionali</li>
        </ul>
        
        <h3>Diritti dell'interessato</h3>
        <p>L'interessato può esercitare i diritti di accesso, rettifica, cancellazione, limitazione, portabilità e opposizione contattando: info@mccastellazzo.it</p>
        """

        if not dry_run:
            page = PrivacyPage(
                title=title,
                slug='privacy',
                locale=locale,
                show_in_menus=False,  # Non in menu principale
                intro=intro,
                body=body,
            )
            homepage.add_child(instance=page)
            page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Creata: /privacy/ (ID: {page.id})'))
        else:
            self.stdout.write('   📝 Sarebbe stata creata: /privacy/')
