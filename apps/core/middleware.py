"""
MC Castellazzo - Security Headers Middleware (V2-020)
======================================================
Aggiunge header di sicurezza moderni non coperti nativamente da Django:
- Permissions-Policy
- Cross-Origin-Opener-Policy (COOP)
- Cross-Origin-Embedder-Policy (COEP)
- Cross-Origin-Resource-Policy (CORP)
"""


class SecurityHeadersMiddleware:
    """
    Middleware che inietta header di sicurezza HTTP moderni in ogni risposta.
    Da abilitare solo in produzione (vedi prod.py).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

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
