from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


def _get_whatsapp_config():
    """Get WhatsApp number and message from SiteConfig, falling back to settings."""
    from core.models import SiteConfig
    try:
        config = SiteConfig.load()
        number = config.whatsapp_number or settings.WHATSAPP_NUMBER
        message = config.whatsapp_default_message or settings.WHATSAPP_DEFAULT_MESSAGE
    except Exception:
        number = settings.WHATSAPP_NUMBER
        message = settings.WHATSAPP_DEFAULT_MESSAGE
    return number, message


@register.simple_tag
def whatsapp_url(message=None, number=None):
    wa_number, wa_message = _get_whatsapp_config()
    num = number or wa_number
    msg = quote(message or wa_message)
    return f"https://wa.me/{num}?text={msg}"


@register.simple_tag
def whatsapp_vehicle_url(vehicle, number=None):
    wa_number, _ = _get_whatsapp_config()
    num = number or wa_number
    msg = quote(
        f"Hi! I'm interested in renting the *{vehicle.name}* "
        f"({vehicle.get_vehicle_type_display()}) "
        f"at \u20b9{vehicle.price_per_day}/day. "
        f"Could you share availability and booking details?"
    )
    return f"https://wa.me/{num}?text={msg}"


@register.filter
def lines(text):
    """Non-empty lines of a text field, stripped."""
    return [s.strip() for s in str(text or "").splitlines() if s.strip()]


@register.filter
def inr(value):
    """Format number as Indian currency: 1,23,456"""
    if value is None:
        return ""
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        return value
    if value < 0:
        return f"-\u20b9{inr(-value)}"
    s = str(value)
    if len(s) <= 3:
        return f"\u20b9{s}"
    last3 = s[-3:]
    remaining = s[:-3]
    groups = []
    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    return f"\u20b9{','.join(groups)},{last3}"


STATUS_COLORS = {
    "available": ("bg-green-100 text-green-800", "Available"),
    "rented": ("bg-sky-100 text-sky-800", "Rented"),
    "maintenance": ("bg-amber-100 text-amber-800", "Maintenance"),
    "reserved": ("bg-purple-100 text-purple-800", "Reserved"),
    "inactive": ("bg-stone-100 text-stone-500", "Inactive"),
    "active": ("bg-green-100 text-green-800", "Active"),
    "completed": ("bg-stone-100 text-stone-600", "Completed"),
    "cancelled": ("bg-red-100 text-red-800", "Cancelled"),
    "new": ("bg-sky-100 text-sky-800", "New"),
    "contacted": ("bg-amber-100 text-amber-800", "Contacted"),
    "follow_up": ("bg-purple-100 text-purple-800", "Follow Up"),
    "converted": ("bg-green-100 text-green-800", "Converted"),
    "closed": ("bg-stone-100 text-stone-500", "Closed"),
    "website": ("bg-sky-100 text-sky-800", "Website"),
    "whatsapp": ("bg-green-100 text-green-800", "WhatsApp"),
    "phone": ("bg-amber-100 text-amber-800", "Phone"),
    "walkin": ("bg-purple-100 text-purple-800", "Walk-in"),
}


@register.inclusion_tag("manage/includes/status_badge.html")
def status_badge(status):
    css_class, label = STATUS_COLORS.get(status, ("bg-stone-100 text-stone-600", status))
    return {"css_class": css_class, "label": label}


@register.filter
def match_any(needles, haystack):
    """True if any of the substrings in needles occurs in haystack (admin nav highlighting)."""
    haystack = haystack or ""
    return any(n in haystack for n in needles)


@register.simple_tag
def sparkline(values, color="#1f8a52", width=120, height=40):
    """Inline SVG area sparkline for a list of numbers (dashboard stat cards)."""
    from django.utils.html import format_html
    vals = [float(v) for v in values] or [0.0]
    if len(vals) == 1:
        vals = vals * 2
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    step = width / (len(vals) - 1)
    pts = [(i * step, height - 4 - (v - lo) / span * (height - 10)) for i, v in enumerate(vals)]
    if hi == lo:
        pts = [(x, height - 6) for x, _ in pts]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,{height} " + line + f" {width},{height}"
    gid = "sg" + color.strip("#")
    return format_html(
        '<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" class="block" aria-hidden="true" preserveAspectRatio="none">'
        '<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity=".22"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient></defs>'
        '<polygon points="{a}" fill="url(#{g})"/><polyline points="{l}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        w=width, h=height, g=gid, c=color, a=area, l=line,
    )


@register.filter
def accent(text, css="r-accent"):
    """Colours the words wrapped in *asterisks*: "Rent Your *Perfect* Vehicle"."""
    import re
    from django.utils.html import escape
    from django.utils.safestring import mark_safe
    return mark_safe(re.sub(r"\*([^*]+)\*", lambda m: f'<span class="{css}">{m.group(1)}</span>', escape(text or "")))
