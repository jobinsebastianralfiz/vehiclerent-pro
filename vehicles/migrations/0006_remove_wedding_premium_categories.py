from django.db import migrations


def remove_categories(apps, schema_editor):
    VehicleCategory = apps.get_model("vehicles", "VehicleCategory")
    VehicleCategory.objects.filter(name__in=["Wedding Service", "Premium Cars"]).delete()


def add_categories_back(apps, schema_editor):
    VehicleCategory = apps.get_model("vehicles", "VehicleCategory")
    VehicleCategory.objects.get_or_create(
        name="Wedding Service",
        defaults={"slug": "wedding-service", "description": "Luxury vehicles for wedding occasions", "icon": "favorite", "display_order": 7},
    )
    VehicleCategory.objects.get_or_create(
        name="Premium Cars",
        defaults={"slug": "premium-cars", "description": "Premium and luxury car collection", "icon": "star", "display_order": 8},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0005_add_premium_wedding_badges'),
    ]

    operations = [
        migrations.RunPython(remove_categories, add_categories_back),
    ]
