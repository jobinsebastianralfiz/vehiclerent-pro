from django.core.exceptions import ValidationError
from django.db import models


class Allocation(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="allocations"
    )
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="allocations"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pickup_location = models.CharField(max_length=300, blank=True)
    drop_location = models.CharField(max_length=300, blank=True)
    odometer_start = models.PositiveIntegerField(blank=True, null=True)
    odometer_end = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.vehicle} → {self.customer} ({self.start_date} to {self.end_date})"

    def duration_days(self):
        return (self.end_date - self.start_date).days

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date.")

        if not self.pk:  # Only on creation
            if hasattr(self, "vehicle") and self.vehicle_id:
                if self.vehicle.status in ("rented", "maintenance"):
                    raise ValidationError("This vehicle is not available for allocation.")
            if hasattr(self, "customer") and self.customer_id:
                if self.customer.is_blacklisted:
                    raise ValidationError("This customer is blacklisted.")

        # Check for overlapping allocations
        if self.vehicle_id and self.start_date and self.end_date:
            overlapping = Allocation.objects.filter(
                vehicle=self.vehicle,
                status="active",
                start_date__lt=self.end_date,
                end_date__gt=self.start_date,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError("This vehicle already has an active allocation during this period.")

    def save(self, *args, **kwargs):
        # Auto-calculate amounts
        if self.start_date and self.end_date and self.daily_rate:
            days = max(self.duration_days(), 1)
            self.total_amount = days * self.daily_rate
            self.balance_amount = self.total_amount - self.advance_paid

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.status == "active":
            self.vehicle.status = "rented"
            self.vehicle.total_trips += 1
            self.vehicle.save(update_fields=["status", "total_trips"])

    def complete(self, actual_return_date=None, odometer_end=None):
        self.status = "completed"
        if actual_return_date:
            self.actual_return_date = actual_return_date
        if odometer_end:
            self.odometer_end = odometer_end
        self.save(update_fields=["status", "actual_return_date", "odometer_end", "updated_at"])
        self.vehicle.status = "available"
        self.vehicle.save(update_fields=["status"])

    def cancel(self):
        self.status = "cancelled"
        self.save(update_fields=["status", "updated_at"])
        self.vehicle.status = "available"
        self.vehicle.save(update_fields=["status"])
