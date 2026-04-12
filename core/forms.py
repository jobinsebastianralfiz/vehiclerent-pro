from django import forms
from .models import SiteConfig, Testimonial


class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Email address",
            "autofocus": True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
        })
    )


class SiteConfigForm(forms.ModelForm):
    class Meta:
        model = SiteConfig
        fields = "__all__"
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "about_content": forms.Textarea(attrs={"rows": 8}),
            "about_mission": forms.Textarea(attrs={"rows": 3}),
            "about_vision": forms.Textarea(attrs={"rows": 3}),
            "license_details": forms.Textarea(attrs={"rows": 4}),
            "footer_text": forms.Textarea(attrs={"rows": 2}),
            "google_maps_embed": forms.Textarea(attrs={"rows": 2}),
            "meta_description": forms.Textarea(attrs={"rows": 2}),
        }


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "role", "quote", "photo", "rating", "is_active", "display_order"]
        widgets = {
            "quote": forms.Textarea(attrs={"rows": 3}),
        }
