from django import forms
from .models import Allocation
from vehicles.models import Vehicle
from customers.models import Customer


class AllocationForm(forms.ModelForm):
    class Meta:
        model = Allocation
        exclude = ["actual_return_date", "odometer_end", "status", "created_at", "updated_at"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(
                status__in=["available", "reserved"]
            )
            self.fields["customer"].queryset = Customer.objects.filter(
                is_blacklisted=False
            )

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get("vehicle")
        customer = cleaned_data.get("customer")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be after start date.")

        if vehicle and start_date and end_date:
            days = (end_date - start_date).days
            if days < vehicle.minimum_rental_days:
                raise forms.ValidationError(
                    f"This vehicle requires a minimum rental of {vehicle.minimum_rental_days} days. "
                    f"You selected {days} day{'s' if days != 1 else ''}."
                )

        if vehicle and not self.instance.pk:
            if vehicle.status in ("rented", "maintenance"):
                raise forms.ValidationError("This vehicle is not available for allocation.")

        if customer and customer.is_blacklisted:
            raise forms.ValidationError("This customer is blacklisted.")

        if vehicle and start_date and end_date:
            overlapping = Allocation.objects.filter(
                vehicle=vehicle,
                status="active",
                start_date__lt=end_date,
                end_date__gt=start_date,
            ).exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise forms.ValidationError("This vehicle has an overlapping active allocation.")

        return cleaned_data


class AllocationCompleteForm(forms.Form):
    actual_return_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    odometer_end = forms.IntegerField(required=False)
