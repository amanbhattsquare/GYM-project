from django import forms
from .models import Enquiry

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['gym']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your contact number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your gender'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your date of birth'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),
            'source': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your source'}),    
            'interested_in': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your interested in'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your status'}),
            'next_follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your next follow up date'}),
            'enquiry_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your enquiry note'}),   
        }