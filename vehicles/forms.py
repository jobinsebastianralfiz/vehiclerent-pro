import json

from django import forms
from .models import (
    BookingAddon,
    City,
    Vehicle,
    VehicleCategory,
    VehicleImage,
    WeddingDecorationPackage,
)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ["slug", "total_trips", "created_at", "updated_at"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "features": forms.HiddenInput(),
            "vehicle_type": forms.Select(),
            "fuel_type": forms.Select(),
            "transmission": forms.Select(),
            "status": forms.Select(),
        }

    def clean_features(self):
        """Accept JSON string from the Alpine.js chips component."""
        value = self.cleaned_data.get("features")
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return []


class CategoryForm(forms.ModelForm):
    class Meta:
        model = VehicleCategory
        fields = ["name", "description", "icon", "display_order", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


VehicleImageFormSet = forms.inlineformset_factory(
    Vehicle, VehicleImage,
    fields=["image", "is_primary", "display_order"],
    extra=3,
    can_delete=True,
)


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ["name", "state", "is_hub", "display_order", "is_active"]


class BookingAddonForm(forms.ModelForm):
    class Meta:
        model = BookingAddon
        fields = ["name", "description", "icon", "price", "pricing_unit", "display_order", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class WeddingDecorationPackageForm(forms.ModelForm):
    class Meta:
        model = WeddingDecorationPackage
        fields = ["name", "description", "image", "price", "display_order", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
