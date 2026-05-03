from django.db import models
from django.utils.text import slugify


class City(models.Model):
    """A pickup/drop-off city served by the rental network."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    state = models.CharField(max_length=80, default="Kerala")
    is_active = models.BooleanField(default=True)
    is_hub = models.BooleanField(default=False, help_text="Major delivery hub city (shown first)")
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ["-is_hub", "display_order", "name"]

    def __str__(self):
        return f"{self.name}, {self.state}" if self.state else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VehicleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Material Symbols icon name")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="Custom <title> for this category page")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Meta description (150–160 chars)")
    meta_keywords = models.CharField(max_length=300, blank=True, help_text="Comma-separated keywords")
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
    with_driver_price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Daily rate when rented with a chauffeur (overrides price_per_day if set)",
    )
    per_km_charge = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        help_text="Charge per km after the daily included kilometres are exhausted",
    )
    included_km_per_day = models.PositiveIntegerField(
        default=200, help_text="Free kilometres included in the daily rate",
    )
    wedding_decoration_charge = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Default basic decoration charge for wedding service vehicles",
    )
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
    is_chauffeur_available = models.BooleanField(default=False, help_text="Can be rented with a chauffeur")
    wedding_tier = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("classic", "Classic"),
            ("premium", "Premium"),
            ("iconic", "Iconic"),
        ],
        help_text="Wedding tier — only used if is_wedding_service is true",
    )
    available_cities = models.ManyToManyField(
        City, blank=True, related_name="vehicles",
        help_text="Cities where this vehicle can be picked up / delivered",
    )
    is_published = models.BooleanField(default=True)
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="Custom <title>; defaults to '{Brand} {Name} for Rent'")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Meta description for search engines (150–160 chars)")
    meta_keywords = models.CharField(max_length=300, blank=True, help_text="Comma-separated keywords")
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


class BookingAddon(models.Model):
    """Optional extras that can be added to a rental (baby seat, GPS, additional driver, etc.)."""

    PRICING_UNIT_CHOICES = [
        ("per_day", "Per Day"),
        ("per_trip", "Per Trip"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Material Symbols icon name")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    pricing_unit = models.CharField(max_length=20, choices=PRICING_UNIT_CHOICES, default="per_day")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} (₹{self.price} {self.get_pricing_unit_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WeddingDecorationPackage(models.Model):
    """Floral / decoration packages for wedding car rentals."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="weddings/decorations/", blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} (₹{self.price})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
