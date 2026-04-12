from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create an admin user"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default="admin@example.com")
        parser.add_argument("--password", type=str, default="admin123")
        parser.add_argument("--name", type=str, default="Admin")

    def handle(self, *args, **options):
        email = options["email"]
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User {email} already exists"))
            return
        User.objects.create_superuser(
            email=email,
            password=options["password"],
            full_name=options["name"],
        )
        self.stdout.write(self.style.SUCCESS(f"Admin user created: {email}"))
