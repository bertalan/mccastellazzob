"""
MC Castellazzo - About Pages Models
====================================
Pagine Chi Siamo con sottopagine:
- AboutPage (schema.org AboutPage)
- BoardPage (Consiglio Direttivo - schema.org Organization with members)
- TransparencyPage (Trasparenza - schema.org WebPage)
- ContactPage (Contatti - schema.org ContactPage)

I dati organizzazione vengono da wagtailseo.SeoSettings.
"""
import hashlib
import hmac
import random
import time
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _, gettext
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

logger = logging.getLogger(__name__)

from apps.core.seo import JsonLdMixin, clean_html, person, get_organization_data, get_seo_settings
from apps.core.maps import get_default_location
from apps.website.blocks import MemberBlock, DocumentBlock, MapBlock, StatsBlock, ValuesBlock, TimelineBlock, FAQItemBlock


class AboutPage(JsonLdMixin, Page):
    """
    Pagina Chi Siamo principale - schema.org AboutPage.
    """
    
    # Hero fields
    hero_title = models.CharField(
        _("Titolo Hero"),
        max_length=100,
        blank=True,
        help_text=_("Titolo principale nell'hero section"),
    )
    
    hero_subtitle = models.CharField(
        _("Sottotitolo Hero"),
        max_length=200,
        blank=True,
        help_text=_("Sottotitolo nell'hero section"),
    )
    
    # Statistics
    founding_year = models.PositiveIntegerField(
        _("Anno di fondazione"),
        default=1933,
    )
    
    members_count = models.PositiveIntegerField(
        _("Numero soci attivi"),
        default=250,
    )
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    body = RichTextField(
        _("Contenuto"),
        blank=True,
    )
    
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine"),
    )
    
    # Timeline storica
    timeline = StreamField(
        [
            ("timeline", TimelineBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Timeline Storica"),
    )
    
    # Milestones - statistiche del motoclub
    milestones = StreamField(
        [
            ("stats", StatsBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Traguardi / Statistiche"),
    )
    
    # Values - valori del motoclub  
    values = StreamField(
        [
            ("values", ValuesBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("I Nostri Valori"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/about_page.jinja2"
    subpage_types = ["website.BoardPage", "website.TransparencyPage", "website.ContactPage"]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
            ],
            heading=_("Hero Section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("founding_year"),
                FieldPanel("members_count"),
            ],
            heading=_("Statistiche"),
        ),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("timeline"),
        FieldPanel("milestones"),
        FieldPanel("values"),
    ]
    
    class Meta:
        verbose_name = _("Chi Siamo")
        verbose_name_plural = _("Chi Siamo")
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "AboutPage"
    
    def get_json_ld_data(self, request=None) -> dict:
        data = {
            "name": self.title,
            "url": self.full_url,
        }
        if self.intro:
            data["description"] = clean_html(self.intro)
        if self.image:
            data["image"] = self.image.get_rendition("original").url
        return data


class BoardPage(JsonLdMixin, Page):
    """
    Pagina Consiglio Direttivo - schema.org Organization con members.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    members = StreamField(
        [
            ("member", MemberBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Membri"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/board_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("members"),
    ]
    
    class Meta:
        verbose_name = _("Consiglio Direttivo")
        verbose_name_plural = _("Consiglio Direttivo")
    
    def get_members_list(self):
        """Ritorna la lista dei membri."""
        members_list = []
        for block in self.members:
            if block.block_type == "member":
                members_list.append(block.value)
        return members_list
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "Organization"
    
    def get_json_ld_data(self, request=None) -> dict:
        members = []
        for m in self.get_members_list():
            members.append(person(
                name=m.get("name", ""),
                job_title=m.get("role", ""),
                image_url=m.get("image").get_rendition("fill-300x300").url if m.get("image") else "",
            ))
        
        return {
            "name": self.title,
            "url": self.full_url,
            "member": members,
        }


class TransparencyPage(JsonLdMixin, Page):
    """
    Pagina Trasparenza - schema.org WebPage con documenti allegati.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    documents = StreamField(
        [
            ("document", DocumentBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Documenti"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/transparency_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("documents"),
    ]
    
    class Meta:
        verbose_name = _("Trasparenza")
        verbose_name_plural = _("Trasparenza")
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "WebPage"
    
    def get_json_ld_data(self, request=None) -> dict:
        return {
            "name": self.title,
            "url": self.full_url,
            "description": clean_html(self.intro) if self.intro else "",
        }


class ContactPage(JsonLdMixin, Page):
    """
    Pagina Contatti - schema.org ContactPage con form e mappa OpenStreetMap.
    """
    
    intro = RichTextField(
        _("Introduzione"),
        blank=True,
    )
    
    # Indirizzo per mappa
    address = models.CharField(
        _("Indirizzo"),
        max_length=500,
        blank=True,
        help_text=_("Indirizzo completo per la mappa"),
    )
    
    latitude = models.FloatField(
        _("Latitudine"),
        null=True,
        blank=True,
    )
    
    longitude = models.FloatField(
        _("Longitudine"),
        null=True,
        blank=True,
    )
    
    # Contatti
    phone = models.CharField(
        _("Telefono"),
        max_length=30,
        blank=True,
    )
    
    email = models.EmailField(
        _("Email"),
        blank=True,
    )
    
    # Form abilitato
    show_contact_form = models.BooleanField(
        _("Mostra form contatto"),
        default=True,
    )
    
    form_success_message = models.CharField(
        _("Messaggio successo form"),
        max_length=255,
        default=_("Grazie per averci contattato!"),
    )
    
    # Note contatti
    phone_note = models.CharField(
        _("Nota telefono"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Chiamaci il giovedì sera'"),
    )
    
    email_note = models.CharField(
        _("Nota email"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Rispondiamo entro 24h'"),
    )
    
    # Orari sede
    opening_hours = models.TextField(
        _("Orari apertura"),
        blank=True,
        help_text=_("Un orario per riga, formato: 'Giorno: HH:MM - HH:MM'"),
    )
    
    opening_hours_note = models.CharField(
        _("Nota orari"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Serata sociale settimanale'"),
    )
    
    # Indicazioni stradali
    map_description = models.CharField(
        _("Descrizione mappa"),
        max_length=255,
        blank=True,
        help_text=_("Testo sotto il titolo 'Dove Trovarci'"),
    )
    
    directions_car = models.CharField(
        _("Indicazioni auto"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Uscita A26 Alessandria Sud, 15 min'"),
    )
    
    directions_train = models.CharField(
        _("Indicazioni treno"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Stazione Alessandria + bus linea 5'"),
    )
    
    directions_parking = models.CharField(
        _("Indicazioni parcheggio"),
        max_length=150,
        blank=True,
        help_text=_("Es: 'Ampio parcheggio gratuito disponibile'"),
    )
    
    # FAQ
    faq = StreamField(
        [("item", FAQItemBlock())],
        blank=True,
        use_json_field=True,
        verbose_name=_("Domande Frequenti"),
        help_text=_("Aggiungi le FAQ. Lascia vuoto per nascondere la sezione."),
    )
    
    faq_title = models.CharField(
        _("Titolo sezione FAQ"),
        max_length=100,
        default=_("Domande Frequenti"),
        blank=True,
    )
    
    faq_subtitle = models.CharField(
        _("Sottotitolo FAQ"),
        max_length=255,
        default=_("Trova rapidamente le risposte alle domande più comuni"),
        blank=True,
    )
    
    # CTA
    cta_title = models.CharField(
        _("Titolo CTA"),
        max_length=100,
        blank=True,
        help_text=_("Es: 'Pronto a Unirti a Noi?'"),
    )
    
    cta_description = models.CharField(
        _("Descrizione CTA"),
        max_length=255,
        blank=True,
        help_text=_("Es: 'Dal 1933 accogliamo appassionati di moto...'"),
    )
    
    # === Wagtail Config ===
    template = "website/pages/contact_page.jinja2"
    parent_page_types = ["website.AboutPage"]
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
            ],
            heading=_("Posizione Mappa"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("phone_note"),
                FieldPanel("email"),
                FieldPanel("email_note"),
            ],
            heading=_("Informazioni Contatto"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("opening_hours"),
                FieldPanel("opening_hours_note"),
            ],
            heading=_("Orari Sede"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("map_description"),
                FieldPanel("directions_car"),
                FieldPanel("directions_train"),
                FieldPanel("directions_parking"),
            ],
            heading=_("Indicazioni Stradali"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_contact_form"),
                FieldPanel("form_success_message"),
            ],
            heading=_("Form Contatto"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("faq_title"),
                FieldPanel("faq_subtitle"),
                FieldPanel("faq"),
            ],
            heading=_("FAQ - Domande Frequenti"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
            ],
            heading=_("Call to Action"),
        ),
    ]
    
    class Meta:
        verbose_name = _("Contatti")
        verbose_name_plural = _("Contatti")
    
    def get_map_location(self):
        """Ritorna lat/lon per la mappa, con fallback a Torino."""
        if self.latitude and self.longitude:
            return {"lat": self.latitude, "lon": self.longitude}
        return get_default_location()
    
    # === Schema.org Methods ===
    def get_json_ld_type(self) -> str:
        return "Organization"
    
    def get_json_ld_data(self, request=None) -> dict:
        """
        Schema.org Organization con ContactPoint.
        https://schema.org/Organization
        I dati vengono presi da wagtailseo.SeoSettings (fonte unica).
        """
        # Ottieni dati base da SeoSettings
        data = get_organization_data(self)
        
        # Aggiungi dati specifici della pagina Contatti
        if self.phone:
            data["telephone"] = self.phone
        if self.email:
            data["contactPoint"] = {
                "@type": "ContactPoint",
                "email": self.email,
                "telephone": self.phone if self.phone else "",
                "contactType": "customer service",
            }
        
        # Indirizzo dalla pagina (se presente) o da SeoSettings
        if self.address:
            seo = get_seo_settings(self)
            data["address"] = {
                "@type": "PostalAddress",
                "streetAddress": self.address,
                "addressLocality": seo.struct_org_address_locality or "Castellazzo Bormida",
                "addressRegion": seo.struct_org_address_region or "Piemonte",
                "postalCode": seo.struct_org_address_postal or "15073",
                "addressCountry": seo.struct_org_address_country or "IT",
            }
        
        # Coordinate geo dalla pagina
        if self.latitude and self.longitude:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
        
        return data
    
    # === Anti-Spam: Honeypot + Timestamp (solo) ===
    
    MIN_FORM_TIME = 10  # Secondi minimi per compilare il form
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file
    MAX_FILES = 3  # Massimo 3 allegati
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt'}
    
    def _get_secret_key(self):
        """Chiave segreta per HMAC."""
        return getattr(settings, 'SECRET_KEY', 'fallback-secret')[:32]
    
    def generate_captcha_token(self):
        """
        Genera token con timestamp firmato (senza CAPTCHA matematico).
        Returns: dict con timestamp_token
        """
        timestamp = int(time.time())
        
        # Crea token HMAC: solo timestamp
        payload = str(timestamp)
        signature = hmac.new(
            self._get_secret_key().encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return {
            'timestamp_token': f"{timestamp}:{signature}",
        }
    
    def verify_timestamp(self, token):
        """
        Verifica il timestamp: form compilato in >10 secondi.
        Returns: (bool success, str error_message)
        """
        if not token:
            return False, gettext("Token anti-spam mancante")
        
        try:
            parts = token.split(':')
            if len(parts) != 2:
                return False, gettext("Token non valido")
            
            timestamp, signature = parts
            timestamp = int(timestamp)
            
            # Verifica firma HMAC
            payload = str(timestamp)
            expected_sig = hmac.new(
                self._get_secret_key().encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            if not hmac.compare_digest(signature, expected_sig):
                return False, gettext("Token manipolato")
            
            # Verifica tempo minimo (10 secondi)
            elapsed = int(time.time()) - timestamp
            if elapsed < self.MIN_FORM_TIME:
                return False, gettext("Hai compilato il form troppo velocemente")
            
            # Verifica token non troppo vecchio (1 ora)
            if elapsed > 3600:
                return False, gettext("Il form è scaduto, ricarica la pagina")
            
            return True, ""
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Timestamp verification failed: {e}")
            return False, gettext("Errore verifica anti-spam")
    
    def verify_honeypot(self, request):
        """Verifica che il campo honeypot sia vuoto."""
        honeypot = request.POST.get('website', '')
        if honeypot:
            logger.warning(f"Honeypot triggered from {request.META.get('REMOTE_ADDR')}")
            return False
        return True
    
    def validate_attachments(self, files):
        """
        Valida gli allegati: dimensione, tipo, numero.
        Returns: (list of valid files, list of errors)
        """
        valid_files = []
        errors = []
        
        if len(files) > self.MAX_FILES:
            errors.append(gettext("Puoi allegare massimo %(max)s file") % {'max': self.MAX_FILES})
            files = files[:self.MAX_FILES]
        
        for f in files:
            # Verifica estensione
            ext = '.' + f.name.split('.')[-1].lower() if '.' in f.name else ''
            if ext not in self.ALLOWED_EXTENSIONS:
                errors.append(
                    gettext("Tipo file non permesso: %(name)s. Usa: %(allowed)s") % {
                        'name': f.name,
                        'allowed': ', '.join(self.ALLOWED_EXTENSIONS)
                    }
                )
                continue
            
            # Verifica dimensione
            if f.size > self.MAX_FILE_SIZE:
                errors.append(
                    gettext("File troppo grande: %(name)s (max 5MB)") % {'name': f.name}
                )
                continue
            
            valid_files.append(f)
        
        return valid_files, errors
    
    def send_contact_email(self, form_data, attachments=None):
        """
        Invia email di contatto con allegati.
        """
        subject = gettext("[MC Castellazzo] Nuovo messaggio: %(subject)s") % {
            'subject': dict([
                ('iscrizione', gettext('Richiesta Iscrizione')),
                ('eventi', gettext('Informazioni Eventi')),
                ('collaborazioni', gettext('Collaborazioni')),
                ('altro', gettext('Altro')),
            ]).get(form_data.get('oggetto', 'altro'), form_data.get('oggetto', 'Contatto'))
        }
        
        body = f"""
Nuovo messaggio dal sito MC Castellazzo
========================================

Nome: {form_data.get('nome', '')} {form_data.get('cognome', '')}
Email: {form_data.get('email', '')}
Telefono: {form_data.get('telefono', 'Non fornito')}
Argomento: {form_data.get('oggetto', '')}

Messaggio:
{form_data.get('messaggio', '')}

---
Inviato dal form contatti di mccastellazzo.com
"""
        
        # Destinatario: email della pagina o default
        to_email = self.email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@mccastellazzo.com')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mccastellazzo.com')
        reply_to = form_data.get('email', '')
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[to_email],
            reply_to=[reply_to] if reply_to else None,
        )
        
        # Aggiungi allegati
        if attachments:
            for f in attachments:
                email.attach(f.name, f.read(), f.content_type)
        
        try:
            email.send(fail_silently=False)
            return True, ""
        except Exception as e:
            logger.error(f"Failed to send contact email: {e}")
            return False, gettext("Errore nell'invio dell'email. Riprova più tardi.")
    
    def get_context(self, request, *args, **kwargs):
        """Aggiunge dati CAPTCHA al context."""
        context = super().get_context(request, *args, **kwargs)
        context['captcha'] = self.generate_captcha_token()
        context['form_errors'] = []
        context['form_success'] = False
        return context
    
    def serve(self, request, *args, **kwargs):
        """
        Gestisce GET e POST del form contatti.
        """
        if request.method == 'POST':
            context = self.get_context(request, *args, **kwargs)
            errors = []
            
            # 1. Verifica honeypot
            if not self.verify_honeypot(request):
                # Non mostrare errore, simula successo per i bot
                context['form_success'] = True
                return TemplateResponse(request, self.template, context)
            
            # 2. Verifica Timestamp (>10 secondi)
            token = request.POST.get('captcha_token', '')
            timestamp_valid, timestamp_error = self.verify_timestamp(token)
            
            if not timestamp_valid:
                errors.append(timestamp_error)
            
            # 3. Valida campi obbligatori
            required_fields = ['nome', 'cognome', 'email', 'oggetto', 'messaggio', 'privacy']
            for field in required_fields:
                if not request.POST.get(field):
                    field_names = {
                        'nome': gettext('Nome'),
                        'cognome': gettext('Cognome'),
                        'email': gettext('Email'),
                        'oggetto': gettext('Oggetto'),
                        'messaggio': gettext('Messaggio'),
                        'privacy': gettext('Accettazione Privacy'),
                    }
                    errors.append(gettext("Campo obbligatorio: %(field)s") % {'field': field_names.get(field, field)})
            
            # 4. Valida allegati
            attachments = request.FILES.getlist('allegati')
            valid_attachments, attachment_errors = self.validate_attachments(attachments)
            errors.extend(attachment_errors)
            
            # 5. Se ci sono errori, mostra il form con errori
            if errors:
                context['form_errors'] = errors
                context['captcha'] = self.generate_captcha_token()  # Nuovo token
                # Mantieni i valori inseriti
                context['form_data'] = request.POST
                return TemplateResponse(request, self.template, context)
            
            # 6. Invia email
            form_data = {
                'nome': request.POST.get('nome', ''),
                'cognome': request.POST.get('cognome', ''),
                'email': request.POST.get('email', ''),
                'telefono': request.POST.get('telefono', ''),
                'oggetto': request.POST.get('oggetto', ''),
                'messaggio': request.POST.get('messaggio', ''),
            }
            
            success, email_error = self.send_contact_email(form_data, valid_attachments)
            
            if not success:
                context['form_errors'] = [email_error]
                context['captcha'] = self.generate_captcha_token()
                context['form_data'] = request.POST
                return TemplateResponse(request, self.template, context)
            
            # 7. Successo!
            context['form_success'] = True
            context['success_message'] = self.form_success_message or gettext("Grazie per averci contattato!")
            
            # Per richieste AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': str(context['success_message'])})
            
            return TemplateResponse(request, self.template, context)
        
        # GET request
        return super().serve(request, *args, **kwargs)
