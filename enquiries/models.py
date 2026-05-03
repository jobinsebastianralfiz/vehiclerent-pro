from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string


class Enquiry(models.Model):
    SOURCE_CHOICES = [
        ("website", "Website"),
        ("whatsapp", "WhatsApp"),
        ("phone", "Phone"),
        ("walkin", "Walk-in"),
    ]
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("follow_up", "Follow Up"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.SET_NULL, blank=True, null=True, related_name="enquiries"
    )
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.SET_NULL, blank=True, null=True, related_name="enquiries"
    )
    RENTAL_TYPE_CHOICES = [
        ("self_drive", "Self-Drive"),
        ("with_driver", "With Driver"),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="website")
    preferred_start_date = models.DateField(blank=True, null=True)
    preferred_end_date = models.DateField(blank=True, null=True)
    pickup_city = models.CharField(max_length=120, blank=True, help_text="City slug from booking widget")
    drop_city = models.CharField(max_length=120, blank=True, help_text="City slug from booking widget")
    rental_type = models.CharField(max_length=20, choices=RENTAL_TYPE_CHOICES, blank=True)
    requested_addons = models.JSONField(default=list, blank=True, help_text="List of addon slugs requested")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Enquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Enquiry from {self.name} ({self.phone})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self._send_notification_email()

    def _send_notification_email(self):
        try:
            subject = f"New Enquiry from {self.name}"
            html_message = render_to_string("emails/enquiry_notification.html", {"enquiry": self})
            send_mail(
                subject=subject,
                message=f"New enquiry from {self.name} ({self.phone})",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFICATION_EMAIL],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass
