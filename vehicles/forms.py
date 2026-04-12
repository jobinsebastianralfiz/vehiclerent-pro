from django import forms
from .models import Vehicle, VehicleCategory, VehicleImage


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ["slug", "total_trips", "created_at", "updated_at"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "features": forms.Textarea(attrs={"rows": 3, "placeholder": '["AC", "GPS", "Bluetooth"]'}),
            "vehicle_type": forms.Select(),
            "fuel_type": forms.Select(),
            "transmission": forms.Select(),
            "status": forms.Select(),
        }


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
