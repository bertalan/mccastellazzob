"""
MC Castellazzo - Image Optimizer
================================
Ottimizzazione automatica immagini per bulk upload.

Funzionalità:
- Ridimensionamento a max 1280px (lato lungo)
- Conversione in WebP con qualità 85%
- Generazione nomi file puliti con numeri sequenziali
"""

import io
import re
from unicodedata import normalize

from PIL import Image


# Configurazioni
MAX_DIMENSION = 1280
WEBP_QUALITY = 85
MAX_FILENAME_LENGTH = 100


def optimize_image(image_buffer: io.BytesIO) -> io.BytesIO:
    """
    Ottimizza un'immagine ridimensionando e convertendo in WebP.
    
    Args:
        image_buffer: Buffer contenente l'immagine originale
        
    Returns:
        Buffer contenente l'immagine ottimizzata in formato WebP
    """
    # Apri l'immagine
    image_buffer.seek(0)
    img = Image.open(image_buffer)
    
    # Converti in RGB se necessario (per PNG con trasparenza, RGBA)
    if img.mode in ("RGBA", "P"):
        # Crea sfondo bianco per trasparenza
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")
    
    # Calcola nuove dimensioni mantenendo l'aspect ratio
    original_width, original_height = img.size
    
    if original_width > MAX_DIMENSION or original_height > MAX_DIMENSION:
        # Trova il lato più lungo
        if original_width >= original_height:
            # Landscape: larghezza è il lato più lungo
            new_width = MAX_DIMENSION
            new_height = int(original_height * (MAX_DIMENSION / original_width))
        else:
            # Portrait: altezza è il lato più lungo
            new_height = MAX_DIMENSION
            new_width = int(original_width * (MAX_DIMENSION / original_height))
        
        # Ridimensiona con antialiasing di alta qualità
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Salva in WebP
    output_buffer = io.BytesIO()
    img.save(output_buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
    output_buffer.seek(0)
    
    return output_buffer


def slugify_title(title: str) -> str:
    """
    Converte un titolo in slug URL-safe.
    
    Args:
        title: Titolo da convertire
        
    Returns:
        Slug minuscolo e URL-safe
    """
    # Normalizza caratteri Unicode (es. è -> e)
    title = normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    
    # Converti in minuscolo
    title = title.lower()
    
    # Sostituisci spazi e caratteri speciali con trattini
    title = re.sub(r"[^a-z0-9]+", "-", title)
    
    # Rimuovi trattini iniziali e finali
    title = title.strip("-")
    
    # Rimuovi trattini multipli
    title = re.sub(r"-+", "-", title)
    
    return title


def generate_filename(title_prefix: str, sequence_number: int) -> str:
    """
    Genera un nome file secondo il pattern: prefisso-000.webp
    
    Args:
        title_prefix: Prefisso del titolo (es. "Raduno Madonnina 2026")
        sequence_number: Numero sequenziale (0-based)
        
    Returns:
        Nome file completo (es. "raduno-madonnina-2026-000.webp")
    """
    # Crea slug dal titolo
    slug = slugify_title(title_prefix)
    
    # Tronca se troppo lungo (lascia spazio per -000.webp = 9 caratteri)
    max_prefix_length = MAX_FILENAME_LENGTH - 9
    if len(slug) > max_prefix_length:
        slug = slug[:max_prefix_length].rstrip("-")
    
    # Formatta numero con zero-padding a 3 cifre
    number_str = f"{sequence_number:03d}"
    
    # Componi nome file
    filename = f"{slug}-{number_str}.webp"
    
    return filename


def get_optimized_image_with_filename(
    image_buffer: io.BytesIO,
    title_prefix: str,
    sequence_number: int
) -> tuple[io.BytesIO, str]:
    """
    Ottimizza un'immagine e genera il nome file.
    
    Args:
        image_buffer: Buffer con l'immagine originale
        title_prefix: Prefisso per il nome file
        sequence_number: Numero sequenziale
        
    Returns:
        Tuple con (buffer ottimizzato, nome file)
    """
    optimized = optimize_image(image_buffer)
    filename = generate_filename(title_prefix, sequence_number)
    
    return optimized, filename
