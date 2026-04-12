import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Initialize production: create admin user and seed data if empty"

    def handle(self, *args, **options):
        # Create admin if none exists
        if not User.objects.filter(is_superuser=True).exists():
            email = os.environ.get("ADMIN_EMAIL", "admin@vehiclerentpro.com")
            password = os.environ.get("ADMIN_PASSWORD", "Admin@2026")
            name = os.environ.get("ADMIN_NAME", "Admin")
            User.objects.create_superuser(email=email, password=password, full_name=name)
            self.stdout.write(self.style.SUCCESS(f"Admin user created: {email}"))
        else:
            self.stdout.write("Admin user already exists, skipping.")

        # Seed data if no vehicles exist
        from vehicles.models import Vehicle
        if not Vehicle.objects.exists():
            call_command("seed_data")
            self.stdout.write(self.style.SUCCESS("Seed data created."))
        else:
            self.stdout.write("Vehicles already exist, skipping seed.")

        # Create SiteConfig if not exists
        from core.models import SiteConfig
        config = SiteConfig.load()
        if not config.phone:
            config.site_name = os.environ.get("BUSINESS_NAME", "VehicleRent Pro")
            config.phone = os.environ.get("BUSINESS_PHONE", "")
            config.email = os.environ.get("BUSINESS_EMAIL", "")
            config.address = os.environ.get("BUSINESS_ADDRESS", "")
            config.whatsapp_number = os.environ.get("WHATSAPP_NUMBER", "")
            config.save()
            self.stdout.write(self.style.SUCCESS("SiteConfig initialized from env vars."))
