"""
MC Castellazzo - Bulk Upload Admin Views
=========================================
Viste admin per il caricamento massivo di immagini e API per metadati immagini.
"""

import io
import json
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.http import require_GET
from wagtail.images import get_image_model
from wagtail.models import Collection

from apps.core.forms import BulkUploadForm
from apps.core.image_optimizer import (
    generate_filename,
    optimize_image,
)


Image = get_image_model()


def process_bulk_upload(
    images: list,
    title_prefix: str,
    tags: list,
    collection: Optional[Collection] = None,
    user=None,
) -> list:
    """
    Processa un batch di immagini per l'upload.
    
    Args:
        images: Lista di file immagine caricati
        title_prefix: Prefisso per i titoli
        tags: Lista di tag da applicare
        collection: Collezione Wagtail opzionale
        user: Utente che esegue l'upload
        
    Returns:
        Lista di oggetti Image creati
    """
    created_images = []
    
    # Se non specificata, usa la root collection
    if collection is None:
        collection = Collection.get_first_root_node()
    
    for idx, uploaded_file in enumerate(images):
        # Numero sequenziale 1-based per titolo, 0-based per filename
        sequence_num = idx + 1
        
        # Genera titolo con numero
        title = f"{title_prefix} - {sequence_num:03d}"
        
        # Genera nome file
        filename = generate_filename(title_prefix, idx)
        
        # Leggi e ottimizza l'immagine
        image_buffer = io.BytesIO(uploaded_file.read())
        optimized_buffer = optimize_image(image_buffer)
        
        # Crea il file Django
        django_file = ContentFile(
            optimized_buffer.read(),
            name=filename
        )
        
        # Crea l'oggetto Image di Wagtail
        wagtail_image = Image(
            title=title,
            file=django_file,
            collection=collection,
        )
        
        # Imposta l'utente che ha caricato se disponibile
        if user and hasattr(wagtail_image, "uploaded_by_user"):
            wagtail_image.uploaded_by_user = user
        
        wagtail_image.save()
        
        # Aggiungi i tag
        if tags:
            for tag in tags:
                wagtail_image.tags.add(tag)
        
        created_images.append(wagtail_image)
    
    return created_images


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("wagtailimages.add_image", raise_exception=True),
    name="dispatch"
)
class BulkUploadView(View):
    """Vista per il caricamento massivo di immagini."""
    
    template_name = "wagtailadmin/bulk_upload.html"
    
    def get(self, request):
        """Mostra il form di upload."""
        form = BulkUploadForm()
        return render(request, self.template_name, {
            "form": form,
            "page_title": _("Caricamento massivo immagini"),
        })
    
    def post(self, request):
        """Processa l'upload."""
        form = BulkUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Estrai i dati dal form
            title_prefix = form.cleaned_data["title_prefix"]
            tags = form.cleaned_data.get("tags", [])
            collection = form.cleaned_data.get("collection")
            images = request.FILES.getlist("images")
            
            # Processa le immagini
            try:
                created = process_bulk_upload(
                    images=images,
                    title_prefix=title_prefix,
                    tags=tags,
                    collection=collection,
                    user=request.user,
                )
                
                # Messaggio di successo
                messages.success(
                    request,
                    _("Caricate con successo %(count)d immagini!") % {
                        "count": len(created)
                    }
                )
                
                # Redirect alla lista immagini
                return redirect("wagtailimages:index")
                
            except Exception as e:
                messages.error(
                    request,
                    _("Errore durante il caricamento: %(error)s") % {
                        "error": str(e)
                    }
                )
        
        return render(request, self.template_name, {
            "form": form,
            "page_title": _("Caricamento massivo immagini"),
        })


@login_required
@require_GET
def get_image_metadata(request, image_id):
    """
    API endpoint per recuperare i metadati di un'immagine.
    Restituisce titolo, descrizione e tag dell'immagine.
    """
    try:
        image = Image.objects.get(pk=image_id)
        
        # Recupera i tag come stringa
        tags_list = list(image.tags.names())
        
        return JsonResponse({
            "success": True,
            "data": {
                "id": image.id,
                "title": image.title or "",
                "description": getattr(image, "description", "") or "",
                "tags": tags_list,
                "alt_text": getattr(image, "alt_text", "") or image.title or "",
            }
        })
    except Image.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Image not found"
        }, status=404)
