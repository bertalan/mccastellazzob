Prompt token-efficient per esperto Python dev specializzato CodeRedCMS/Wagtail. Costruisci sito dinamico motoclub accattivante: colori oro (#D4AF37), blu nautico (#1B263B), amaranto (#9B1D64). Usa Jinja2 templates su CodeRedCMS. No code/chat nelle istruzioni. Schema pagine campi identici schema.org types. TDD development, con priorità su coderedCMS. Sito 4 lingue pari (IT/FR/ES/EN). Traduzione auto IA contenuti. Auth frontend. OpenStreetMap+Nominatim (no Google Maps). Se >100 righe, suddividi file istruzioni interconnessi; compatta chat/reset a sezione. Usa docker, dove trovdrai un database per mccastellazzob, cancellalo e installalo ex nuovo. Ingora la cartella vecchio presente nella root, come da .gitignore
Usa le ultime versioni, minimo i seguenti: 
- Stack: CodeRedCMS 6.0 / Wagtail 7.0 LTS / Django 5.2 LTS

## Sezione 1: Setup Base + Pagine Principali (file: setup_base.txt)
- Inizializza CodeRedCMS project Wagtail. Config LANGUAGES=[('it','Italiano'),('fr','Français'),('es','Español'),('en','English')]. Integra Jinja2 templating. Tema CSS: gradienti oro-blu, accenti amaranto, responsive mobile-first, animazioni smooth timeline.
- Homepage: schema.org Organization. Campi: name, logo, url, description, address (PostalAddress: street, city=Torino, region=Piedmont, country=IT), contactPoint (ContactPoint: telephone, email), foundingDate, knowsAbout=Motoclub.
- Pagina Timeline: schema.org ItemList verticale. StreamField articoli (schema.org Article/NewsArticle): headline, image, datePublished (recenti cima), articleSection (categoria/tema), url (link approfondimento). Template Jinja2 verticale scroll con foto hover.
- Pagine Chi Siamo: schema.org AboutPage. Sottopagine: Consiglio Direttivo (schema.org Organization: member list con name, role, image); Trasparenza (schema.org WebPage: bilanci, documenti allegati); Contatti (schema.org ContactPage: form con name/email/message, mappa OpenStreetMap Nominatim geocoder lat/lon Torino).[1][2][3]

## Sezione 2: Eventi + Storico (file: eventi_storico.txt)
- Eventi: schema.org EventSeries. Lista eventi anno corrente (filter current year da today). Campi: name, startDate/endDate, location (Place: name, address), image, description, organizer (Organization ref), eventStatus (EventScheduled/Cancelled). Template grid cards.
- Storico Eventi: pagina archivio, filtra per anno passato (gruppi annuali, newest year top). Ogni evento link a dettaglio schema.org Event full.
- Caricamento articoli/gallerie: Editor con multiple ImageChooserPanel (schema.org ImageObject array), lightbox gallery Jinja2 responsive multi-foto.[4][5]

## Sezione 3: Multilingua + Traduzione IA (file: multilanguage_ai.txt)
- Wagtail-localize + django-parler o custom: pagine tradotte linkate 4 lingue pari, switcher header. Percorsi /it/ /fr/ /es/ /en/.
- Integra servizio IA (es. DeepL API o LibreTranslate open): auto-traduci campi RichText/CharField on-save/publish, fallback manuale. Batch translate nuovi contenuti.[3]

## Sezione 4: Auth + Mappe + Finale (file: auth_mappe.txt)
- Frontend auth: django-allauth + Wagtail integration. Pagine login/register/password-reset frontend templates Jinja2, session user menu.
- Sostituisci Google Maps: OpenStreetMap blocks con Nominatim geocoder (API search address->lat/lon), embed Leaflet.js interattivo.
- Integra tutto: menu nav lingue/auth, search globale, SEO schema.org JSON-LD auto. Migra, collectstatic, deploy-ready. Test dinamico 4 lingue.[6][7]

Esegui sequenziale: completa sezione, reset chat, prosegui prossima citando prev. Totale token minimo.[2][8][5][4]

[1](https://www.coderedcorp.com/cms/)
[2](https://github.com/coderedcorp/coderedcms)
[3](https://www.unomena.com/insights/creating-multi-language-site-wagtail-cms)
[4](https://docs.wagtail.org/en/stable/topics/pages.html)
[5](https://schema.org/Event)
[6](https://learnwagtail.com/tutorials/adding-user-authentication-registration-and-login-your-wagtail-website/)
[7](https://stackoverflow.com/questions/79085529/django-wagtail-react-native-and-3rd-party-signup-and-signin)
[8](https://pypi.org/project/coderedcms/)
[9](https://docs.wagtail.org/en/6.3/deployment/)
[10](https://www.codered.cloud/docs/wagtail/quickstart/)
[11](https://stackoverflow.com/questions/7337814/jinja2-load-template-file-from-template)
[12](https://www.reddit.com/r/WagtailCMS/comments/mo2cbv/registration_system_allowing_loggedin_users_to/)
[13](https://djangopackages.org/grids/g/two-factor-authentication/)
[14](https://docs.wagtail.org/en/v1.13.4/getting_started/integrating_into_django.html)
[15](https://pagescms.org/docs/custom-fields/)
[16](https://docs.wagtail.org/en/stable/getting_started/tutorial.html)
[17](https://www.youtube.com/watch?v=kAblCAxsWzY)
[18](https://www.reddit.com/r/web_design/comments/ad8tw/how_should_i_set_up_a_multilingual_site/)