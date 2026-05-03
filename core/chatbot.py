"""Lightweight rule-based chatbot for car search.

Parses a natural-language message and returns matching vehicles from the DB.
No LLM — just keyword/regex extraction. Good enough for queries like:
    "automatic SUV under 3000"
    "wedding car in Kochi with driver"
    "Maruti petrol manual"
    "Show me electric cars"

Returns a dict {reply, vehicles, filters_applied}.
"""
from __future__ import annotations

import re
from decimal import Decimal

from django.db.models import Q

from vehicles.models import BookingAddon, City, Vehicle, VehicleCategory


# ── Keyword dictionaries ───────────────────────────────────────────────

BODY_TYPES = {
    "suv": "suv", "jeep": "suv", "crossover": "suv", "off-road": "suv", "offroad": "suv",
    "sedan": "car", "saloon": "car",
    "hatchback": "car", "hatch": "car", "compact": "car",
    "van": "van", "minivan": "van", "muv": "van",
    "bike": "bike", "motorcycle": "bike", "two-wheeler": "bike", "two wheeler": "bike",
    "scooter": "scooter",
    "truck": "truck", "pickup": "truck",
    "auto": "auto", "rickshaw": "auto",
    "bus": "bus",
}

FUEL_TYPES = {
    "petrol": "petrol", "gasoline": "petrol", "gas": "petrol",
    "diesel": "diesel",
    "electric": "electric", "ev": "electric", "battery": "electric",
    "hybrid": "hybrid",
    "cng": "cng",
}

TRANSMISSIONS = {
    "automatic": "automatic", "auto-gear": "automatic", "auto gear": "automatic",
    "amt": "amt",
    "manual": "manual", "stick shift": "manual", "stick-shift": "manual",
    "cvt": "cvt",
}

INTENT_PATTERNS = {
    "wedding": re.compile(r"\b(wedding|marriage|bride|groom|baraat|reception)\b", re.I),
    "premium": re.compile(r"\b(premium|luxury|luxurious|high[\s-]?end|elite|top[\s-]?tier)\b", re.I),
    "with_driver": re.compile(r"\b(with[\s-]?driver|chauffeur|chauffeured|chauffer|driver included|with a driver)\b", re.I),
    "self_drive": re.compile(r"\b(self[\s-]?drive|drive myself|without driver)\b", re.I),
    "airport": re.compile(r"\b(airport|flight|pickup from airport)\b", re.I),
    "outstation": re.compile(r"\b(outstation|inter[\s-]?state|kerala\s+to|outside kerala)\b", re.I),
    "monthly": re.compile(r"\b(monthly|per month|long[\s-]?term|subscription)\b", re.I),
    "greeting": re.compile(r"^\s*(hi|hello|hey|hai|hii|namaste|good\s+(morning|afternoon|evening))\b", re.I),
    "thanks": re.compile(r"\b(thanks|thank you|thx|ty)\b", re.I),
    "help": re.compile(r"\b(help|how|what can|menu|options)\b", re.I),
}

# ── Extractors ─────────────────────────────────────────────────────────


def _extract_price(text: str):
    """Pull a price ceiling from text. Handles 'under 2000', 'below 3k', '<5000', 'less than 1500'."""
    # Match "under/below/<= N", optionally with k suffix
    m = re.search(r"(?:under|below|less than|max(?:imum)?|<=?)\s*₹?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?", text, re.I)
    if m:
        amount = float(m.group(1))
        if m.group(2):
            amount *= 1000
        return Decimal(str(amount))
    # "around N" treated as ceiling +20%
    m = re.search(r"\b(?:around|about|approximately)\s+₹?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?", text, re.I)
    if m:
        amount = float(m.group(1))
        if m.group(2):
            amount *= 1000
        return Decimal(str(amount * 1.2))
    return None


def _extract_seats(text: str):
    m = re.search(r"\b(\d+)\s*(?:seater|seat|seats|adults?|people|persons?|pax)\b", text, re.I)
    if m:
        return int(m.group(1))
    return None


def _find_in_dict(text: str, mapping: dict):
    """Return the first dictionary value whose key appears in text."""
    lower = f" {text.lower()} "
    # Sort longer keys first so 'two wheeler' matches before 'two'
    for key in sorted(mapping.keys(), key=len, reverse=True):
        if f" {key} " in lower or lower.startswith(key + " ") or lower.endswith(" " + key):
            return mapping[key]
    return None


def _find_city(text: str):
    """Match any active City name (case-insensitive substring)."""
    lower = text.lower()
    for city in City.objects.filter(is_active=True):
        if city.name.lower() in lower:
            return city
    return None


def _find_brand(text: str):
    """Match any brand string used by published vehicles."""
    brands = (
        Vehicle.objects.filter(is_published=True)
        .values_list("brand", flat=True)
        .distinct()
    )
    lower = text.lower()
    for brand in brands:
        if brand and brand.lower() in lower:
            return brand
    return None


# ── Main entry point ───────────────────────────────────────────────────


def search(message: str, limit: int = 5) -> dict:
    """Parse `message` and return a chatbot response dict."""
    text = (message or "").strip()
    if not text:
        return _help_response()

    # Pure greetings / thanks / help — short-circuit
    if INTENT_PATTERNS["greeting"].search(text) and len(text.split()) <= 4:
        return {
            "reply": "Hi there! 👋 I can help you find a car. Try: \"automatic SUV in Kochi\", \"wedding car under 10000\", or \"Maruti petrol manual\".",
            "vehicles": [],
            "filters_applied": [],
            "intent": "greeting",
        }
    if INTENT_PATTERNS["thanks"].search(text) and len(text.split()) <= 5:
        return {
            "reply": "You're welcome! Anything else I can help you find?",
            "vehicles": [],
            "filters_applied": [],
            "intent": "thanks",
        }
    if INTENT_PATTERNS["help"].search(text) and len(text.split()) <= 6:
        return _help_response()

    # Extract everything we can
    body = _find_in_dict(text, BODY_TYPES)
    fuel = _find_in_dict(text, FUEL_TYPES)
    transmission = _find_in_dict(text, TRANSMISSIONS)
    price_ceiling = _extract_price(text)
    seats = _extract_seats(text)
    city = _find_city(text)
    brand = _find_brand(text)

    is_wedding = bool(INTENT_PATTERNS["wedding"].search(text))
    is_premium = bool(INTENT_PATTERNS["premium"].search(text))
    is_chauffeur = bool(INTENT_PATTERNS["with_driver"].search(text))
    is_outstation = bool(INTENT_PATTERNS["outstation"].search(text))
    is_monthly = bool(INTENT_PATTERNS["monthly"].search(text))

    # Build query
    qs = Vehicle.objects.filter(is_published=True).exclude(status="inactive").select_related("category")
    filters = []

    if body:
        qs = qs.filter(vehicle_type=body)
        filters.append(body.upper())
    if fuel:
        qs = qs.filter(fuel_type=fuel)
        filters.append(fuel.title())
    if transmission:
        qs = qs.filter(transmission=transmission)
        filters.append(transmission.title())
    if brand:
        qs = qs.filter(brand__iexact=brand)
        filters.append(brand)
    if seats:
        qs = qs.filter(seating_capacity__gte=seats)
        filters.append(f"{seats}+ seats")
    if price_ceiling:
        qs = qs.filter(price_per_day__lte=price_ceiling)
        filters.append(f"under ₹{int(price_ceiling)}")
    if city:
        qs = qs.filter(Q(available_cities=city) | Q(available_cities__isnull=True)).distinct()
        filters.append(f"in {city.name}")
    if is_wedding:
        qs = qs.filter(is_wedding_service=True)
        filters.append("Wedding")
    if is_premium:
        qs = qs.filter(is_premium=True)
        filters.append("Premium")
    if is_chauffeur:
        qs = qs.filter(is_chauffeur_available=True)
        filters.append("With Driver")
    if is_monthly:
        qs = qs.filter(rental_mode__in=["monthly", "flexible"])
        filters.append("Monthly")

    # Free-text fallback search if we couldn't extract anything
    if not filters and text:
        # Tokenize, drop stopwords, search name/brand/model
        tokens = [t for t in re.findall(r"\w{3,}", text.lower()) if t not in _STOPWORDS]
        if tokens:
            q = Q()
            for t in tokens:
                q |= Q(name__icontains=t) | Q(brand__icontains=t) | Q(model__icontains=t) | Q(description__icontains=t)
            qs = qs.filter(q)
            filters.append(f"matching '{' '.join(tokens[:3])}'")

    # Order: featured first, then cheapest first
    qs = qs.order_by("-is_featured", "price_per_day")[:limit]
    vehicles = list(qs)

    if vehicles:
        n = len(vehicles)
        crit = ", ".join(filters) if filters else "your search"
        reply = f"Found {n} car{'s' if n != 1 else ''} for {crit}. Here are the top picks:"
    else:
        crit = ", ".join(filters) if filters else "that"
        reply = f"I couldn't find any cars matching {crit}. Try widening the search — change the body type, drop the price limit, or message us on WhatsApp for help."

    return {
        "reply": reply,
        "vehicles": [_serialize(v) for v in vehicles],
        "filters_applied": filters,
        "intent": "search",
    }


_STOPWORDS = {
    "the", "and", "for", "with", "any", "show", "find", "want", "need", "looking",
    "have", "has", "are", "from", "this", "that", "please", "can", "you", "give",
    "tell", "what", "where", "which", "your", "our", "but", "not",
}


def _serialize(v: Vehicle) -> dict:
    price, label = v.primary_price
    return {
        "id": v.id,
        "name": v.name,
        "brand": v.brand,
        "slug": v.slug,
        "url": v.get_absolute_url(),
        "price": float(price) if price else None,
        "price_label": label,
        "thumbnail": v.thumbnail.url if v.thumbnail else None,
        "transmission": v.get_transmission_display() if v.transmission else "",
        "fuel": v.get_fuel_type_display() if v.fuel_type else "",
        "seats": v.seating_capacity,
        "is_premium": v.is_premium,
        "is_wedding": v.is_wedding_service,
        "category": v.category.name if v.category else "",
    }


def _help_response() -> dict:
    return {
        "reply": (
            "I can help you find a car. Tell me what you're looking for — try things like:\n\n"
            "• \"Automatic SUV under 3000\"\n"
            "• \"Wedding car in Kochi\"\n"
            "• \"Maruti petrol manual\"\n"
            "• \"Premium car with driver\"\n"
            "• \"7 seater for outstation\""
        ),
        "vehicles": [],
        "filters_applied": [],
        "intent": "help",
    }
