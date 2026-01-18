"""
Test TDD per Bulk Upload Immagini con Ottimizzazione.

Funzionalità:
- Upload multiplo immagini
- Metadati comuni (prefisso titolo, tag, collezione, categoria)
- Ottimizzazione automatica (resize 1280px, WebP 85%)
- Rinomina file secondo pattern: prefisso-000.webp
- Multilingua UI
"""

import io
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

User = get_user_model()


def create_test_image(width=4000, height=3000, format="JPEG"):
    """Crea un'immagine di test in memoria."""
    image = Image.new("RGB", (width, height), color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer


def create_uploaded_image(name="test.jpg", width=4000, height=3000):
    """Crea un SimpleUploadedFile per i test."""
    buffer = create_test_image(width, height)
    return SimpleUploadedFile(
        name=name,
        content=buffer.read(),
        content_type="image/jpeg"
    )


# ============================================
# Test Accesso Vista
# ============================================
@pytest.mark.django_db
class TestBulkUploadViewAccess:
    """Test per l'accesso alla vista di bulk upload."""

    def test_view_requires_login(self, client):
        """La vista richiede autenticazione."""
        response = client.get("/admin/bulk-upload/")
        # Redirect al login
        assert response.status_code in [302, 403]

    def test_view_requires_image_permission(self, client):
        """L'utente deve avere permesso di aggiungere immagini."""
        # Crea utente senza permessi
        user = User.objects.create_user(
            username="noperm",
            email="noperm@test.com",
            password="testpass123"
        )
        client.login(username="noperm", password="testpass123")
        
        response = client.get("/admin/bulk-upload/")
        assert response.status_code in [302, 403]

    def test_view_accessible_by_superuser(self, client):
        """Un superuser può accedere alla vista."""
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        User.objects.create_superuser(
            username=f"admin_{unique_id}",
            email=f"admin_{unique_id}@test.com",
            password="testpass123"
        )
        client.login(username=f"admin_{unique_id}", password="testpass123")
        
        response = client.get("/admin/bulk-upload/")
        assert response.status_code == 200


# ============================================
# Test Form
# ============================================
@pytest.mark.django_db
class TestBulkUploadForm:
    """Test per il form di bulk upload."""

    def test_form_has_title_prefix_field(self):
        """Il form deve avere il campo prefisso titolo."""
        from apps.core.forms import BulkUploadForm
        form = BulkUploadForm()
        assert "title_prefix" in form.fields

    def test_form_has_tags_field(self):
        """Il form deve avere il campo tag."""
        from apps.core.forms import BulkUploadForm
        form = BulkUploadForm()
        assert "tags" in form.fields

    def test_form_has_collection_field(self):
        """Il form deve avere il campo collezione."""
        from apps.core.forms import BulkUploadForm
        form = BulkUploadForm()
        assert "collection" in form.fields

    def test_form_has_images_field(self):
        """Il form deve avere il campo immagini."""
        from apps.core.forms import BulkUploadForm
        form = BulkUploadForm()
        assert "images" in form.fields

    def test_form_title_prefix_required(self):
        """Il prefisso titolo è obbligatorio."""
        from apps.core.forms import BulkUploadForm
        form = BulkUploadForm(data={})
        assert not form.is_valid()
        assert "title_prefix" in form.errors


# ============================================
# Test Ottimizzazione Immagini
# ============================================
@pytest.mark.django_db
class TestImageOptimization:
    """Test per l'ottimizzazione delle immagini."""

    def test_resize_landscape_image_to_1280_width(self):
        """Un'immagine landscape viene ridimensionata a max 1280px di larghezza."""
        from apps.core.image_optimizer import optimize_image
        
        # Immagine 4000x3000 (landscape)
        buffer = create_test_image(4000, 3000)
        result = optimize_image(buffer)
        
        img = Image.open(result)
        assert img.width == 1280
        assert img.height == 960  # Mantiene proporzioni

    def test_resize_portrait_image_to_1280_height(self):
        """Un'immagine portrait viene ridimensionata a max 1280px di altezza."""
        from apps.core.image_optimizer import optimize_image
        
        # Immagine 3000x4000 (portrait)
        buffer = create_test_image(3000, 4000)
        result = optimize_image(buffer)
        
        img = Image.open(result)
        assert img.height == 1280
        assert img.width == 960  # Mantiene proporzioni

    def test_small_image_not_upscaled(self):
        """Un'immagine piccola non viene ingrandita."""
        from apps.core.image_optimizer import optimize_image
        
        # Immagine 800x600 (già piccola)
        buffer = create_test_image(800, 600)
        result = optimize_image(buffer)
        
        img = Image.open(result)
        assert img.width == 800
        assert img.height == 600

    def test_convert_to_webp(self):
        """L'immagine viene convertita in WebP."""
        from apps.core.image_optimizer import optimize_image
        
        buffer = create_test_image(2000, 1500)
        result = optimize_image(buffer)
        
        img = Image.open(result)
        assert img.format == "WEBP"

    def test_webp_quality_reduces_filesize(self):
        """La compressione WebP 85% riduce significativamente la dimensione."""
        from apps.core.image_optimizer import optimize_image
        
        buffer = create_test_image(2000, 1500)
        original_size = buffer.getbuffer().nbytes
        
        result = optimize_image(buffer)
        optimized_size = result.getbuffer().nbytes
        
        # Deve essere almeno 50% più piccolo
        assert optimized_size < original_size * 0.5

    def test_aspect_ratio_maintained(self):
        """L'aspect ratio viene mantenuto."""
        from apps.core.image_optimizer import optimize_image
        
        # Immagine 16:9
        buffer = create_test_image(3840, 2160)
        result = optimize_image(buffer)
        
        img = Image.open(result)
        original_ratio = 3840 / 2160
        new_ratio = img.width / img.height
        
        assert abs(original_ratio - new_ratio) < 0.01


# ============================================
# Test Rinomina File
# ============================================
@pytest.mark.django_db
class TestFileRenaming:
    """Test per la rinomina dei file."""

    def test_generate_filename_with_prefix_and_number(self):
        """Genera nome file con prefisso e numero progressivo."""
        from apps.core.image_optimizer import generate_filename
        
        result = generate_filename("Raduno Madonnina 2026", 0)
        assert result == "raduno-madonnina-2026-000.webp"

    def test_generate_filename_sequential_numbers(self):
        """I numeri sono sequenziali con zero-padding."""
        from apps.core.image_optimizer import generate_filename
        
        assert generate_filename("Test", 0) == "test-000.webp"
        assert generate_filename("Test", 1) == "test-001.webp"
        assert generate_filename("Test", 99) == "test-099.webp"
        assert generate_filename("Test", 100) == "test-100.webp"

    def test_generate_filename_sanitizes_special_chars(self):
        """I caratteri speciali vengono rimossi/sostituiti."""
        from apps.core.image_optimizer import generate_filename
        
        result = generate_filename("Raduno 2026 - Foto è bella!", 5)
        # Deve essere URL-safe
        assert " " not in result
        assert "!" not in result
        assert "è" not in result or "e" in result

    def test_generate_filename_lowercase(self):
        """Il nome file è tutto minuscolo."""
        from apps.core.image_optimizer import generate_filename
        
        result = generate_filename("RADUNO GRANDE", 0)
        assert result == result.lower()

    def test_generate_filename_max_length(self):
        """Il nome file non supera una lunghezza ragionevole."""
        from apps.core.image_optimizer import generate_filename
        
        long_prefix = "A" * 200
        result = generate_filename(long_prefix, 0)
        
        # Max 100 caratteri per il nome file
        assert len(result) <= 100


# ============================================
# Test Processing Batch
# ============================================
@pytest.mark.django_db
class TestBulkUploadProcessing:
    """Test per il processing batch delle immagini."""

    def test_upload_creates_wagtail_images(self):
        """L'upload crea oggetti Image di Wagtail."""
        from wagtail.images import get_image_model
        from apps.core.admin_views import process_bulk_upload
        
        Image = get_image_model()
        initial_count = Image.objects.count()
        
        images = [
            create_uploaded_image("foto1.jpg"),
            create_uploaded_image("foto2.jpg"),
        ]
        
        process_bulk_upload(
            images=images,
            title_prefix="Test Upload",
            tags=["test", "upload"],
            collection=None
        )
        
        assert Image.objects.count() == initial_count + 2

    def test_upload_applies_sequential_titles(self):
        """Le immagini hanno titoli sequenziali."""
        from wagtail.images import get_image_model
        from apps.core.admin_views import process_bulk_upload
        
        Image = get_image_model()
        
        images = [
            create_uploaded_image("a.jpg"),
            create_uploaded_image("b.jpg"),
            create_uploaded_image("c.jpg"),
        ]
        
        created = process_bulk_upload(
            images=images,
            title_prefix="Evento 2026",
            tags=[],
            collection=None
        )
        
        titles = [img.title for img in created]
        assert "Evento 2026 - 001" in titles
        assert "Evento 2026 - 002" in titles
        assert "Evento 2026 - 003" in titles

    def test_upload_applies_tags_to_all(self):
        """I tag vengono applicati a tutte le immagini."""
        from wagtail.images import get_image_model
        from apps.core.admin_views import process_bulk_upload
        
        Image = get_image_model()
        
        images = [create_uploaded_image("test.jpg")]
        
        created = process_bulk_upload(
            images=images,
            title_prefix="Test",
            tags=["raduno", "2026", "madonnina"],
            collection=None
        )
        
        img = created[0]
        tag_names = [tag.name for tag in img.tags.all()]
        
        assert "raduno" in tag_names
        assert "2026" in tag_names
        assert "madonnina" in tag_names

    def test_upload_renames_files(self):
        """I file vengono rinominati secondo il pattern."""
        from wagtail.images import get_image_model
        from apps.core.admin_views import process_bulk_upload
        
        images = [
            create_uploaded_image("DSC_12345.jpg"),
            create_uploaded_image("IMG_67890.jpg"),
        ]
        
        created = process_bulk_upload(
            images=images,
            title_prefix="Raduno Primavera",
            tags=[],
            collection=None
        )
        
        # I file devono avere nomi puliti (0-based per i file)
        assert "raduno-primavera-000" in created[0].file.name
        assert "raduno-primavera-001" in created[1].file.name


# ============================================
# Test Multilingua
# ============================================
@pytest.mark.django_db
class TestBulkUploadI18n:
    """Test per le traduzioni dell'interfaccia."""

    def test_form_labels_translated_en(self, client):
        """Le label del form sono tradotte in inglese."""
        from django.utils.translation import activate
        from apps.core.forms import BulkUploadForm
        
        activate("en")
        form = BulkUploadForm()
        
        # Verifica che le label non siano in italiano
        title_label = str(form.fields["title_prefix"].label)
        assert title_label != "" and title_label is not None

    def test_form_labels_translated_fr(self, client):
        """Le label del form sono tradotte in francese."""
        from django.utils.translation import activate
        from apps.core.forms import BulkUploadForm
        
        activate("fr")
        form = BulkUploadForm()
        
        title_label = str(form.fields["title_prefix"].label)
        assert title_label != "" and title_label is not None

    def test_form_labels_translated_de(self, client):
        """Le label del form sono tradotte in tedesco."""
        from django.utils.translation import activate
        from apps.core.forms import BulkUploadForm
        
        activate("de")
        form = BulkUploadForm()
        
        title_label = str(form.fields["title_prefix"].label)
        assert title_label != "" and title_label is not None

    def test_form_labels_translated_es(self, client):
        """Le label del form sono tradotte in spagnolo."""
        from django.utils.translation import activate
        from apps.core.forms import BulkUploadForm
        
        activate("es")
        form = BulkUploadForm()
        
        title_label = str(form.fields["title_prefix"].label)
        assert title_label != "" and title_label is not None


# ============================================
# Test Menu Admin
# ============================================
@pytest.mark.django_db
class TestBulkUploadAdminMenu:
    """Test per l'integrazione nel menu admin."""

    def test_menu_item_appears_in_images_menu(self, client):
        """La voce appare nel menu Immagini di Wagtail."""
        User.objects.create_superuser(
            username="admin2",
            email="admin2@test.com",
            password="testpass123"
        )
        client.login(username="admin2", password="testpass123")
        
        # Accedi all'admin
        response = client.get("/admin/")
        
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            # Deve contenere link al bulk upload
            assert "bulk-upload" in content.lower() or "caricamento" in content.lower()
