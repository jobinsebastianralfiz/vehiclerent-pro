from django import forms
from .models import Enquiry


class EnquiryPublicForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["name", "phone", "email", "message", "preferred_start_date", "preferred_end_date", "vehicle"]
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


class EnquiryUpdateForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["status", "admin_notes"]
        widgets = {
            "admin_notes": forms.Textarea(attrs={"rows": 4}),
        }
