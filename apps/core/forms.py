"""
MC Castellazzo - Bulk Upload Forms
===================================
Forms per il caricamento massivo di immagini.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from taggit.forms import TagField
from wagtail.models import Collection


class MultipleFileInput(forms.ClearableFileInput):
    """Widget per upload multiplo di file."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Campo per upload multiplo di file."""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]


class BulkUploadForm(forms.Form):
    """
    Form per il caricamento massivo di immagini.
    
    Campi:
    - title_prefix: Prefisso comune per i titoli (es. "Raduno 2026")
    - tags: Tag comuni da applicare a tutte le immagini
    - collection: Collezione Wagtail dove salvare
    - images: File immagini da caricare
    """
    
    title_prefix = forms.CharField(
        label=_("Prefisso titolo"),
        max_length=100,
        required=True,
        help_text=_(
            "Il titolo base per tutte le immagini. "
            "Verrà aggiunto un numero sequenziale (es. 'Raduno 2026' → "
            "'Raduno 2026 - 001', 'Raduno 2026 - 002', ...)"
        ),
        widget=forms.TextInput(attrs={
            "class": "w-field__input",
            "placeholder": _("es. Raduno Madonnina 2026")
        })
    )
    
    tags = TagField(
        label=_("Tag"),
        required=False,
        help_text=_(
            "Tag comuni da applicare a tutte le immagini. "
            "Separare con virgola."
        ),
        widget=forms.TextInput(attrs={
            "class": "w-field__input",
            "placeholder": _("es. raduno, 2026, madonnina")
        })
    )
    
    collection = forms.ModelChoiceField(
        label=_("Collezione"),
        queryset=Collection.objects.all(),
        required=False,
        empty_label=_("Root (nessuna collezione)"),
        help_text=_("Collezione dove salvare le immagini."),
        widget=forms.Select(attrs={
            "class": "w-field__input"
        })
    )
    
    images = MultipleFileField(
        label=_("Immagini"),
        required=True,
        help_text=_(
            "Seleziona una o più immagini. "
            "Formati supportati: JPG, PNG, GIF, WebP. "
            "Le immagini verranno ottimizzate automaticamente: "
            "max 1280px, formato WebP, qualità 85%."
        ),
        widget=MultipleFileInput(attrs={
            "class": "w-field__input",
            "accept": "image/*",
            "multiple": True
        })
    )
    
    def clean_images(self):
        """Valida i file immagine."""
        images = self.cleaned_data.get("images", [])
        
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        ]
        
        for image in images:
            if hasattr(image, "content_type"):
                if image.content_type not in allowed_types:
                    raise forms.ValidationError(
                        _("Formato non supportato: %(name)s. "
                          "Usa JPG, PNG, GIF o WebP."),
                        params={"name": image.name}
                    )
        
        return images
