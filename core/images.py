"""Shrinks photos to web size when they are uploaded (and, via a command, ones already on the site).

Phone and AI-made photos arrive as multi-megabyte PNGs that load slowly; a 1920px JPEG looks the same
on screen. Images with transparency (cut-out category photos) stay PNG, just resized.
"""
import io
import os

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_PX = 1920
QUALITY = 84


def _has_alpha(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA").getextrema()[3][0] < 255
    return False


def shrunk(file, max_px=MAX_PX):
    """(new_name, ContentFile) for a smaller copy, or None when the file is already small enough."""
    try:
        file.seek(0)
        im = Image.open(file)
        im.load()
    except Exception:
        return None
    big = max(im.size) > max_px
    heavy = getattr(file, "size", 0) > 600 * 1024
    if not (big or heavy or im.format == "PNG"):
        return None
    im = ImageOps.exif_transpose(im)
    alpha = _has_alpha(im)
    if big:
        im.thumbnail((max_px, max_px), Image.LANCZOS)
    out = io.BytesIO()
    base = os.path.splitext(os.path.basename(file.name))[0]
    if alpha:
        im.save(out, "PNG", optimize=True)
        name = base + ".png"
    else:
        im.convert("RGB").save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        name = base + ".jpg"
    if not big and out.tell() >= getattr(file, "size", out.tell() + 1):
        return None  # not worth it
    return name, ContentFile(out.getvalue())


def shrink_uploads(instance, *fields):
    """Call from save(): replaces just-uploaded files in these ImageFields with web-size copies."""
    for name in fields:
        f = getattr(instance, name, None)
        if not f or getattr(f, "_committed", True):
            continue  # nothing new uploaded
        res = shrunk(f.file)
        if res:
            f.save(res[0], res[1], save=False)


SHARE_SIZE = (1200, 630)


def share_image(file):
    """(new_name, ContentFile) for a 1200x630 JPEG crop of the image: the size WhatsApp, Facebook and X preview best."""
    try:
        file.seek(0)
        im = ImageOps.exif_transpose(Image.open(file))
    except Exception:
        return None
    im = ImageOps.fit(im.convert("RGB"), SHARE_SIZE, Image.LANCZOS, centering=(0.5, 0.5))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return os.path.splitext(os.path.basename(file.name))[0] + "-share.jpg", ContentFile(out.getvalue())


# ──────────────── Responsive copies for the public site ────────────────
# Pages ask for a photo at the width they show it; a WebP copy is made the first time and kept under
# MEDIA_ROOT/cache/<width>/, then served like any other media file. The original upload is never changed.

CACHE_DIR = "cache"
WEBP_QUALITY = 78


def _source(file_or_url):
    """(relative media path, absolute path) of an ImageField file or a /media/... URL, else (None, None)."""
    from django.conf import settings
    name = getattr(file_or_url, "name", None)
    if not name and isinstance(file_or_url, str) and file_or_url.startswith(settings.MEDIA_URL):
        name = file_or_url[len(settings.MEDIA_URL):]
    if not name or name.startswith(CACHE_DIR + "/"):
        return None, None
    return name, os.path.join(settings.MEDIA_ROOT, name)


def resized_url(file_or_url, width):
    """URL of a WebP copy at most `width` px wide; the original URL if the file is missing or can't be read."""
    from django.conf import settings
    fallback = getattr(file_or_url, "url", file_or_url) if file_or_url else ""
    name, src = _source(file_or_url)
    if not name or not os.path.exists(src):
        return fallback
    rel = os.path.join(CACHE_DIR, str(width), os.path.splitext(name)[0] + ".webp")
    dst = os.path.join(settings.MEDIA_ROOT, rel)
    try:
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with Image.open(src) as im:
                im = ImageOps.exif_transpose(im)
                if im.width > width:
                    im.thumbnail((width, width * 10), Image.LANCZOS)
                keep_alpha = _has_alpha(im)
                im = im.convert("RGBA" if keep_alpha else "RGB")
                tmp = dst + ".tmp"
                im.save(tmp, "WEBP", quality=WEBP_QUALITY, method=4)
                os.replace(tmp, dst)  # atomic, so a half-written file is never served
    except Exception:
        return fallback
    return settings.MEDIA_URL + rel.replace(os.sep, "/")
