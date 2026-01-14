from django import forms
from .models import DietPlan, MembershipPlan, WorkoutPlan

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        exclude = ['gym']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your duration in minutes'}),
            'difficulty': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your difficulty'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'created_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter creator name'}),
        }


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        exclude = ['gym']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your title'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your amount'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your discount'}),
            'duration': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your duration'}),
            'add_on_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your add-on days'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your description'}),
        }

class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        exclude = ['gym']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'target': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your target'}),
            'daily_calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your daily calories'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your duration in weeks'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'created_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter creator name'}),
        }