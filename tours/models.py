from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.images import shrink_uploads


def _lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


class TourPackage(models.Model):
    """A holiday package (domestic or international). No prices on the site: visitors enquire."""

    SCOPE_CHOICES = [("domestic", "Domestic"), ("international", "International")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="domestic", db_index=True)
    destinations = models.CharField(max_length=200, blank=True, help_text="Places covered, e.g. Munnar · Thekkady")
    nights = models.PositiveSmallIntegerField(null=True, blank=True)
    days = models.PositiveSmallIntegerField(null=True, blank=True)
    tag = models.CharField(max_length=40, blank=True, help_text="Optional badge on the card, e.g. Bestseller")
    summary = models.CharField(max_length=300, blank=True, help_text="One or two lines shown on the card and at the top of the page")
    highlights = models.TextField(blank=True, help_text="One per line")
    itinerary = models.TextField(blank=True, help_text="One day per line, e.g. Day 1: Arrive in Munnar, tea museum")
    inclusions = models.TextField(blank=True, help_text="What's included, one per line")
    exclusions = models.TextField(blank=True, help_text="What's not included, one per line")
    cover_image = models.ImageField(upload_to="tours/", blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Shown first")
    display_order = models.IntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "display_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "tour"
            slug, n = base, 1
            while TourPackage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        shrink_uploads(self, "cover_image")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tour_detail", args=[self.slug])

    @property
    def duration(self):
        if self.nights and self.days:
            return f"{self.nights}N / {self.days}D"
        if self.days:
            return f"{self.days} day{'s' if self.days != 1 else ''}"
        if self.nights:
            return f"{self.nights} night{'s' if self.nights != 1 else ''}"
        return ""

    @property
    def highlight_list(self):
        return _lines(self.highlights)

    @property
    def itinerary_days(self):
        """[(label, text)]: "Day 1: Arrive" -> ("Day 1", "Arrive"); lines without a colon get a running day number."""
        out = []
        for i, line in enumerate(_lines(self.itinerary), 1):
            head, sep, rest = line.partition(":")
            out.append((head.strip(), rest.strip()) if sep and len(head) <= 20 else (f"Day {i}", line))
        return out

    @property
    def inclusion_list(self):
        return _lines(self.inclusions)

    @property
    def exclusion_list(self):
        return _lines(self.exclusions)

    @property
    def whatsapp_text(self):
        bits = ", ".join(b for b in (self.duration, self.destinations) if b)
        return (f"Hi! I'm interested in the *{self.title}* tour package{f' ({bits})' if bits else ''}. "
                f"Could you share the details and price for my dates?")
