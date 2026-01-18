"""
Widget personalizzati per l'admin Wagtail.
"""
from django import forms
from django.utils.safestring import mark_safe


class AddressWithGeocodingWidget(forms.TextInput):
    """
    Widget per l'inserimento dell'indirizzo con geocoding automatico.
    Quando l'utente inserisce un indirizzo e preme Tab o clicca fuori,
    le coordinate lat/lng vengono recuperate automaticamente da Nominatim.
    """
    
    template_name = "widgets/address_geocoding.html"
    
    def __init__(self, lat_field_id=None, lng_field_id=None, *args, **kwargs):
        self.lat_field_id = lat_field_id
        self.lng_field_id = lng_field_id
        super().__init__(*args, **kwargs)
    
    class Media:
        js = ("js/address_geocoding.js",)
    
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-geocoding-widget"] = "true"
        if self.lat_field_id:
            attrs["data-lat-field"] = self.lat_field_id
        if self.lng_field_id:
            attrs["data-lng-field"] = self.lng_field_id
        return attrs
