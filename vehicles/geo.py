"""Approximate centre coordinates for Kerala towns, used to pin cities on the map.

A City with no latitude/longitude gets these filled in on save when its name
(or a common alternative spelling) is listed here. Admins can override them.
"""

KERALA_COORDS = {
    "kochi": (9.9312, 76.2673),
    "kasaragod": (12.4996, 74.9869),
    "kannur": (11.8745, 75.3704),
    "wayanad": (11.6085, 76.0830),
    "kalpetta": (11.6085, 76.0830),
    "calicut": (11.2588, 75.7804),
    "malappuram": (11.0510, 76.0711),
    "palakkad": (10.7867, 76.6548),
    "thrissur": (10.5276, 76.2144),
    "guruvayur": (10.5946, 76.0410),
    "munnar": (10.0889, 77.0595),
    "idukki": (9.8497, 76.9722),
    "thodupuzha": (9.8959, 76.7184),
    "aluva": (10.1004, 76.3570),
    "muvattupuzha": (9.9894, 76.5790),
    "kottayam": (9.5916, 76.5222),
    "alappuzha": (9.4981, 76.3388),
    "kumarakom": (9.6175, 76.4301),
    "changanassery": (9.4442, 76.5410),
    "thiruvalla": (9.3835, 76.5741),
    "pathanamthitta": (9.2648, 76.7870),
    "kollam": (8.8932, 76.6141),
    "varkala": (8.7379, 76.7163),
    "trivandrum": (8.5241, 76.9366),
    "kovalam": (8.4004, 76.9787),
    "thekkady": (9.6031, 77.1615),
    "vagamon": (9.6862, 76.9052),
}

ALIASES = {
    "cochin": "kochi",
    "ernakulam": "kochi",
    "kozhikode": "calicut",
    "thiruvananthapuram": "trivandrum",
    "alleppey": "alappuzha",
    "quilon": "kollam",
    "trichur": "thrissur",
    "palghat": "palakkad",
    "cannanore": "kannur",
    "tiruvalla": "thiruvalla",
    "changanacherry": "changanassery",
}


def lookup(name):
    """Return (lat, lng) for a Kerala town name, or None if it isn't known."""
    key = (name or "").strip().lower()
    key = ALIASES.get(key, key)
    return KERALA_COORDS.get(key)
