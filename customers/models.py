from django.db import models


class Customer(models.Model):
    ID_PROOF_CHOICES = [
        ("aadhaar", "Aadhaar"),
        ("driving_license", "Driving License"),
        ("passport", "Passport"),
        ("voter_id", "Voter ID"),
    ]

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    id_proof_type = models.CharField(max_length=50, choices=ID_PROOF_CHOICES, blank=True)
    id_proof_number = models.CharField(max_length=100, blank=True)
    id_proof_image = models.ImageField(upload_to="customers/id_proofs/", blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    license_expiry = models.DateField(blank=True, null=True)
    license_image = models.ImageField(upload_to="customers/licenses/", blank=True)
    notes = models.TextField(blank=True, help_text="Admin notes")
    is_blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name

    def total_allocations(self):
        return self.allocations.count()

    def active_allocation(self):
        return self.allocations.filter(status="active").first()
