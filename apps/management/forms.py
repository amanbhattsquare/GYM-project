from django import forms
from .models import PackagePlan

class PackagePlanForm(forms.ModelForm):
    class Meta:
        model = PackagePlan
        fields = '__all__'