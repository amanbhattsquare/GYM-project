from django import forms
from django.contrib.auth.models import User
from .models import Gym

class GymForm(forms.ModelForm):

    class Meta:
        model = Gym
        fields = ['name', 'slogan', 'logo', 'address', 'phone', 'landline', 'email', 'website', 'note']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def __init__(self, *args, **kwargs):
        super(GymForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class GymAdminForm(forms.Form):
    name= forms.CharField(max_length=150, required=True)
    Phone_number = forms.CharField(max_length=15, required=True)    
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})