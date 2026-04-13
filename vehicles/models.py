from django.db import models
from django.utils.text import slugify


class VehicleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Material Symbols icon name")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Vehicle Categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def vehicle_count(self):
        return self.vehicles.filter(is_published=True).exclude(status="inactive").count()


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ("car", "Car"),
        ("bike", "Bike"),
        ("scooter", "Scooter"),
        ("van", "Van"),
        ("truck", "Truck"),
        ("bus", "Bus"),
        ("suv", "SUV"),
        ("tempo", "Tempo"),
        ("auto", "Auto"),
        ("other", "Other"),
    ]
    FUEL_TYPE_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
        ("cng", "CNG"),
        ("lpg", "LPG"),
    ]
    TRANSMISSION_CHOICES = [
        ("manual", "Manual"),
        ("automatic", "Automatic"),
        ("amt", "AMT"),
        ("cvt", "CVT"),
    ]
    STATUS_CHOICES = [
        ("available", "Available"),
        ("rented", "Rented"),
        ("maintenance", "Maintenance"),
        ("reserved", "Reserved"),
        ("inactive", "Inactive"),
    ]
    RENTAL_MODE_CHOICES = [
        ("daily", "Daily Rental"),
        ("weekly", "Weekly Rental"),
        ("monthly", "Monthly Rental"),
        ("flexible", "Flexible (All Plans)"),
    ]

    slug = models.SlugField(max_length=200, unique=True, blank=True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField(blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default="car")
    category = models.ForeignKey(
        VehicleCategory, on_delete=models.SET_NULL, blank=True, null=True, related_name="vehicles"
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, blank=True)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, blank=True)
    seating_capacity = models.PositiveIntegerField(blank=True, null=True)
    engine_cc = models.PositiveIntegerField(blank=True, null=True, help_text="For petrol/diesel/CNG vehicles")
    mileage_kmpl = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, help_text="For petrol/diesel vehicles")
    # EV / Hybrid specific fields
    battery_capacity_kwh = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True, help_text="Battery capacity in kWh (for EV/Hybrid)")
    range_km = models.PositiveIntegerField(blank=True, null=True, help_text="Range in km on full charge (for EV/Hybrid)")
    motor_power_kw = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True, help_text="Motor power in kW (for EV/Hybrid)")
    charging_time_hours = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Charging time in hours (for EV)")
    fast_charging = models.BooleanField(default=False, help_text="Supports fast charging")
    rental_mode = models.CharField(max_length=20, choices=RENTAL_MODE_CHOICES, default="flexible", help_text="How this vehicle is rented out")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    minimum_rental_days = models.PositiveIntegerField(default=1, help_text="Minimum rental period in days")
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    thumbnail = models.ImageField(upload_to="vehicles/thumbnails/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Mark as a premium/luxury vehicle")
    is_wedding_service = models.BooleanField(default=False, help_text="Available for wedding services")
    is_published = models.BooleanField(default=True)
    total_trips = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand}-{self.model}-{self.name}")
            slug = base_slug
            counter = 1
            while Vehicle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/vehicles/{self.slug}/"

    def is_available(self):
        return self.status == "available"

    @property
    def is_ev_or_hybrid(self):
        return self.fuel_type in ("electric", "hybrid")

    @property
    def primary_price(self):
        """Returns (price, label) for the main display price."""
        if self.rental_mode == "monthly":
            return (self.price_per_month, "month")
        if self.rental_mode == "weekly":
            return (self.price_per_week or self.price_per_day, "week" if self.price_per_week else "day")
        return (self.price_per_day, "day")

    @property
    def primary_price_value(self):
        return self.primary_price[0]

    @property
    def primary_price_label(self):
        return self.primary_price[1]

    @property
    def daily_rate_for_allocation(self):
        """Best rate to use for allocation auto-fill."""
        if self.price_per_day:
            return self.price_per_day
        if self.price_per_month:
            return round(self.price_per_month / 30, 2)
        if self.price_per_week:
            return round(self.price_per_week / 7, 2)
        return 0


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicles/gallery/")
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-is_primary"]

    def __str__(self):
        return f"Image for {self.vehicle.name} (#{self.display_order})"
