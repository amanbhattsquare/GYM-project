from django import forms
from .models import Member, MedicalHistory, EmergencyContact, MembershipHistory, PersonalTrainer

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'mobile_number', 'email', 'age', 'gender', 'date_of_birth', 'profile_picture', 'address', 'area', 'state', 'city', 'pincode', 'profession', 'sign', 'identity_type', 'identity_no', 'identity_document_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'sign': forms.FileInput(attrs={'class': 'form-control'}),
            'identity_type': forms.TextInput(attrs={'class': 'form-control'}),
            'identity_no': forms.TextInput(attrs={'class': 'form-control'}),
            'identity_document_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False
        self.fields['sign'].required = False
        self.fields['identity_type'].required = False
        self.fields['identity_no'].required = False
        self.fields['identity_document_image'].required = False

class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['condition', 'type', 'since']
        widgets = {
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'since': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(MedicalHistoryForm, self).__init__(*args, **kwargs)
        self.fields['condition'].required = False
        self.fields['type'].required = False
        self.fields['since'].required = False

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'mobile', 'relation']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'relation': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MembershipHistoryForm(forms.ModelForm):
    class Meta:
        model = MembershipHistory
        fields = ['plan', 'registration_fee', 'membership_start_date', 'add_on_days', 'discount', 'total_amount', 'paid_amount', 'payment_mode', 'comment']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'membership_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'add_on_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PersonalTrainerForm(forms.ModelForm):
    class Meta:
        model = PersonalTrainer
        fields = ['trainer', 'months', 'trainer_fee', 'gym_charges', 'pt_start_date', 'discount', 'total_amount', 'paid_amount', 'payment_mode']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'months': forms.NumberInput(attrs={'class': 'form-control'}),
            'trainer_fee': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'gym_charges': forms.NumberInput(attrs={'class': 'form-control'}),
            'pt_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
        }