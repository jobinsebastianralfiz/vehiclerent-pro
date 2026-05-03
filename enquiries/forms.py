from django import forms
from .models import Enquiry


class EnquiryPublicForm(forms.ModelForm):
    # Capture multi-select addons from the booking widget
    addons = forms.MultipleChoiceField(required=False, choices=())

    class Meta:
        model = Enquiry
        fields = [
            "name", "phone", "email", "message",
            "preferred_start_date", "preferred_end_date",
            "vehicle", "pickup_city", "drop_city", "rental_type",
        ]
        widgets = {
            "vehicle": forms.HiddenInput(),
            "preferred_start_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].required = False
        self.fields["email"].required = False
        self.fields["message"].required = False
        self.fields["preferred_start_date"].required = False
        self.fields["preferred_end_date"].required = False
        self.fields["pickup_city"].required = False
        self.fields["drop_city"].required = False
        self.fields["rental_type"].required = False
        # Resolve addon choices lazily so admin migrations don't import-fail
        try:
            from vehicles.models import BookingAddon
            self.fields["addons"].choices = [
                (a.slug, a.name) for a in BookingAddon.objects.filter(is_active=True)
            ]
        except Exception:
            self.fields["addons"].choices = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.requested_addons = self.cleaned_data.get("addons", []) or []
        if commit:
            instance.save()
        return instance


class EnquiryUpdateForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["status", "admin_notes"]
        widgets = {
            "admin_notes": forms.Textarea(attrs={"rows": 4}),
        }
