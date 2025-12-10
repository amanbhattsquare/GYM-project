from django import forms
from .models import Expense
from django.utils import timezone

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        exclude = ['added_by', 'is_deleted', 'gym']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_bill_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurring_cycle': forms.Select(attrs={'class': 'form-select'}),
        }