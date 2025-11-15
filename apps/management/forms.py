from django import forms
from .models import DietPlan, PackagePlan

class PackagePlanForm(forms.ModelForm):
    class Meta:
        model = PackagePlan
        fields = '__all__'

class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'target': forms.Select(attrs={'class': 'form-control'}),
            'daily_calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }