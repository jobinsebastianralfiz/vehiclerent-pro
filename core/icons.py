"""The Material Symbols icons the public site uses, so base.html can load just those glyphs instead of the
whole 1 MB icon font (Google Fonts `icon_names=`; names that aren't icons are ignored, so erring wide is safe).

Static names are scanned from the public templates and the view modules once per process; icons stored in the
database (vehicle categories, booking add-ons) are added per request. Admin pages keep the full font: they have
an icon picker.
"""
import re
from functools import lru_cache
from pathlib import Path

from django.conf import settings

ICON_FONT = "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@300..600,0..1"
NAME = r"[a-z][a-z0-9_]{1,40}"
_SPAN_TEXT = re.compile(r'material-symbols-outlined[^>]*>\s*(' + NAME + r')\s*<')
_ICON_ARG = re.compile(r'\bicon\s*=\s*["\'](' + NAME + r')["\']')
_DEFAULT = re.compile(r'default:\s*["\'](' + NAME + r')["\']')
_CYCLE = re.compile(r'{%\s*cycle\s+([^%]+)%}')
_QUOTED = re.compile(r'["\'](' + NAME + r')["\']')
_TEXTCONTENT = re.compile(r'textContent\s*=\s*["\'`](' + NAME + r')["\'`]')
# an <span class="material-symbols-outlined" x-text="cond ? 'a' : 'b'"> swaps its icon in the browser
_XTEXT = re.compile(r'material-symbols-outlined[^>]*x-text="([^"]+)"|x-text="([^"]+)"[^>]*material-symbols-outlined')
# icon lists in the views: ("icon_name", "Label", ...) tuples and {"icon": "name"} dicts
_PY_TUPLE = re.compile(r'\(\s*(?:reverse\([^)]*\),\s*)?"(' + NAME + r')",\s*"[A-Z]')
_PY_DICT = re.compile(r'"icon":\s*"(' + NAME + r')"')
FALLBACK = {"directions_car", "category", "interests", "add_circle", "check_circle", "arrow_forward", "arrow_back",
            "close", "menu", "favorite", "keyboard_arrow_up", "expand_more", "chat", "call", "search"}


@lru_cache(maxsize=1)
def static_icons():
    names = set(FALLBACK)
    root = Path(settings.BASE_DIR) / "templates"
    for f in root.rglob("*.html"):
        if "manage" in f.parts:
            continue
        text = f.read_text(errors="ignore")
        names.update(_SPAN_TEXT.findall(text))
        names.update(_ICON_ARG.findall(text))
        names.update(_TEXTCONTENT.findall(text))
        for m in _DEFAULT.findall(text):
            names.add(m)
        for args in _CYCLE.findall(text):
            names.update(_QUOTED.findall(args))
        for a, b in _XTEXT.findall(text):
            names.update(_QUOTED.findall(a or b))
    for mod in ("core/views.py", "vehicles/views.py", "core/context_processors.py", "core/chatbot.py"):
        p = Path(settings.BASE_DIR) / mod
        if p.exists():
            text = p.read_text(errors="ignore")
            names.update(_PY_TUPLE.findall(text))
            names.update(_PY_DICT.findall(text))
    return frozenset(names)


def icon_font_url():
    """The icon font stylesheet for public pages: only the glyphs the site can show."""
    from vehicles.models import BookingAddon, VehicleCategory
    names = set(static_icons())
    names.update(i for i in VehicleCategory.objects.exclude(icon="").values_list("icon", flat=True) if re.fullmatch(NAME, i))
    names.update(i for i in BookingAddon.objects.exclude(icon="").values_list("icon", flat=True) if re.fullmatch(NAME, i))
    return f"{ICON_FONT}&icon_names={','.join(sorted(names))}&display=block"
