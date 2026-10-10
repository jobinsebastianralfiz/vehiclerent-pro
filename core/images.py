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
