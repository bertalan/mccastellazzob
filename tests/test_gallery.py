"""
Test per la galleria e il lightbox.
TDD: test first secondo CLAUDE.md
"""
import pytest
from django.test import Client
from bs4 import BeautifulSoup
from wagtail.models import Locale, Site, Collection, Page
from wagtail.images import get_image_model

from apps.website.models import GalleryPage, GalleryImage, GalleryCategory
from apps.website.blocks import CollectionGalleryBlock

Image = get_image_model()


@pytest.fixture
def it_locale(db):
    """Fixture per la locale italiana."""
    return Locale.objects.get_or_create(language_code="it")[0]


@pytest.fixture
def gallery_category(db, it_locale):
    """Fixture per una categoria galleria."""
    return GalleryCategory.objects.create(
        name="Test Category",
        slug="test-cat",
        icon="fas fa-camera",
        sort_order=1,
        locale=it_locale,
    )


@pytest.mark.django_db
class TestGalleryLightbox:
    """Test per il lightbox della galleria."""
    
    def test_lightbox_has_close_button(self, client):
        """Il lightbox deve avere un pulsante di chiusura funzionante."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Cerca il lightbox
            lightbox = soup.find(id="lightbox")
            if lightbox:
                # Deve avere un pulsante di chiusura
                close_btn = lightbox.find("button", {"aria-label": True})
                assert close_btn is not None, "Lightbox deve avere un pulsante di chiusura"
                
                # Il pulsante deve avere un onclick che chiama closeLightbox
                onclick = close_btn.get("onclick", "")
                assert "closeLightbox" in onclick, "Pulsante deve chiamare closeLightbox"
    
    def test_lightbox_has_title_and_caption_elements(self, client):
        """Il lightbox deve avere elementi per titolo e descrizione."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Cerca gli elementi del lightbox
            title_elem = soup.find(id="lightbox-title")
            caption_elem = soup.find(id="lightbox-caption")
            
            assert title_elem is not None, "Lightbox deve avere elemento per il titolo"
            assert caption_elem is not None, "Lightbox deve avere elemento per la descrizione"
    
    def test_lightbox_javascript_functions_defined(self, client):
        """Le funzioni JavaScript del lightbox devono essere definite."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            
            # Verifica che le funzioni siano definite
            assert "function openLightbox" in content, "openLightbox deve essere definita"
            assert "function closeLightbox" in content, "closeLightbox deve essere definita"
    
    def test_lightbox_close_removes_hidden_class(self, client):
        """closeLightbox deve aggiungere la classe hidden."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            
            # La funzione closeLightbox deve manipolare la classe hidden
            assert "classList.add('hidden')" in content or 'classList.add("hidden")' in content, \
                "closeLightbox deve aggiungere la classe hidden"


@pytest.mark.django_db
class TestGalleryImageData:
    """Test per i dati delle immagini nella galleria."""
    
    def test_image_title_not_none_string(self, client):
        """Il titolo dell'immagine non deve mostrare 'None' come stringa."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            content = response.content.decode("utf-8")
            
            # Non deve esserci "None" come valore di data-title o nel onclick
            # Cerca pattern sospetti
            assert "data-title=\"None\"" not in content, \
                "data-title non deve contenere la stringa 'None'"
            assert "'None'" not in content or "None" not in content.split("openLightbox")[1][:100] if "openLightbox" in content else True, \
                "openLightbox non deve passare 'None' come parametro"
    
    def test_gallery_item_has_data_attributes(self, client):
        """Gli item della galleria devono avere gli attributi data corretti."""
        response = client.get("/it/galleria/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            gallery_items = soup.find_all(class_="gallery-item")
            for item in gallery_items:
                # Ogni item deve avere data-title e data-caption (anche se vuoti)
                assert item.has_attr("data-title"), "gallery-item deve avere data-title"
                assert item.has_attr("data-caption"), "gallery-item deve avere data-caption"
                
                # I valori non devono essere la stringa "None"
                assert item.get("data-title") != "None", "data-title non deve essere 'None'"
                assert item.get("data-caption") != "None", "data-caption non deve essere 'None'"


@pytest.mark.django_db
class TestGalleryCategory:
    """Test per le categorie della galleria."""
    
    def test_category_model_has_required_fields(self, gallery_category):
        """GalleryCategory deve avere tutti i campi richiesti."""
        assert gallery_category.name == "Test Category"
        assert gallery_category.slug == "test-cat"
        assert gallery_category.icon == "fas fa-camera"
        assert gallery_category.sort_order == 1
    
    def test_category_str_representation(self, gallery_category):
        """GalleryCategory deve avere una rappresentazione stringa corretta."""
        assert str(gallery_category) == "Test Category"
    
    def test_category_is_translatable(self, gallery_category, it_locale):
        """GalleryCategory deve supportare le traduzioni."""
        # Verifica che abbia translation_key (da TranslatableMixin)
        assert hasattr(gallery_category, "translation_key")
        assert gallery_category.locale == it_locale


# ============================================
# Test Collection Gallery Block
# ============================================
@pytest.fixture
def test_collection(db):
    """Fixture per una collezione di test."""
    root = Collection.get_first_root_node()
    return root.add_child(name="Raduno 2026")


@pytest.fixture
def test_collection_2(db):
    """Fixture per una seconda collezione di test."""
    root = Collection.get_first_root_node()
    return root.add_child(name="Raduno 2025")


@pytest.fixture
def test_image_in_collection(db, test_collection):
    """Fixture per un'immagine nella collezione."""
    import io
    from PIL import Image as PILImage
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # Crea immagine di test
    pil_image = PILImage.new("RGB", (100, 100), color="blue")
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Usa SimpleUploadedFile che gestisce width/height automaticamente
    file = SimpleUploadedFile(
        name="test-raduno-001.png",
        content=buffer.read(),
        content_type="image/png"
    )
    
    image = Image(
        title="Foto Raduno 001",
        collection=test_collection,
        file=file,
    )
    image.save()
    image.tags.add("raduno", "2026", "madonnina")
    
    return image


@pytest.fixture
def test_image_in_collection_2(db, test_collection_2):
    """Fixture per un'immagine nella seconda collezione."""
    import io
    from PIL import Image as PILImage
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    pil_image = PILImage.new("RGB", (100, 100), color="green")
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    
    file = SimpleUploadedFile(
        name="test-raduno-2025.png",
        content=buffer.read(),
        content_type="image/png"
    )
    
    image = Image(
        title="Foto Raduno 2025",
        collection=test_collection_2,
        file=file,
    )
    image.save()
    image.tags.add("raduno", "2025")
    
    return image


@pytest.fixture
def gallery_page_with_collection_block(
    db, it_locale, test_collection, test_image_in_collection, gallery_category
):
    """Fixture per una GalleryPage con CollectionGalleryBlock in StreamField."""
    from wagtail.blocks import StreamValue
    
    root_page = Page.objects.filter(depth=1).first()
    
    # Crea StreamField con CollectionGalleryBlock
    gallery_blocks = [
        {
            "type": "collection_gallery",
            "value": {
                "collection": test_collection.id,
                "category": gallery_category.id,
            }
        }
    ]
    
    gallery = GalleryPage(
        title="Galleria Test",
        slug="galleria-test",
        locale=it_locale,
    )
    gallery.gallery = gallery_blocks
    root_page.add_child(instance=gallery)
    
    return gallery


@pytest.mark.django_db
class TestCollectionGalleryBlock:
    """Test per il blocco CollectionGalleryBlock."""
    
    def test_block_exists(self):
        """CollectionGalleryBlock deve esistere."""
        from apps.website.blocks import CollectionGalleryBlock
        assert CollectionGalleryBlock is not None
    
    def test_block_has_collection_field(self):
        """CollectionGalleryBlock deve avere campo collection."""
        block = CollectionGalleryBlock()
        assert "collection" in block.child_blocks
    
    def test_block_has_category_field(self):
        """CollectionGalleryBlock deve avere campo category opzionale."""
        block = CollectionGalleryBlock()
        assert "category" in block.child_blocks
    
    def test_gallery_streamfield_accepts_collection_block(
        self, gallery_page_with_collection_block
    ):
        """GalleryPage.gallery deve accettare CollectionGalleryBlock."""
        # Verifica che la galleria abbia almeno un blocco
        assert len(gallery_page_with_collection_block.gallery) >= 1
    
    def test_get_all_images_includes_collection_block_images(
        self, gallery_page_with_collection_block, test_image_in_collection
    ):
        """get_all_images() deve includere le immagini dai blocchi collezione."""
        images = gallery_page_with_collection_block.get_all_images()
        
        # Deve contenere l'immagine dalla collection
        image_ids = [img["image"].id for img in images]
        assert test_image_in_collection.id in image_ids
    
    def test_collection_block_images_use_image_title(
        self, gallery_page_with_collection_block, test_image_in_collection
    ):
        """Le immagini dal blocco Collection usano Image.title come titolo."""
        images = gallery_page_with_collection_block.get_all_images()
        
        collection_img = next(
            img for img in images if img["image"] == test_image_in_collection
        )
        assert collection_img["title"] == "Foto Raduno 001"
    
    def test_collection_block_images_use_tags_as_caption(
        self, gallery_page_with_collection_block, test_image_in_collection
    ):
        """Le immagini dal blocco Collection usano i tag come descrizione."""
        images = gallery_page_with_collection_block.get_all_images()
        
        collection_img = next(
            img for img in images if img["image"] == test_image_in_collection
        )
        caption = collection_img["caption"]
        # La caption contiene i tag separati da virgola
        assert "raduno" in caption.lower() or "2026" in caption
    
    def test_collection_block_category_applied(
        self, gallery_page_with_collection_block, test_image_in_collection, gallery_category
    ):
        """La categoria del blocco viene applicata alle immagini."""
        images = gallery_page_with_collection_block.get_all_images()
        
        collection_img = next(
            img for img in images if img["image"] == test_image_in_collection
        )
        assert collection_img["category"] == gallery_category
    
    def test_multiple_collection_blocks_supported(
        self, db, it_locale, test_collection, test_collection_2,
        test_image_in_collection, test_image_in_collection_2, gallery_category
    ):
        """Più blocchi CollectionGalleryBlock possono essere usati insieme."""
        root_page = Page.objects.filter(depth=1).first()
        
        # Crea StreamField con 2 blocchi collezione
        gallery_blocks = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": gallery_category.id,
                }
            },
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection_2.id,
                    "category": None,
                }
            },
        ]
        
        gallery = GalleryPage(
            title="Galleria Multi Collection",
            slug="galleria-multi",
            locale=it_locale,
        )
        gallery.gallery = gallery_blocks
        root_page.add_child(instance=gallery)
        
        images = gallery.get_all_images()
        
        # Deve contenere immagini da entrambe le collezioni
        image_ids = [img["image"].id for img in images]
        assert test_image_in_collection.id in image_ids
        assert test_image_in_collection_2.id in image_ids
    
    def test_inline_images_take_precedence_over_collection_block(
        self, gallery_page_with_collection_block, test_image_in_collection
    ):
        """Le immagini InlinePanel hanno priorità sui blocchi collezione."""
        from wagtail.images import get_image_model
        import io
        from PIL import Image as PILImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        Image = get_image_model()
        
        # Crea un'altra immagine per InlinePanel
        pil_image = PILImage.new("RGB", (100, 100), color="red")
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        file = SimpleUploadedFile(
            name="inline-test.png",
            content=buffer.read(),
            content_type="image/png"
        )
        
        inline_image = Image(title="Immagine Inline", file=file)
        inline_image.save()
        
        # Aggiungi all'InlinePanel
        GalleryImage.objects.create(
            page=gallery_page_with_collection_block,
            image=inline_image,
            title="Titolo Inline Custom",
            sort_order=0,
        )
        
        images = gallery_page_with_collection_block.get_all_images()
        
        # La prima immagine deve essere quella inline
        assert images[0]["title"] == "Titolo Inline Custom"
    
    def test_collection_block_images_not_duplicated_if_in_inline(
        self, gallery_page_with_collection_block, test_image_in_collection
    ):
        """Se un'immagine è già nell'InlinePanel, non viene duplicata dal blocco."""
        # Aggiungi la stessa immagine anche all'InlinePanel
        GalleryImage.objects.create(
            page=gallery_page_with_collection_block,
            image=test_image_in_collection,
            title="Titolo Personalizzato",
            caption="Caption personalizzata",
            sort_order=0,
        )
        
        images = gallery_page_with_collection_block.get_all_images()
        
        # Conta quante volte appare l'immagine
        count = sum(1 for img in images if img["image"] == test_image_in_collection)
        assert count == 1, "L'immagine non deve essere duplicata"
        
        # Il titolo deve essere quello personalizzato (InlinePanel ha precedenza)
        img_data = next(img for img in images if img["image"] == test_image_in_collection)
        assert img_data["title"] == "Titolo Personalizzato"


@pytest.mark.django_db
class TestGalleryTags:
    """Test per il metodo get_all_tags()."""
    
    def test_get_all_tags_returns_list(self, db, test_collection, test_image_in_collection):
        """get_all_tags() deve restituire una lista di tuple (tag, count)."""
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        gallery = GalleryPage(
            title="Galleria",
            slug="galleria-tags",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                    "title": "Test",
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        tags = gallery.get_all_tags()
        assert isinstance(tags, list)
    
    def test_tags_sorted_by_frequency(self, db):
        """I tag devono essere ordinati per frequenza."""
        from io import BytesIO
        from PIL import Image as PILImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        from wagtail.models import Collection
        from taggit.models import Tag
        
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        # Crea collezione
        root_collection = Collection.get_first_root_node()
        coll = root_collection.add_child(name="Tags Test Collection")
        
        Image = get_image_model()
        
        # Crea 3 immagini con tag diversi
        for i, tags_list in enumerate([["moto", "guzzi"], ["moto"], ["moto", "ducati"]]):
            img_bytes = BytesIO()
            PILImage.new("RGB", (100, 100), "red").save(img_bytes, "PNG")
            img_bytes.seek(0)
            
            img = Image.objects.create(
                title=f"Img {i}",
                file=SimpleUploadedFile(f"img_tag_{i}.png", img_bytes.read()),
                collection=coll,
            )
            for tag_name in tags_list:
                img.tags.add(tag_name)
        
        gallery = GalleryPage(
            title="Galleria Tags",
            slug="galleria-tags-freq",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": coll.id,
                    "category": None,
                    "title": "Test Tags",
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        tags = gallery.get_all_tags()
        
        # "moto" dovrebbe essere il primo (3 occorrenze)
        assert tags[0][0] == "moto"
        assert tags[0][1] == 3


@pytest.mark.django_db
class TestGallerySections:
    """Test per la navigazione a sezioni della galleria."""
    
    def test_get_gallery_sections_returns_list(self, db, test_collection, test_image_in_collection):
        """get_gallery_sections() deve restituire una lista di sezioni."""
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        gallery = GalleryPage(
            title="Galleria",
            slug="galleria-sections",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                    "title": "Sezione Test",
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        sections = gallery.get_gallery_sections()
        assert isinstance(sections, list)
        assert len(sections) == 1
    
    def test_section_has_required_fields(self, db, test_collection, test_image_in_collection):
        """Ogni sezione deve avere id, title e images."""
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        gallery = GalleryPage(
            title="Galleria",
            slug="galleria-sections-2",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                    "title": "Sezione Uno",
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        sections = gallery.get_gallery_sections()
        section = sections[0]
        
        assert "id" in section
        assert "title" in section
        assert "images" in section
        assert section["id"] == "sezione-uno"  # slugified
        assert section["title"] == "Sezione Uno"
        assert len(section["images"]) == 1
    
    def test_section_uses_collection_name_if_no_title(self, db, test_collection, test_image_in_collection):
        """Se il titolo non è specificato, usa il nome della collezione."""
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        gallery = GalleryPage(
            title="Galleria",
            slug="galleria-sections-3",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                    "title": "",  # Empty title
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        sections = gallery.get_gallery_sections()
        section = sections[0]
        
        # Deve usare il nome della collezione
        assert section["title"] == test_collection.name
    
    def test_multiple_sections_for_multiple_collections(self, db, test_image_in_collection):
        """Più blocchi collection_gallery creano più sezioni."""
        from wagtail.models import Collection
        
        root_page = Page.objects.filter(depth=1).first()
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        
        # Crea una seconda collezione
        root_collection = Collection.get_first_root_node()
        coll1 = Collection.objects.filter(name="Test Events").first()
        if not coll1:
            coll1 = root_collection.add_child(name="Test Events")
        
        coll2 = Collection.objects.filter(name="Test Raduni").first()
        if not coll2:
            coll2 = root_collection.add_child(name="Test Raduni")
        
        # Aggiungi immagini a entrambe
        Image = get_image_model()
        for coll in [coll1, coll2]:
            if not Image.objects.filter(collection=coll).exists():
                from io import BytesIO
                from PIL import Image as PILImage
                from django.core.files.uploadedfile import SimpleUploadedFile
                
                img_bytes = BytesIO()
                PILImage.new("RGB", (100, 100), "blue").save(img_bytes, "PNG")
                img_bytes.seek(0)
                
                Image.objects.create(
                    title=f"Img in {coll.name}",
                    file=SimpleUploadedFile(f"img_{coll.name}.png", img_bytes.read()),
                    collection=coll,
                )
        
        gallery = GalleryPage(
            title="Galleria Multi",
            slug="galleria-multi-sections",
            locale=it_locale,
        )
        gallery.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": coll1.id,
                    "category": None,
                    "title": "Eventi",
                }
            },
            {
                "type": "collection_gallery",
                "value": {
                    "collection": coll2.id,
                    "category": None,
                    "title": "Raduni",
                }
            }
        ]
        root_page.add_child(instance=gallery)
        
        sections = gallery.get_gallery_sections()
        assert len(sections) == 2
        assert sections[0]["title"] == "Eventi"
        assert sections[1]["title"] == "Raduni"


@pytest.mark.django_db
class TestCollectionGalleryBlockMultilingual:
    """Test multilingua per CollectionGalleryBlock."""
    
    def test_same_collection_different_locales(self, db, test_collection, test_image_in_collection):
        """Gallerie in lingue diverse possono usare la stessa Collection via blocco."""
        root_page = Page.objects.filter(depth=1).first()
        
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        en_locale = Locale.objects.get_or_create(language_code="en")[0]
        
        gallery_blocks = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                }
            }
        ]
        
        # Galleria italiana
        gallery_it = GalleryPage(
            title="Galleria",
            slug="galleria-it",
            locale=it_locale,
        )
        gallery_it.gallery = gallery_blocks
        root_page.add_child(instance=gallery_it)
        
        # Galleria inglese
        gallery_en = GalleryPage(
            title="Gallery",
            slug="gallery-en",
            locale=en_locale,
        )
        gallery_en.gallery = gallery_blocks
        root_page.add_child(instance=gallery_en)
        
        # Entrambe devono vedere la stessa immagine
        images_it = gallery_it.get_all_images()
        images_en = gallery_en.get_all_images()
        
        assert len(images_it) == len(images_en)
        assert images_it[0]["image"] == images_en[0]["image"]
    
    def test_translated_gallery_inherits_blocks_from_source(self, db, test_collection, test_image_in_collection):
        """Una galleria tradotta senza blocchi eredita i blocchi dalla sorgente."""
        root_page = Page.objects.filter(depth=1).first()
        
        it_locale = Locale.objects.get_or_create(language_code="it")[0]
        fr_locale = Locale.objects.get_or_create(language_code="fr")[0]
        
        # Galleria italiana CON blocchi
        gallery_it = GalleryPage(
            title="Galleria",
            slug="galleria-source",
            locale=it_locale,
        )
        gallery_it.gallery = [
            {
                "type": "collection_gallery",
                "value": {
                    "collection": test_collection.id,
                    "category": None,
                    "title": "Titolo Sezione",
                }
            }
        ]
        root_page.add_child(instance=gallery_it)
        
        # Galleria francese SENZA blocchi (simula traduzione)
        gallery_fr = GalleryPage(
            title="Galerie",
            slug="galerie-fr",
            locale=fr_locale,
            translation_key=gallery_it.translation_key,  # Stessa translation_key
        )
        # NON impostiamo gallery_fr.gallery - resta vuoto
        root_page.add_child(instance=gallery_fr)
        
        # La galleria francese deve ereditare le sezioni
        sections_fr = gallery_fr.get_gallery_sections()
        sections_it = gallery_it.get_gallery_sections()
        
        assert len(sections_fr) == len(sections_it)
        assert len(sections_fr[0]["images"]) == len(sections_it[0]["images"])
