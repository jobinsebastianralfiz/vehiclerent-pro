"""Seed default categories, Kerala cities, booking addons and wedding decoration packages.

Idempotent — safe to re-run.
"""
from django.core.management.base import BaseCommand

from vehicles.models import (
    BookingAddon,
    City,
    VehicleCategory,
    WeddingDecorationPackage,
)


CATEGORIES = [
    ("Self-Drive", "directions_car", 10, "Drive yourself — pickup, go, explore."),
    ("Wedding Cars", "favorite", 20, "Chauffeur-driven decorated cars for the wedding day."),
    ("Chauffeur Driven", "badge", 30, "Sit back and let our trained chauffeurs drive you."),
    ("Premium / Luxury", "diamond", 40, "European luxury and flagship Indian models."),
    ("SUV", "directions_car", 50, "Spacious SUVs for ghats, beaches and family trips."),
    ("Sedan", "airline_seat_recline_extra", 60, "Comfortable sedans for city and highway."),
    ("Hatchback", "garage", 70, "Compact, agile hatchbacks for city runs."),
    ("Electric", "bolt", 80, "Zero-emission, near-silent, charged and ready."),
    ("Automatic", "settings", 90, "No clutch needed — automatic-only fleet."),
    ("Manual", "tune", 95, "Classic manual transmission for the driving purist."),
    ("Outstation", "route", 100, "Vehicles permitted for inter-state travel."),
    ("Airport Transfer", "flight", 110, "Doorstep airport pickups and drops."),
    ("Monthly Subscription", "calendar_month", 120, "Long-term plans with monthly billing."),
]

CITIES = [
    # (name, is_hub, order)
    ("Kochi", True, 10),
    ("Trivandrum", True, 20),
    ("Kottayam", True, 30),
    ("Calicut", True, 40),
    ("Thrissur", True, 50),
    ("Kannur", False, 60),
    ("Alappuzha", False, 70),
    ("Kollam", False, 80),
    ("Pathanamthitta", False, 90),
    ("Idukki", False, 100),
    ("Palakkad", False, 110),
    ("Malappuram", False, 120),
    ("Thiruvalla", False, 130),
    ("Changanassery", False, 140),
    ("Munnar", False, 150),
    ("Wayanad", False, 160),
]

ADDONS = [
    ("Baby Seat", "child_friendly", 200, "per_day", 10),
    ("GPS Device", "gps_fixed", 150, "per_day", 20),
    ("Additional Driver", "person_add", 500, "per_trip", 30),
    ("Zero-Deposit Waiver", "shield", 400, "per_day", 40),
    ("Premium Insurance", "verified_user", 250, "per_day", 50),
    ("Doorstep Delivery", "local_shipping", 500, "per_trip", 60),
]

DECORATIONS = [
    ("Traditional Kerala", "Marigold + jasmine + plantain leaf — classic Kerala wedding decor.", 3500, 10),
    ("Modern Minimal", "White roses + eucalyptus — restrained, photographic.", 6000, 20),
    ("Luxe Rose & Orchid", "Premium imported roses with cascading orchids.", 12000, 30),
    ("Custom (consult florist)", "Designed with our in-house florist around your theme.", 8000, 40),
]


class Command(BaseCommand):
    help = "Seed default taxonomy: categories, cities, booking addons, wedding decoration packages."

    def handle(self, *args, **options):
        created_categories = 0
        for name, icon, order, desc in CATEGORIES:
            obj, created = VehicleCategory.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "display_order": order, "description": desc, "is_active": True},
            )
            if created:
                created_categories += 1
        self.stdout.write(self.style.SUCCESS(f"Categories: {created_categories} new, {len(CATEGORIES)} total."))

        created_cities = 0
        for name, is_hub, order in CITIES:
            obj, created = City.objects.get_or_create(
                name=name,
                defaults={"is_hub": is_hub, "display_order": order, "state": "Kerala", "is_active": True},
            )
            if created:
                created_cities += 1
        self.stdout.write(self.style.SUCCESS(f"Cities: {created_cities} new, {len(CITIES)} total."))

        created_addons = 0
        for name, icon, price, unit, order in ADDONS:
            obj, created = BookingAddon.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "price": price, "pricing_unit": unit, "display_order": order, "is_active": True},
            )
            if created:
                created_addons += 1
        self.stdout.write(self.style.SUCCESS(f"Addons: {created_addons} new, {len(ADDONS)} total."))

        created_decorations = 0
        for name, desc, price, order in DECORATIONS:
            obj, created = WeddingDecorationPackage.objects.get_or_create(
                name=name,
                defaults={"description": desc, "price": price, "display_order": order, "is_active": True},
            )
            if created:
                created_decorations += 1
        self.stdout.write(self.style.SUCCESS(f"Decorations: {created_decorations} new, {len(DECORATIONS)} total."))

        self.stdout.write(self.style.SUCCESS("\nDone. Run /manage/categories/ to review."))
