"""
MC Castellazzo - Map Utilities
==============================
OpenStreetMap + Nominatim geocoder (no Google Maps).
"""
import requests
from django.conf import settings


def geocode_address(address: str) -> dict | None:
    """
    Geocodifica un indirizzo usando Nominatim.
    
    Args:
        address: L'indirizzo da geocodificare
        
    Returns:
        Dict con lat, lon, display_name o None se non trovato
    """
    base_url = getattr(settings, "NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
    user_agent = getattr(settings, "NOMINATIM_USER_AGENT", "MCCastellazzo/1.0")
    
    try:
        response = requests.get(
            f"{base_url}/search",
            params={
                "q": address,
                "format": "json",
                "limit": 1,
            },
            headers={"User-Agent": user_agent},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        
        if data:
            result = data[0]
            return {
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "display_name": result.get("display_name", ""),
            }
    except (requests.RequestException, ValueError, KeyError):
        pass
    
    return None


def get_default_location() -> dict:
    """
    Ritorna la location di default (Torino).
    """
    return getattr(settings, "DEFAULT_LOCATION", {
        "lat": 45.0703,
        "lon": 7.6869,
        "city": "Torino",
        "region": "Piedmont",
        "country": "IT",
    })


def generate_leaflet_map_html(
    lat: float,
    lon: float,
    zoom: int = 13,
    marker_text: str = "",
    map_id: str = "map",
    height: str = "400px",
) -> str:
    """
    Genera HTML per una mappa Leaflet con OpenStreetMap.
    
    Args:
        lat: Latitudine
        lon: Longitudine
        zoom: Livello di zoom
        marker_text: Testo popup del marker
        map_id: ID dell'elemento HTML
        height: Altezza della mappa
        
    Returns:
        HTML string per la mappa
    """
    marker_popup = f'.bindPopup("{marker_text}")' if marker_text else ""
    
    return f'''
<div id="{map_id}" style="height: {height}; width: 100%;"></div>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    (function() {{
        var map = L.map('{map_id}').setView([{lat}, {lon}], {zoom});
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }}).addTo(map);
        L.marker([{lat}, {lon}]).addTo(map){marker_popup};
    }})();
</script>
'''
