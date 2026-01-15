"""
Management command per popolare il sito con contenuti d'esempio.
Crea tutte le pagine necessarie per il Moto Club Castellazzo Bormida.
"""
import os
from datetime import date, datetime, timedelta, timezone as dt_tz
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image
from wagtail.images.models import Image as WagtailImage
from wagtail.models import Locale, Page, Site

from apps.website.models import (
    AboutPage,
    BoardPage,
    ContactPage,
    EventDetailPage,
    EventsArchivePage,
    EventsPage,
    HomePage,
    TimelinePage,
    TransparencyPage,
)


class Command(BaseCommand):
    help = "Popola il database con contenuti d'esempio per MC Castellazzo Bormida"

    def create_placeholder_image(self, name, width=800, height=600, color=(212, 175, 55)):
        """Crea un'immagine placeholder."""
        img = Image.new("RGB", (width, height), color)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        wagtail_image = WagtailImage(
            title=name,
            file=ImageFile(buffer, name=f"{name.lower().replace(' ', '_')}.png"),
        )
        wagtail_image.save()
        return wagtail_image

    def handle(self, *args, **options):
        self.stdout.write("🏍️ Creazione contenuti d'esempio per MC Castellazzo Bormida...")
        
        # Assicura che esista la lingua italiana
        locale, _ = Locale.objects.get_or_create(language_code="it")
        
        # Ottieni la root page (Site Root)
        from wagtail.models import Site
        
        root_page = Page.objects.filter(depth=1).first()
        if not root_page:
            self.stdout.write(self.style.ERROR("Root page non trovata!"))
            return
        
        # Rimuovi le pagine di default se esistono (eccetto HomePage)
        Page.objects.filter(depth=2).exclude(
            pk__in=HomePage.objects.values_list("pk", flat=True)
        ).delete()
        
        # Verifica se HomePage esiste già
        if HomePage.objects.exists():
            self.stdout.write(self.style.WARNING("HomePage già esistente, salto creazione..."))
            home = HomePage.objects.first()
        else:
            # Crea immagini placeholder
            self.stdout.write("📸 Creazione immagini placeholder...")
            logo_image = self.create_placeholder_image("Logo MC Castellazzo", 400, 400, (212, 175, 55))
            hero_image = self.create_placeholder_image("Hero Motoclub", 1920, 800, (27, 38, 59))
            
            # === HOMEPAGE ===
            self.stdout.write("🏠 Creazione HomePage...")
            home = HomePage(
                title="Home",
                slug="home",
                locale=locale,
                organization_name="Moto Club Castellazzo Bormida",
                description="""<p>Il <strong>Moto Club Castellazzo Bormida</strong>, fondato nel 1933, è uno dei più antichi motoclub italiani ancora in attività. Da oltre 90 anni promuoviamo la passione per le due ruote nel cuore del Monferrato.</p>
                <p>Organizziamo raduni, gare di regolarità, escursioni turistiche e eventi culturali legati al mondo delle moto. La nostra sede si trova nel centro storico di Castellazzo Bormida, in provincia di Alessandria.</p>""",
                street_address="Via Roma, 45",
                city="Castellazzo Bormida",
                region="Piemonte",
                country="IT",
                postal_code="15073",
                telephone="+39 0131 123456",
                email="info@mccastellazzobormida.it",
                founding_date=date(1933, 1, 1),
                hero_title="Moto Club Castellazzo Bormida",
                hero_subtitle="Dal 1933 - La passione per le due ruote nel cuore del Monferrato",
                logo=logo_image,
                hero_image=hero_image,
            )
            root_page.add_child(instance=home)
            home.save_revision().publish()
            
            # Aggiorna il Site
            site = Site.objects.first()
            if site:
                site.root_page = home
                site.site_name = "MC Castellazzo Bormida"
                site.save()
        
        # === TIMELINE PAGE ===
        if not TimelinePage.objects.exists():
            self.stdout.write("📜 Creazione Timeline...")
            timeline_image1 = self.create_placeholder_image("Raduno 2025", 800, 600, (155, 29, 100))
            timeline_image2 = self.create_placeholder_image("Gara Regolarità", 800, 600, (27, 38, 59))
            timeline_image3 = self.create_placeholder_image("Festa sociale", 800, 600, (212, 175, 55))
            
            timeline = TimelinePage(
                title="Novità",
                slug="novita",
                locale=locale,
                intro="<p>Le ultime notizie e attività del Moto Club Castellazzo Bormida</p>",
                articles=[
                    {
                        "type": "article",
                        "value": {
                            "headline": "Grande successo per il 91° Raduno Nazionale",
                            "image": timeline_image1.pk,
                            "date_published": date.today() - timedelta(days=5),
                            "article_section": "Raduni",
                            "summary": "<p>Oltre 500 motociclisti hanno partecipato alla 91ª edizione del nostro storico raduno nazionale. Un weekend all'insegna della passione, dell'amicizia e delle due ruote.</p>",
                            "url": "",
                        },
                    },
                    {
                        "type": "article",
                        "value": {
                            "headline": "Campionato Regionale Regolarità: il nostro team sul podio",
                            "image": timeline_image2.pk,
                            "date_published": date.today() - timedelta(days=15),
                            "article_section": "Competizioni",
                            "summary": "<p>Marco Rossi e Luca Bianchi conquistano il secondo posto nella classifica a squadre del Campionato Regionale di Regolarità Piemonte-Valle d'Aosta.</p>",
                            "url": "",
                        },
                    },
                    {
                        "type": "article",
                        "value": {
                            "headline": "Festa sociale: celebrati i 50 anni di iscrizione",
                            "image": timeline_image3.pk,
                            "date_published": date.today() - timedelta(days=30),
                            "article_section": "Vita del Club",
                            "summary": "<p>Durante la tradizionale festa sociale abbiamo premiato i soci che hanno raggiunto i 50 anni di iscrizione continuativa al Club. Un traguardo che testimonia l'attaccamento alla nostra famiglia motociclistica.</p>",
                            "url": "",
                        },
                    },
                    {
                        "type": "article",
                        "value": {
                            "headline": "Nuovo percorso turistico: alla scoperta del Monferrato",
                            "image": None,
                            "date_published": date.today() - timedelta(days=45),
                            "article_section": "Turismo",
                            "summary": "<p>Inaugurato il nuovo itinerario turistico che tocca le più belle cantine e i castelli del Monferrato. 120 km tra colline patrimonio UNESCO.</p>",
                            "url": "",
                        },
                    },
                ],
            )
            home.add_child(instance=timeline)
            timeline.save_revision().publish()
        
        # === CHI SIAMO ===
        if not AboutPage.objects.exists():
            self.stdout.write("ℹ️ Creazione Chi Siamo...")
            about_image = self.create_placeholder_image("Storia Club", 800, 600, (27, 38, 59))
            
            about = AboutPage(
                title="Chi Siamo",
                slug="chi-siamo",
                locale=locale,
                intro="<p>Scopri la storia e i valori del Moto Club Castellazzo Bormida</p>",
                body="""<h2>La nostra storia</h2>
                <p>Il Moto Club Castellazzo Bormida nasce nel <strong>1933</strong> per volontà di un gruppo di appassionati motociclisti locali. In quasi un secolo di attività, il Club ha attraversato guerre, boom economici e crisi, mantenendo sempre viva la fiamma della passione per le due ruote.</p>
                
                <h3>I primi anni (1933-1945)</h3>
                <p>Fondato in un'epoca in cui la motocicletta era ancora un lusso per pochi, il Club si distinse subito per l'organizzazione di gare di regolarità sulle strade sterrate del Monferrato.</p>
                
                <h3>Il dopoguerra e la crescita (1946-1970)</h3>
                <p>Con il boom economico, il numero dei soci crebbe esponenzialmente. Furono anni di grandi raduni e di affermazioni sportive a livello nazionale.</p>
                
                <h3>Gli anni della maturità (1970-2000)</h3>
                <p>Il Club si strutturò definitivamente, acquisendo la sede attuale e consolidando la tradizione del Raduno Nazionale che ancora oggi attira motociclisti da tutta Italia.</p>
                
                <h3>Il nuovo millennio</h3>
                <p>Oggi il Moto Club Castellazzo Bormida conta oltre 200 soci attivi e continua a promuovere eventi, escursioni e attività per tutti gli appassionati delle due ruote, mantenendo vivi i valori di amicizia, rispetto e passione che da sempre ci contraddistinguono.</p>
                
                <h2>I nostri valori</h2>
                <ul>
                    <li><strong>Passione</strong> - L'amore per le moto è il motore di tutto ciò che facciamo</li>
                    <li><strong>Amicizia</strong> - Il Club è prima di tutto una grande famiglia</li>
                    <li><strong>Rispetto</strong> - Per la strada, per l'ambiente, per gli altri</li>
                    <li><strong>Tradizione</strong> - Custodiamo 90 anni di storia motociclistica</li>
                </ul>""",
                image=about_image,
            )
            home.add_child(instance=about)
            about.save_revision().publish()
            
            # === CONSIGLIO DIRETTIVO ===
            self.stdout.write("👥 Creazione Consiglio Direttivo...")
            member_images = [
                self.create_placeholder_image(f"Membro {i}", 300, 300, (155, 29, 100))
                for i in range(1, 8)
            ]
            
            board = BoardPage(
                title="Consiglio Direttivo",
                slug="consiglio-direttivo",
                locale=locale,
                intro="<p>Il Consiglio Direttivo del Moto Club Castellazzo Bormida per il triennio 2024-2027</p>",
                members=[
                    {"type": "member", "value": {
                        "name": "Giovanni Ferraris",
                        "role": "Presidente",
                        "image": member_images[0].pk,
                        "bio": "<p>Socio dal 1985, appassionato di moto d'epoca. Ha guidato il Club attraverso importanti traguardi negli ultimi 10 anni.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Maria Castellani",
                        "role": "Vice Presidente",
                        "image": member_images[1].pk,
                        "bio": "<p>Prima donna nel direttivo del Club, porta energia e nuove idee all'organizzazione degli eventi.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Paolo Rossi",
                        "role": "Segretario",
                        "image": member_images[2].pk,
                        "bio": "<p>Gestisce le comunicazioni con i soci e la FMI. Meticoloso e sempre disponibile.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Andrea Bianchi",
                        "role": "Tesoriere",
                        "image": member_images[3].pk,
                        "bio": "<p>Commercialista di professione, garantisce una gestione trasparente delle finanze del Club.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Marco Dellavalle",
                        "role": "Responsabile Sportivo",
                        "image": member_images[4].pk,
                        "bio": "<p>Ex pilota di enduro, coordina le attività sportive e le gare di regolarità.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Laura Monti",
                        "role": "Responsabile Eventi",
                        "image": member_images[5].pk,
                        "bio": "<p>Organizza raduni, gite sociali e la festa del Club. Creatività e precisione sono le sue doti.</p>",
                    }},
                    {"type": "member", "value": {
                        "name": "Roberto Gallo",
                        "role": "Consigliere",
                        "image": member_images[6].pk,
                        "bio": "<p>Socio storico, memoria vivente del Club e custode delle tradizioni.</p>",
                    }},
                ],
            )
            about.add_child(instance=board)
            board.save_revision().publish()
            
            # === TRASPARENZA ===
            self.stdout.write("📋 Creazione Trasparenza...")
            transparency = TransparencyPage(
                title="Trasparenza",
                slug="trasparenza",
                locale=locale,
                intro="<p>In questa sezione pubblichiamo i documenti relativi alla gestione e all'amministrazione del Moto Club Castellazzo Bormida, nel rispetto dei principi di trasparenza e correttezza.</p>",
                documents=[
                    {"type": "document", "value": {
                        "title": "Statuto del Moto Club (aggiornato 2023)",
                        "document": None,
                        "description": "Lo Statuto vigente approvato dall'Assemblea dei Soci",
                    }},
                    {"type": "document", "value": {
                        "title": "Bilancio Consuntivo 2024",
                        "document": None,
                        "description": "Rendiconto economico-finanziario dell'esercizio 2024",
                    }},
                    {"type": "document", "value": {
                        "title": "Bilancio Preventivo 2025",
                        "document": None,
                        "description": "Budget previsto per le attività dell'anno 2025",
                    }},
                    {"type": "document", "value": {
                        "title": "Verbale Assemblea Soci 2024",
                        "document": None,
                        "description": "Verbale dell'assemblea ordinaria dei soci del 15 marzo 2024",
                    }},
                ],
            )
            about.add_child(instance=transparency)
            transparency.save_revision().publish()
            
            # === CONTATTI ===
            self.stdout.write("📞 Creazione Contatti...")
            contact = ContactPage(
                title="Contatti",
                slug="contatti",
                locale=locale,
                intro="""<p>Vuoi contattarci o venirci a trovare? Ecco tutte le informazioni utili.</p>
                <h2>Sede del Club</h2>
                <p>La nostra sede si trova nel centro storico di Castellazzo Bormida, facilmente raggiungibile dall'uscita autostradale di Alessandria Est.</p>
                
                <h3>Orari di apertura</h3>
                <ul>
                    <li><strong>Mercoledì</strong>: 21:00 - 23:00 (serata sociale)</li>
                    <li><strong>Sabato</strong>: 15:00 - 18:00</li>
                    <li><strong>Domenica</strong>: 10:00 - 12:00 (solo su appuntamento)</li>
                </ul>
                
                <h3>Come raggiungerci</h3>
                <p>Dalla A26: uscita Alessandria Est, proseguire per SS30 direzione Castellazzo Bormida. La sede è in centro paese, con parcheggio nelle vicinanze.</p>""",
                address="Via Roma, 45 - 15073 Castellazzo Bormida (AL)",
                latitude=44.8456,
                longitude=8.5734,
                phone="+39 0131 123456",
                email="info@mccastellazzobormida.it",
                show_contact_form=True,
            )
            about.add_child(instance=contact)
            contact.save_revision().publish()
        
        # === EVENTI ===
        if not EventsPage.objects.exists():
            self.stdout.write("📅 Creazione pagina Eventi...")
            events = EventsPage(
                title="Eventi",
                slug="eventi",
                locale=locale,
                intro="<p>Tutti gli eventi organizzati dal Moto Club Castellazzo Bormida per l'anno in corso</p>",
            )
            home.add_child(instance=events)
            events.save_revision().publish()
            
            # Eventi d'esempio
            event_images = [
                self.create_placeholder_image(f"Evento {i}", 800, 600, (212, 175, 55))
                for i in range(1, 6)
            ]
            
            now = timezone.now()
            current_year = now.year
            
            eventi_data = [
                {
                    "title": "92° Raduno Nazionale",
                    "event_name": "92° Raduno Nazionale Moto Club Castellazzo Bormida",
                    "start_date": datetime(current_year, 6, 15, 9, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(current_year, 6, 16, 18, 0, tzinfo=dt_tz.utc),
                    "location_name": "Piazza Vittorio Emanuele II",
                    "location_address": "Piazza Vittorio Emanuele II, Castellazzo Bormida (AL)",
                    "location_lat": 44.8456,
                    "location_lon": 8.5734,
                    "description": """<p>La storica manifestazione che dal 1933 richiama motociclisti da tutta Italia!</p>
                    <h3>Programma</h3>
                    <p><strong>Sabato 15 giugno:</strong></p>
                    <ul>
                        <li>09:00 - Apertura iscrizioni e accoglienza</li>
                        <li>10:00 - Partenza giro turistico nel Monferrato</li>
                        <li>13:00 - Pranzo sociale presso Agriturismo "Le Colline"</li>
                        <li>16:00 - Esposizione moto d'epoca</li>
                        <li>20:00 - Cena di gala con premiazioni</li>
                    </ul>
                    <p><strong>Domenica 16 giugno:</strong></p>
                    <ul>
                        <li>08:00 - Colazione in sede</li>
                        <li>10:00 - Prova di regolarità "Memorial Mario Rossi"</li>
                        <li>13:00 - Premiazioni e saluti</li>
                    </ul>""",
                    "event_status": "EventScheduled",
                    "image": event_images[0],
                },
                {
                    "title": "Motoraduno di Primavera",
                    "event_name": "Motoraduno di Primavera - Colline del Monferrato",
                    "start_date": datetime(current_year, 4, 20, 9, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(current_year, 4, 20, 18, 0, tzinfo=dt_tz.utc),
                    "location_name": "Sede MC Castellazzo",
                    "location_address": "Via Roma 45, Castellazzo Bormida",
                    "location_lat": 44.8456,
                    "location_lon": 8.5734,
                    "description": "<p>Escursione turistica di una giornata attraverso le colline del Monferrato. Pranzo presso trattoria tipica con menu a prezzo convenzionato.</p>",
                    "event_status": "EventScheduled",
                    "image": event_images[1],
                },
                {
                    "title": "Gita Sociale Liguria",
                    "event_name": "Gita Sociale - Mare e Moto in Liguria",
                    "start_date": datetime(current_year, 7, 13, 7, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(current_year, 7, 14, 20, 0, tzinfo=dt_tz.utc),
                    "location_name": "Finale Ligure",
                    "location_address": "Finale Ligure (SV)",
                    "location_lat": 44.1692,
                    "location_lon": 8.3433,
                    "description": "<p>Weekend di relax sulla Riviera Ligure. Partenza sabato mattina, pernottamento in hotel convenzionato, rientro domenica sera.</p>",
                    "event_status": "EventScheduled",
                    "image": event_images[2],
                },
                {
                    "title": "Prova Regolarità FMI",
                    "event_name": "6ª Prova Campionato Regionale Regolarità",
                    "start_date": datetime(current_year, 9, 21, 8, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(current_year, 9, 21, 17, 0, tzinfo=dt_tz.utc),
                    "location_name": "Zona industriale",
                    "location_address": "Via Industria, Castellazzo Bormida",
                    "location_lat": 44.8400,
                    "location_lon": 8.5800,
                    "description": "<p>Prova valida per il Campionato Regionale Piemonte-Valle d'Aosta. Percorso di 80 km con 6 prove speciali.</p>",
                    "event_status": "EventScheduled",
                    "image": event_images[3],
                },
                {
                    "title": "Festa Sociale 2026",
                    "event_name": "Festa Sociale e Assemblea dei Soci",
                    "start_date": datetime(current_year, 12, 7, 19, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(current_year, 12, 7, 24, 0, tzinfo=dt_tz.utc),
                    "location_name": "Ristorante La Pergola",
                    "location_address": "Via Asti 12, Castellazzo Bormida",
                    "location_lat": 44.8480,
                    "location_lon": 8.5700,
                    "description": "<p>Tradizionale cena sociale con premiazione dei soci e rinnovo tessere per l'anno nuovo. Seguirà l'Assemblea ordinaria dei Soci.</p>",
                    "event_status": "EventScheduled",
                    "image": event_images[4],
                },
            ]
            
            for i, evt_data in enumerate(eventi_data):
                img = evt_data.pop("image")
                evt = EventDetailPage(
                    slug=f"evento-{i+1}",
                    locale=locale,
                    image=img,
                    **evt_data,
                )
                events.add_child(instance=evt)
                evt.save_revision().publish()
        
        # === ARCHIVIO EVENTI ===
        if not EventsArchivePage.objects.exists():
            self.stdout.write("📚 Creazione Archivio Eventi...")
            archive = EventsArchivePage(
                title="Archivio Eventi",
                slug="archivio-eventi",
                locale=locale,
                intro="<p>Archivio storico degli eventi organizzati dal Moto Club Castellazzo Bormida</p>",
            )
            home.add_child(instance=archive)
            archive.save_revision().publish()
            
            # Eventi passati d'esempio
            past_events = [
                {
                    "title": "91° Raduno Nazionale 2025",
                    "event_name": "91° Raduno Nazionale Moto Club Castellazzo Bormida",
                    "start_date": datetime(2025, 6, 14, 9, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(2025, 6, 15, 18, 0, tzinfo=dt_tz.utc),
                    "location_name": "Piazza Vittorio Emanuele II",
                    "location_address": "Castellazzo Bormida",
                    "description": "<p>Edizione da record con oltre 500 partecipanti da tutta Italia!</p>",
                    "event_status": "EventScheduled",
                },
                {
                    "title": "Gita Val d'Aosta 2025",
                    "event_name": "Escursione Sociale Val d'Aosta",
                    "start_date": datetime(2025, 8, 10, 7, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(2025, 8, 12, 20, 0, tzinfo=dt_tz.utc),
                    "location_name": "Aosta",
                    "location_address": "Aosta (AO)",
                    "description": "<p>Tre giorni tra le montagne valdostane. Valico del Gran San Bernardo e Piccolo San Bernardo.</p>",
                    "event_status": "EventScheduled",
                },
                {
                    "title": "Raduno 2024",
                    "event_name": "90° Raduno Nazionale - Edizione del Novantennale",
                    "start_date": datetime(2024, 6, 15, 9, 0, tzinfo=dt_tz.utc),
                    "end_date": datetime(2024, 6, 16, 18, 0, tzinfo=dt_tz.utc),
                    "location_name": "Piazza Vittorio Emanuele II",
                    "location_address": "Castellazzo Bormida",
                    "description": "<p>Edizione speciale per celebrare i 90 anni dalla fondazione del Club!</p>",
                    "event_status": "EventScheduled",
                },
            ]
            
            past_image = self.create_placeholder_image("Evento passato", 800, 600, (100, 100, 100))
            for i, evt_data in enumerate(past_events):
                evt = EventDetailPage(
                    slug=f"archivio-evento-{i+1}",
                    locale=locale,
                    image=past_image,
                    **evt_data,
                )
                archive.add_child(instance=evt)
                evt.save_revision().publish()
        
        self.stdout.write(self.style.SUCCESS("✅ Contenuti d'esempio creati con successo!"))
        self.stdout.write("")
        self.stdout.write("Pagine create:")
        self.stdout.write("  🏠 Home")
        self.stdout.write("  📜 Novità (Timeline)")
        self.stdout.write("  ℹ️ Chi Siamo")
        self.stdout.write("    👥 Consiglio Direttivo")
        self.stdout.write("    📋 Trasparenza")
        self.stdout.write("    📞 Contatti")
        self.stdout.write("  📅 Eventi (5 eventi)")
        self.stdout.write("  📚 Archivio Eventi (3 eventi)")
        self.stdout.write("")
        self.stdout.write("Accedi all'admin: http://localhost:8000/admin/")
        self.stdout.write("Credenziali: admin / admin123")
