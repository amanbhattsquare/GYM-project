from django import forms
from .models import Trainer

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['name', 'email', 'phone', 'address', 'joining_date', 'salary', 'personal_training_monthly_amount', 'specialization', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter salary'}),
            'personal_training_monthly_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter personal training monthly amount'}),
            'specialization': forms.Select(attrs={'class': 'form-control'}, choices=Trainer.SPECIALIZATION_CHOICES),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }