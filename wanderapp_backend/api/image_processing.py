# api/image_processing.py
from PIL import Image, ImageOps, ImageCms
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Photo
import os

def process_and_save_photo(uploaded_file, stage, user):
    original_filename = uploaded_file.name

    # Bild laden
    img = Image.open(uploaded_file)

    # EXIF-orientiert physisch drehen
    img = ImageOps.exif_transpose(img)

    # Farbraum auf sRGB normalisieren (falls Profil vorhanden)
    icc = img.info.get("icc_profile")
    if icc:
        try:
            srgb = ImageCms.createProfile("sRGB")
            src = ImageCms.ImageCmsProfile(BytesIO(icc))
            img = ImageCms.profileToProfile(img, src, srgb, outputMode="RGB")
            icc = None  # Profil nach Konvertierung meist nicht mehr nötig
        except Exception:
            pass

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Korrekte Dimensionen (nach Rotation!)
    correct_width, correct_height = img.size

    # Photo-Objekt anlegen
    photo = Photo.objects.create(
        stage=stage,
        creator=user,
        original_width=correct_width,
        original_height=correct_height,
    )

    base, _ext = os.path.splitext(original_filename)
    # 1) "Original" als normalisierte JPEG-Version speichern (keine EXIF-Orientierung mehr)
    buf_norm = BytesIO()
    img.save(
        buf_norm,
        format="JPEG",
        quality=90,
        optimize=True,
        progressive=True,
        icc_profile=icc if icc else None
    )
    photo.original.save(f"{base}.jpg", ContentFile(buf_norm.getvalue()), save=False)

    # 2) Derivate
    DERIVATIVES = {
        "display": (1280, 1280),
        "thumbnail": (640, 640),
    }

    for name, size in DERIVATIVES.items():
        im2 = img.copy()
        im2.thumbnail(size, Image.Resampling.LANCZOS)

        # JPEG
        b_jpg = BytesIO()
        im2.save(b_jpg, format="JPEG", quality=85, optimize=True, progressive=True)
        getattr(photo, name).save(f"{base}_{name}.jpg", ContentFile(b_jpg.getvalue()), save=False)

        # WebP
        b_webp = BytesIO()
        im2.save(b_webp, format="WEBP", quality=85, method=6)
        getattr(photo, f"{name}_webp").save(f"{base}_{name}.webp", ContentFile(b_webp.getvalue()), save=False)

    photo.save()
    return photo
