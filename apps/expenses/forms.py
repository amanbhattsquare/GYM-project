from django import forms
from .models import Expense
from django.utils import timezone

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        exclude = ['added_by', 'is_deleted', 'gym']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control ', 'placeholder': 'Select category'}),        
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vendor name'}),
            'vendor_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vendor phone'}),
            'vendor_bill_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vendor bill number'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select payment mode'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter transaction ID'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Upload receipt image'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input', 'placeholder': 'Is recurring?'}),
            'recurring_cycle': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select recurring cycle'}),
        }