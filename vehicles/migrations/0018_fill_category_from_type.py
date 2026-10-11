from django.db import migrations

TYPE_CATEGORY = {
    "hatchback": "cars", "sedan": "cars", "muv": "cars", "car": "cars",
    "suv": "suvs", "bike": "bikes", "scooter": "scooters",
    "van": "vans", "tempo": "vans", "bus": "vans", "truck": "trucks",
}


def fill_category(apps, schema_editor):
    """Vehicles without a category get the one their type maps to."""
    Vehicle = apps.get_model("vehicles", "Vehicle")
    VehicleCategory = apps.get_model("vehicles", "VehicleCategory")
    ids = dict(VehicleCategory.objects.filter(is_active=True).values_list("slug", "id"))
    for vtype, slug in TYPE_CATEGORY.items():
        if slug in ids:
            Vehicle.objects.filter(category__isnull=True, vehicle_type=vtype).update(category_id=ids[slug])


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0017_luxury_flag"),
    ]

    operations = [
        migrations.RunPython(fill_category, migrations.RunPython.noop),
    ]
