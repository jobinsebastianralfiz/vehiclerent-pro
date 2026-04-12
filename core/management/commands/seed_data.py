from django.core.management.base import BaseCommand
from vehicles.models import VehicleCategory, Vehicle


class Command(BaseCommand):
    help = "Seed sample categories and vehicles"

    def handle(self, *args, **options):
        categories = [
            {"name": "Cars", "icon": "directions_car", "display_order": 1},
            {"name": "SUVs", "icon": "suv", "display_order": 2},
            {"name": "Bikes", "icon": "two_wheeler", "display_order": 3},
            {"name": "Vans", "icon": "airport_shuttle", "display_order": 4},
            {"name": "Scooters", "icon": "electric_scooter", "display_order": 5},
            {"name": "Trucks", "icon": "local_shipping", "display_order": 6},
        ]

        for cat_data in categories:
            cat, created = VehicleCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults=cat_data,
            )
            if created:
                self.stdout.write(f"  Created category: {cat.name}")

        cars_cat = VehicleCategory.objects.get(name="Cars")
        suv_cat = VehicleCategory.objects.get(name="SUVs")
        bikes_cat = VehicleCategory.objects.get(name="Bikes")

        vehicles = [
            {"name": "Swift Dzire VXi", "brand": "Maruti Suzuki", "model": "Dzire", "vehicle_type": "car", "category": cars_cat, "fuel_type": "petrol", "transmission": "manual", "seating_capacity": 5, "price_per_day": 1500, "price_per_week": 9000, "price_per_month": 30000, "features": ["AC", "Power Steering", "Power Windows", "Music System"], "is_featured": True, "description": "A reliable and fuel-efficient sedan perfect for city commutes and short trips."},
            {"name": "Innova Crysta GX", "brand": "Toyota", "model": "Innova Crysta", "vehicle_type": "car", "category": cars_cat, "fuel_type": "diesel", "transmission": "manual", "seating_capacity": 7, "price_per_day": 3000, "price_per_week": 18000, "price_per_month": 60000, "features": ["AC", "Power Steering", "Captain Seats", "Music System", "USB Charging"], "is_featured": True, "description": "Premium MPV with spacious interiors, ideal for family trips and airport transfers."},
            {"name": "Creta SX", "brand": "Hyundai", "model": "Creta", "vehicle_type": "suv", "category": suv_cat, "fuel_type": "petrol", "transmission": "automatic", "seating_capacity": 5, "price_per_day": 2500, "price_per_week": 15000, "price_per_month": 50000, "features": ["AC", "Sunroof", "Touchscreen", "Reverse Camera", "Bluetooth"], "is_featured": True, "description": "A popular compact SUV with great features and a smooth automatic transmission."},
            {"name": "Fortuner 4x4", "brand": "Toyota", "model": "Fortuner", "vehicle_type": "suv", "category": suv_cat, "fuel_type": "diesel", "transmission": "automatic", "seating_capacity": 7, "price_per_day": 5000, "price_per_week": 30000, "price_per_month": 100000, "security_deposit": 10000, "features": ["AC", "4WD", "Leather Seats", "Cruise Control", "Touchscreen", "360 Camera"], "is_featured": True, "description": "A powerful full-size SUV built for both city driving and off-road adventures."},
            {"name": "Royal Enfield Classic 350", "brand": "Royal Enfield", "model": "Classic 350", "vehicle_type": "bike", "category": bikes_cat, "fuel_type": "petrol", "transmission": "manual", "seating_capacity": 2, "engine_cc": 349, "price_per_day": 800, "price_per_week": 5000, "features": ["ABS", "Digital Console", "USB Charging"], "description": "An iconic cruiser motorcycle perfect for leisure rides and weekend getaways."},
            {"name": "Ertiga ZXi", "brand": "Maruti Suzuki", "model": "Ertiga", "vehicle_type": "car", "category": cars_cat, "fuel_type": "petrol", "transmission": "automatic", "seating_capacity": 7, "price_per_day": 2000, "price_per_week": 12000, "price_per_month": 40000, "features": ["AC", "Touchscreen", "Rear AC Vents", "Push Start"], "description": "A practical 7-seater MPV with good fuel efficiency and comfortable ride."},
        ]

        for v_data in vehicles:
            v, created = Vehicle.objects.get_or_create(
                name=v_data["name"],
                brand=v_data["brand"],
                defaults=v_data,
            )
            if created:
                self.stdout.write(f"  Created vehicle: {v.brand} {v.name}")

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))
