from django import forms
from .models import Item, StockLog, Equipment, Maintenance

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'name', 'category', 'sku', 'unit', 'current_stock', 'supplier', 
            'purchase_price', 'selling_price', 'expiry_date', 'image', 'description'
        ]
        labels = {
            'current_stock': 'Stock Quantity',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Whey Protein, Yoga Mat'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., WP-001'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 100'}),

            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Global Fitness', 'list': 'supplier-list'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'A brief description of the item'}),
        }

class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockLog
        fields = [
            'item', 'quantity', 'reason', 'issued_to', 'phone_number', 'date', 'remarks'
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'issued_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., "John Doe"'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 9876543210'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes...'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        item = self.cleaned_data.get('item')
        if item and quantity > item.current_stock:
            raise forms.ValidationError(f"Not enough stock. Only {item.current_stock} items available.")
        return quantity

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name', 'category', 'brand', 'model', 'serial_number', 'supplier',
            'purchase_date', 'purchase_cost', 'warranty_period', 'installation_date',
            'location', 'expected_life', 'notes', 'image', 'condition', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Treadmill, Dumbbell Set'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Life Fitness, Precor'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., T5, 956i'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SN-12345'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Global Fitness', 'list': 'supplier-list'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'warranty_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 years'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cardio Section, Weight Room'}),
            'expected_life': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10 years'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.choices = Item.CATEGORY_CHOICES


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'equipment', 'maintenance_type', 'issue_description', 'service_date',
            'technician_name', 'cost', 'next_service_date', 'status', 'downtime_days'
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'issue_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the issue...'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'next_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'downtime_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2'}),
        }