from django import forms

from .models import TourPackage


class TourPackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        exclude = ["slug", "created_at", "updated_at"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Munnar & Thekkady Hills"}),
            "destinations": forms.TextInput(attrs={"placeholder": "e.g. Munnar · Thekkady"}),
            "tag": forms.TextInput(attrs={"placeholder": "e.g. Bestseller"}),
            "summary": forms.TextInput(attrs={"placeholder": "Tea estates, spice gardens and a Periyar boat ride in one easy trip."}),
            "highlights": forms.Textarea(attrs={"rows": 5, "placeholder": "Tea estates & Eravikulam\nSpice plantation walk\nPeriyar boat ride"}),
            "itinerary": forms.Textarea(attrs={"rows": 5, "placeholder": "Day 1: Pickup from Kochi, drive to Munnar\nDay 2: Eravikulam, tea museum\nDay 3: Thekkady, spice walk"}),
            "inclusions": forms.Textarea(attrs={"rows": 4, "placeholder": "Hotel stay with breakfast\nAC car with driver\nSightseeing as listed"}),
            "exclusions": forms.Textarea(attrs={"rows": 4, "placeholder": "Entry tickets\nLunch and dinner"}),
            "meta_description": forms.TextInput(),
        }
