from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class AdminUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class AdminUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = AdminUserManager()

    def __str__(self):
        return self.full_name or self.email


class SiteConfig(models.Model):
    """Singleton site configuration — only one row should exist."""

    # Branding
    site_name = models.CharField(max_length=200, default="VehicleRent Pro")
    tagline = models.CharField(max_length=300, blank=True, default="The Digital Concierge")
    logo = models.ImageField(upload_to="site/", blank=True, help_text="Site logo image")
    favicon = models.ImageField(upload_to="site/", blank=True)

    # Contact
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Without + sign, e.g. 919999999999")
    whatsapp_default_message = models.CharField(max_length=500, blank=True, default="Hi, I'm interested in renting a vehicle from your fleet.")
    google_maps_embed = models.TextField(blank=True, help_text="Google Maps embed iframe URL")

    # Homepage Hero
    hero_title = models.CharField(max_length=300, default="Rent Your Perfect Vehicle")
    hero_subtitle = models.CharField(max_length=500, blank=True, default="Premium Vehicle Rental")
    hero_cta_text = models.CharField(max_length=100, default="Browse Fleet")
    hero_image = models.ImageField(upload_to="site/hero/", blank=True, help_text="Hero background/side image")

    # About Page
    about_title = models.CharField(max_length=300, default="About Us")
    about_content = models.TextField(blank=True, help_text="Main about page content (HTML allowed)")
    about_image = models.ImageField(upload_to="site/about/", blank=True)
    about_mission = models.TextField(blank=True, help_text="Our Mission statement")
    about_vision = models.TextField(blank=True, help_text="Our Vision statement")
    years_in_business = models.PositiveIntegerField(default=0, blank=True)
    total_happy_customers = models.PositiveIntegerField(default=0, blank=True)
    license_number = models.CharField(max_length=200, blank=True, help_text="Business license/registration number")
    license_details = models.TextField(blank=True, help_text="License details, certifications, registrations (HTML allowed)")

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="Default page title for SEO")
    meta_description = models.CharField(max_length=500, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to="site/seo/", blank=True, help_text="Default Open Graph sharing image")

    # Social
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    # Footer
    footer_text = models.CharField(max_length=500, blank=True, default="Premium vehicle rental service. Flexible daily, weekly & monthly plans.")

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True, help_text="e.g. Business Owner, Tourist")
    quote = models.TextField()
    photo = models.ImageField(upload_to="testimonials/", blank=True)
    rating = models.PositiveIntegerField(default=5, help_text="1-5 stars")
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.quote[:50]}"


# Keep legacy model for backward compatibility
class SiteSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Site Settings (Legacy)"

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=""):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
