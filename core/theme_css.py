"""Colour tokens for the pre-built Tailwind stylesheet (static/css/site.css).

Tailwind is compiled ahead of time (see tailwind.config.js and `make css`), with every theme colour pointing at a
CSS variable: `bg-primary` is `rgb(var(--c-primary) / <alpha>)`. base.html prints the variables for the active
theme, so one stylesheet serves all five themes. Admin pages remap Tailwind's blue scale to the brand green.
"""
from functools import lru_cache

# The editorial palette (the default); themes override some of these in core/themes.py
DEFAULT_COLORS = {
    "surface": "#fbfaf1", "surface-dim": "#dbdad2", "surface-bright": "#fbfaf1",
    "surface-container-lowest": "#ffffff", "surface-container-low": "#f5f4eb", "surface-container": "#efeee6",
    "surface-container-high": "#e9e8e0", "surface-container-highest": "#e4e3da", "surface-variant": "#e4e3da",
    "surface-tint": "#51652a", "background": "#fbfaf1",
    "on-surface": "#1b1c17", "on-surface-variant": "#45483c", "on-background": "#1b1c17",
    "inverse-surface": "#30312b", "inverse-on-surface": "#f2f1e8",
    "outline": "#75786b", "outline-variant": "#c5c8b8",
    "primary": "#1f2e00", "primary-container": "#33450d", "on-primary": "#ffffff", "on-primary-container": "#9cb36f",
    "primary-fixed": "#d4eca2", "primary-fixed-dim": "#b8cf88", "on-primary-fixed": "#141f00",
    "on-primary-fixed-variant": "#3a4d14", "inverse-primary": "#b8cf88",
    "secondary": "#52652a", "secondary-container": "#d4eca2", "on-secondary": "#ffffff", "on-secondary-container": "#576b2f",
    "secondary-fixed": "#d4eca2", "secondary-fixed-dim": "#b8cf88", "on-secondary-fixed": "#141f00",
    "on-secondary-fixed-variant": "#3b4d14",
    "tertiary": "#421941", "tertiary-container": "#5b2f58", "on-tertiary": "#ffffff", "on-tertiary-container": "#d199c9",
    "tertiary-fixed": "#ffd7f6", "tertiary-fixed-dim": "#efb4e6", "on-tertiary-fixed": "#320a32",
    "on-tertiary-fixed-variant": "#643760",
    "error": "#ba1a1a", "on-error": "#ffffff", "error-container": "#ffdad6", "on-error-container": "#93000a",
}

# Tailwind's own blue (public pages) and the brand-green stand-in the admin uses for it
BLUE = {"50": "#eff6ff", "100": "#dbeafe", "200": "#bfdbfe", "300": "#93c5fd", "400": "#60a5fa", "500": "#3b82f6",
        "600": "#2563eb", "700": "#1d4ed8", "800": "#1e40af", "900": "#1e3a8a", "950": "#172554"}
ADMIN_BLUE = {"50": "#ecf7f0", "100": "#d3eedd", "200": "#a8dcbb", "300": "#74c495", "400": "#3fa56d", "500": "#1f8a52",
              "600": "#145c38", "700": "#0f4a2d", "800": "#0c3a24", "900": "#0a2e1d", "950": "#061c12"}


def color_names():
    """Every colour token any theme uses, for tailwind.config.js."""
    from .themes import THEMES
    names = list(DEFAULT_COLORS)
    for t in THEMES.values():
        names += [k for k in t["colors"] if k not in names]
    return names


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return f"{int(h[0:2], 16)} {int(h[2:4], 16)} {int(h[4:6], 16)}"


@lru_cache(maxsize=32)
def _vars(theme_key, admin):
    from .themes import THEMES
    colors = dict(DEFAULT_COLORS)
    if not admin and theme_key in THEMES:
        colors.update(THEMES[theme_key]["colors"])
    out = [f"--c-{k}:{_rgb(v)}" for k, v in colors.items()]
    out += [f"--c-blue-{k}:{_rgb(v)}" for k, v in (ADMIN_BLUE if admin else BLUE).items()]
    return ":root{" + ";".join(out) + "}"


def css_vars(theme_key, admin=False):
    """The :root block of colour variables for a page."""
    return _vars(theme_key, admin)
