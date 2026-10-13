from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .themes import DEFAULT_THEME, THEME_CHOICES


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
    show_brand_name = models.BooleanField(default=True, help_text="Show brand name text next to the logo")
    favicon = models.ImageField(upload_to="site/", blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=DEFAULT_THEME, help_text="Design of the public website")

    # Contact
    phone = models.CharField(max_length=30, blank=True)
    business_hours = models.CharField(max_length=100, blank=True, default="9:00 AM – 8:00 PM (Daily)", help_text="When the phone is answered, shown on the contact page")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Without + sign, e.g. 919999999999")
    whatsapp_default_message = models.CharField(max_length=500, blank=True, default="Hi, I'm interested in renting a vehicle from your fleet.")
    google_maps_embed = models.TextField(blank=True, help_text="Google Maps embed iframe URL")

    # Homepage Hero
    hero_title = models.CharField(max_length=300, default="Rent Your Perfect Vehicle")
    hero_subtitle = models.CharField(max_length=500, blank=True, default="Premium Vehicle Rental")
    hero_description = models.CharField(max_length=500, blank=True, default="Explore our premium fleet. Flexible daily, weekly, and monthly rentals with 24/7 roadside support.")
    hero_cta_text = models.CharField(max_length=100, default="Browse Fleet")
    hero_highlights = models.TextField(blank=True, default="Well-maintained vehicles\nFlexible rental plans\nTrusted local support",
                                       help_text="Short trust points under the hero button, one per line (up to 3)")
    hero_image = models.ImageField(upload_to="site/hero/", blank=True, help_text="Hero background/side image")
    hero_bg_1 = models.ImageField(upload_to="site/hero/", blank=True, help_text="Hero background slide 1")
    hero_bg_2 = models.ImageField(upload_to="site/hero/", blank=True, help_text="Hero background slide 2")
    hero_bg_3 = models.ImageField(upload_to="site/hero/", blank=True, help_text="Hero background slide 3")

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
    # Tour packages section (home page + Tours page)
    tours_on_home = models.BooleanField(default=True, help_text="Show the tour packages section on the home page")
    tours_heading = models.CharField(max_length=120, blank=True, default="Where to *next?*", help_text="Wrap words in *asterisks* for the italic accent")
    tours_intro = models.CharField(max_length=300, blank=True, default="Hand-planned holidays with stays, sightseeing and a car with driver, across India and abroad.")
    tours_domestic_places = models.CharField(max_length=300, blank=True, default="Kerala, Kashmir, Goa, Rajasthan, Himachal, Andaman",
                                             help_text="Comma-separated; shown as WhatsApp enquiry chips while no domestic packages are added")
    tours_domestic_image = models.ImageField(upload_to="site/", blank=True, help_text="Background photo of the Domestic card")
    tours_international_image = models.ImageField(upload_to="site/", blank=True, help_text="Background photo of the International card")
    tours_international_places = models.CharField(max_length=300, blank=True, default="Dubai, Thailand, Bali, Singapore, Malaysia, Maldives",
                                                  help_text="Comma-separated; shown as WhatsApp enquiry chips while no international packages are added")

    footer_text = models.CharField(max_length=500, blank=True, default="Premium vehicle rental service. Flexible daily, weekly & monthly plans.")

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        from .images import shrink_uploads
        shrink_uploads(self, "hero_image", "hero_bg_1", "hero_bg_2", "hero_bg_3", "about_image")
        # a newly uploaded share image becomes an exact 1200x630 JPEG
        if self.og_image and not getattr(self.og_image, "_committed", True):
            from .images import share_image
            res = share_image(self.og_image.file)
            if res:
                self.og_image.save(res[0], res[1], save=False)
        # pasted SEO text arrives with line breaks; search engines and share previews want one line
        for f in ("meta_title", "meta_description", "meta_keywords"):
            setattr(self, f, " ".join((getattr(self, f) or "").split()))
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


class PageView(models.Model):
    """One public page view, recorded by core.analytics.PageViewMiddleware. No IP is stored: `visitor` is a
    daily-rotating hash, enough to count unique visitors per day and nothing more."""
    SOURCE_CHOICES = [
        ("direct", "Direct"), ("google", "Google"), ("bing", "Bing"), ("whatsapp", "WhatsApp"),
        ("facebook", "Facebook"), ("instagram", "Instagram"), ("youtube", "YouTube"),
        ("ai", "AI assistants"), ("internal", "Within the site"), ("other", "Other sites"),
    ]
    DEVICE_CHOICES = [("mobile", "Mobile"), ("tablet", "Tablet"), ("desktop", "Desktop")]

    path = models.CharField(max_length=300, db_index=True)
    vehicle_slug = models.SlugField(max_length=200, blank=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="direct")
    referrer_host = models.CharField(max_length=200, blank=True)
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES, default="desktop")
    visitor = models.CharField(max_length=16, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.path} ({self.source})"


class SpeedResult(models.Model):
    """Latest Google PageSpeed Insights result for a page and strategy (mobile/desktop), saved from the admin."""
    path = models.CharField(max_length=300)
    strategy = models.CharField(max_length=10, choices=[("mobile", "Mobile"), ("desktop", "Desktop")])
    score = models.PositiveSmallIntegerField()
    lcp_ms = models.PositiveIntegerField(null=True, blank=True)
    cls = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    tbt_ms = models.PositiveIntegerField(null=True, blank=True)
    tested_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("path", "strategy")]

    @property
    def lcp_s(self):
        return round(self.lcp_ms / 1000, 1) if self.lcp_ms else None

    def __str__(self):
        return f"{self.path} {self.strategy}: {self.score}"
