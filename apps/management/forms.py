from django import forms
from .models import DietPlan, PackagePlan, WorkoutPlan

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
        }


class PackagePlanForm(forms.ModelForm):
    class Meta:
        model = PackagePlan
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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