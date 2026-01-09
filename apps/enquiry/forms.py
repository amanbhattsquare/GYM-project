from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Enquiry
from django.utils import timezone

class EnquiryForm(forms.ModelForm):

    class Meta:
        model = Enquiry
        exclude = ['gym']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your contact number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your gender'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),
            'source': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select source'}),
            'interested_in': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select interested in'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select status'}),
            'next_follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'enquiry_note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your enquiry note', 'rows': 3}),
        }

    # ⭐ Required fields (industry style)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            'name',
            'mobile_number',
            'gender',
            'age',
            'next_follow_up_date'
        ]

        for field in required_fields:
            self.fields[field].required = True
            self.fields[field].label = f"{self.fields[field].label} *"

    # Name validation
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Name must be at least 3 characters long")
        return name

    #  Contact number validation (India)
    def clean_mobile_number(self):
        contact = self.cleaned_data.get('mobile_number')
        if not re.match(r'^[0-9]\d{9}$', contact):
            raise ValidationError("Enter a valid 10-digit mobile number")
        return contact

    # Age validation
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 16:
            raise ValidationError("Minimum age should be 16 years")
        return age

    # Next follow-up date validation
    def clean_next_follow_up_date(self):
        date = self.cleaned_data.get('next_follow_up_date')
        if date < timezone.now().date():
            raise ValidationError("Follow-up date cannot be in the past")
        return date
