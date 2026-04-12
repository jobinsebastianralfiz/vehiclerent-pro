from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def whatsapp_url(number=None):
    num = number or settings.WHATSAPP_NUMBER
    msg = quote(settings.WHATSAPP_DEFAULT_MESSAGE)
    return f"https://wa.me/{num}?text={msg}"


@register.simple_tag
def whatsapp_vehicle_url(vehicle, number=None):
    num = number or settings.WHATSAPP_NUMBER
    msg = quote(
        f"Hi! I'm interested in renting the *{vehicle.name}* "
        f"({vehicle.get_vehicle_type_display()}) "
        f"at \u20b9{vehicle.price_per_day}/day. "
        f"Could you share availability and booking details?"
    )
    return f"https://wa.me/{num}?text={msg}"


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
    "rented": ("bg-blue-100 text-blue-800", "Rented"),
    "maintenance": ("bg-amber-100 text-amber-800", "Maintenance"),
    "reserved": ("bg-purple-100 text-purple-800", "Reserved"),
    "inactive": ("bg-stone-100 text-stone-500", "Inactive"),
    "active": ("bg-green-100 text-green-800", "Active"),
    "completed": ("bg-stone-100 text-stone-600", "Completed"),
    "cancelled": ("bg-red-100 text-red-800", "Cancelled"),
    "new": ("bg-blue-100 text-blue-800", "New"),
    "contacted": ("bg-amber-100 text-amber-800", "Contacted"),
    "follow_up": ("bg-purple-100 text-purple-800", "Follow Up"),
    "converted": ("bg-green-100 text-green-800", "Converted"),
    "closed": ("bg-stone-100 text-stone-500", "Closed"),
    "website": ("bg-blue-100 text-blue-800", "Website"),
    "whatsapp": ("bg-green-100 text-green-800", "WhatsApp"),
    "phone": ("bg-amber-100 text-amber-800", "Phone"),
    "walkin": ("bg-purple-100 text-purple-800", "Walk-in"),
}


@register.inclusion_tag("manage/includes/status_badge.html")
def status_badge(status):
    css_class, label = STATUS_COLORS.get(status, ("bg-stone-100 text-stone-600", status))
    return {"css_class": css_class, "label": label}
