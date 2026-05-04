"""
MC Castellazzo - Security Headers Middleware (V2-020 + V2-017)
==============================================================
Aggiunge header di sicurezza moderni non coperti nativamente da Django:
- Content-Security-Policy (V2-017)
- Permissions-Policy
- Cross-Origin-Opener-Policy (COOP)
- Cross-Origin-Embedder-Policy (COEP)
- Cross-Origin-Resource-Policy (CORP)
"""

from django.conf import settings


# CSP per pagine pubbliche del sito.
# Sorgenti esterne effettivamente caricate dai template:
#   - https://fonts.googleapis.com (CSS Google Fonts)
#   - https://fonts.gstatic.com (file font Google)
#   - https://cdnjs.cloudflare.com (FontAwesome)
#   - https://unpkg.com (Leaflet, AOS)
#   - https://*.tile.openstreetmap.org (tile mappe)
#   - https://nominatim.openstreetmap.org (geocoding lato server, ma anche fetch)
_PUBLIC_CSP = "; ".join(
    [
        "default-src 'self'",
        # 'unsafe-inline' richiesto da blocchi inline generati da coderedcms/Wagtail
        # e da onclick handler nei template. Senza 'unsafe-eval'.
        "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
        "https://unpkg.com https://cdnjs.cloudflare.com",
        "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        # img-src permissivo: i tile OSM, le immagini editoriali e i data:
        # SVG (es. QR code) devono passare. https: copre tutti i CDN HTTPS.
        "img-src 'self' data: blob: https:",
        "connect-src 'self' https://nominatim.openstreetmap.org",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
    ]
)


def _is_admin_path(path: str) -> bool:
    """Wagtail/Django admin usa eval/inline aggressivamente: skip CSP lì."""
    return path.startswith(("/admin/", "/django-admin/", "/cms/"))


class SecurityHeadersMiddleware:
    """
    Middleware che inietta header di sicurezza HTTP moderni in ogni risposta.
    Da abilitare solo in produzione (vedi prod.py).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # --- CSP (V2-017) -------------------------------------------------
        # Skip per i percorsi admin (Wagtail richiede unsafe-eval/inline).
        if not _is_admin_path(request.path):
            # Toggle Report-Only via settings: durante il rollout è True,
            # poi si passa a False per enforce.
            csp_header = (
                "Content-Security-Policy-Report-Only"
                if getattr(settings, "CSP_REPORT_ONLY", True)
                else "Content-Security-Policy"
            )
            # Non sovrascrivere se Wagtail/altre app hanno già impostato la CSP
            if csp_header not in response and "Content-Security-Policy" not in response:
                response[csp_header] = _PUBLIC_CSP

        # Limita accesso a camera/microfono/geolocalizzazione
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Isola il browsing context per prevenire Spectre side-channel attacks
        response["Cross-Origin-Opener-Policy"] = "same-origin"

        # Necessario per abilitare COEP; consente risorse cross-origin esplicite
        # NOTA: "unsafe-none" è il default meno restrittivo; usare "require-corp"
        # solo se tutte le risorse esterne (Leaflet CDN, ecc.) aggiungono CORP header.
        response["Cross-Origin-Embedder-Policy"] = "unsafe-none"

        # Le risorse statiche di questo sito non devono essere caricate cross-origin
        response["Cross-Origin-Resource-Policy"] = "same-site"

        return response
