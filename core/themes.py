"""Public-site themes. The admin picks one in Site Settings (SiteConfig.theme).

Each theme can override any public page, navbar or footer by putting a
template of the same name in templates/public/themes/<key>/; pages it does not
override fall back to templates/public/ and take the theme's colour tokens and
fonts, which base.html feeds into the Tailwind config.
"""

DEFAULT_THEME = "editorial"

_SERIF_FONTS = "family=Noto+Serif:ital,wght@0,400;0,700;1,400;1,700&family=Manrope:wght@300;400;500;600;700;800"

THEMES = {
    "editorial": {
        "label": "Editorial",
        "description": "Cream and olive, editorial serif type. Rolling headlines, dealt cards, a pinned luxury slider.",
        "fonts": _SERIF_FONTS,
        "font_display": "Noto Serif",
        "font_body": "Manrope",
        "dark": False,
        "colors": {},  # base.html defaults are the editorial palette
    },
    "night": {
        "label": "Night Drive",
        "description": "Dark and cinematic. A headlight beam reveals the car, a scroll-driven drive-by, lime edge-lit cards.",
        "fonts": _SERIF_FONTS,
        "font_display": "Noto Serif",
        "font_body": "Manrope",
        "dark": True,
        "colors": {
            "surface": "#0d0f0a", "surface-bright": "#0d0f0a", "background": "#0d0f0a", "surface-dim": "#080906",
            "surface-container-lowest": "#11140c", "surface-container-low": "#151910", "surface-container": "#1a1f14",
            "surface-container-high": "#212719", "surface-container-highest": "#283020", "surface-variant": "#283020",
            "on-surface": "#eef0e4", "on-background": "#eef0e4", "on-surface-variant": "#b4b8a5",
            "outline": "#8a8f7a", "outline-variant": "#3a4030",
            "inverse-surface": "#eef0e4", "inverse-on-surface": "#1b1c17",
            "primary": "#d4eca2", "on-primary": "#141f00", "primary-container": "#b8cf88", "on-primary-container": "#1f2e00",
            "primary-fixed": "#33450d", "primary-fixed-dim": "#3a4d14", "on-primary-fixed": "#d4eca2",
            "secondary": "#b8cf88", "secondary-container": "#33450d", "on-secondary-container": "#d4eca2",
        },
    },
    "route": {
        "label": "Kerala Route",
        "description": "Warm golden-hour palette. A road draws itself down the page, fleet as boarding-pass tickets.",
        "fonts": _SERIF_FONTS,
        "font_display": "Noto Serif",
        "font_body": "Manrope",
        "dark": False,
        "colors": {
            "surface": "#f7f0e3", "surface-bright": "#f7f0e3", "background": "#f7f0e3",
            "surface-container-lowest": "#fffaf0", "surface-container-low": "#f3e9d6", "surface-container": "#efe3cb",
            "surface-container-high": "#e9dcc0", "surface-container-highest": "#e3d4b5", "surface-variant": "#e3d4b5",
            "on-surface-variant": "#4a4a3e", "outline": "#7b7766", "outline-variant": "#d6ccb5",
            "tertiary": "#134e4a", "tertiary-container": "#cfe3dc",
        },
    },
    "reels": {
        "label": "Showroom Reels",
        "description": "Closest to the AGC design. Light showroom, colour tiles, slot-machine type, cards that shuffle.",
        "fonts": "family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Figtree:wght@300;400;500;600;700&family=Space+Mono:wght@400;700",
        "font_display": "Bricolage Grotesque",
        "font_body": "Figtree",
        "dark": False,
        "colors": {
            "surface": "#f6f7f1", "surface-bright": "#f6f7f1", "background": "#f6f7f1",
            "surface-container-low": "#eef0e7", "surface-container": "#e8eadf", "surface-container-high": "#e1e4d6",
            "surface-container-highest": "#dadecd", "surface-variant": "#dadecd",
        },
    },
    "bento": {
        "label": "Bento Concierge",
        "description": "App-like bento grid, frosted tiles, a live rental estimator and a phone that walks through booking.",
        "fonts": _SERIF_FONTS,
        "font_display": "Manrope",
        "font_body": "Manrope",
        "dark": False,
        "colors": {
            "surface": "#f7f7f2", "surface-bright": "#f7f7f2", "background": "#f7f7f2",
            "surface-container-low": "#f1f1ea", "surface-container": "#ebebe3", "surface-container-high": "#e4e4db",
            "surface-container-highest": "#dedfd4", "surface-variant": "#dedfd4",
        },
    },
}

THEME_CHOICES = [(key, t["label"]) for key, t in THEMES.items()]


def get_theme(key):
    """Return the theme dict (with its key) for key, falling back to the default."""
    key = key if key in THEMES else DEFAULT_THEME
    t = THEMES[key]
    return {"key": key, "page_bg": t["colors"].get("surface", "#fbfaf1"), "page_fg": t["colors"].get("on-surface", "#1b1c17"), **t}


def active_theme(request, config):
    """The saved theme, or the one a logged-in admin is previewing (?theme=<key>, ?theme=off to stop)."""
    saved = config.theme if config else None
    if request.user.is_authenticated and hasattr(request, "session"):
        wanted = request.GET.get("theme")
        if wanted in THEMES:
            request.session["theme_preview"] = wanted
        elif wanted is not None:
            request.session.pop("theme_preview", None)
        return get_theme(request.session.get("theme_preview") or saved)
    return get_theme(saved)


def themed(request, name):
    """Template candidates for a public page: the active theme's version first, then the shared one."""
    from .models import SiteConfig
    key = active_theme(request, SiteConfig.load())["key"]
    return [f"public/themes/{key}/{name}", f"public/{name}"]
