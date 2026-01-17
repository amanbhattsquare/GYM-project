from django import forms
from .models import Member, MedicalHistory, EmergencyContact, MembershipHistory, PersonalTrainer, AssignDietPlan, AssignWorkoutPlan
from apps.management.models import MembershipPlan, DietPlan, WorkoutPlan
from apps.trainers.models import Trainer
import re

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'mobile_number', 'email', 'age', 'gender',
            'date_of_birth', 'profile_picture', 'address', 'state', 'city',
            'pincode', 'profession', 'sign', 'identity_type', 'identity_no',
            'identity_document_image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number', 'maxlength': '10'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your gender'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your date of birth'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Upload your profile picture'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your area'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your pincode'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your profession'}),
            'sign': forms.FileInput(attrs={'class': 'form-control'}),
            'identity_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your identity type'}),
            'identity_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your identity number'}),
            'identity_document_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False
        self.fields['sign'].required = False
        self.fields['identity_type'].required = False
        self.fields['identity_no'].required = False
        self.fields['identity_document_image'].required = False
        self.fields['date_of_birth'].required = False


        required_fields = [
            'first_name',
            'last_name',
            'mobile_number',
            'gender',
            'age',
        ]

        for field in required_fields:
            self.fields[field].required = True
            self.fields[field].label = f"{self.fields[field].label} *"

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not re.match(r'^[0-9]\d{9}$', mobile_number):
            raise forms.ValidationError("Enter a valid 10-digit mobile number.")
        return mobile_number

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get("date_of_birth")
        if date_of_birth:
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            cleaned_data["age"] = age
        return cleaned_data

class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['condition', 'type', 'since']
        widgets = {
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your condition'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your type'}),
            'since': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your since date'}),
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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}),
            'relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your relation'}),
        }
    def __init__(self, *args, **kwargs):
        super(EmergencyContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['mobile'].required = False
        self.fields['relation'].required = False


class MembershipHistoryForm(forms.ModelForm):
    class Meta:
        model = MembershipHistory
        fields = ['plan', 'registration_fee', 'membership_start_date', 'add_on_days', 'discount', 'total_amount', 'paid_amount', 'payment_mode', 'comment']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your plan'}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registration fee'}),
            'membership_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your membership start date'}),  
            'add_on_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your add on days'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your discount'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Total amount'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your paid amount'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your payment mode'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment'}),
        }

    def __init__(self, *args, **kwargs):
        gym = kwargs.pop('gym', None)
        super(MembershipHistoryForm, self).__init__(*args, **kwargs)
        if gym:
            self.fields['plan'].queryset = MembershipPlan.objects.filter(gym=gym)


class PersonalTrainerForm(forms.ModelForm):
    class Meta:
        model = PersonalTrainer
        fields = ['trainer', 'months', 'trainer_fee', 'gym_charges', 'pt_start_date', 'discount', 'total_amount', 'paid_amount', 'payment_mode']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your months'}),
            'trainer_fee': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Trainer fee'}),
            'gym_charges': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your gym charges'}),
            'pt_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Select your pt start date'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your discount'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Total amount'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your paid amount'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select your payment mode'}),
        }

    def __init__(self, *args, **kwargs):
        gym = kwargs.pop('gym', None)
        super(PersonalTrainerForm, self).__init__(*args, **kwargs)
        if gym:
            self.fields['trainer'].queryset = Trainer.objects.filter(gym=gym)


class AssignDietPlanForm(forms.ModelForm):
    class Meta:
        model = AssignDietPlan
        fields = ['diet_plan']

    def __init__(self, *args, **kwargs):
        gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)
        if gym:
            self.fields['diet_plan'].queryset = DietPlan.objects.filter(gym=gym)


class AssignWorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = AssignWorkoutPlan
        fields = ['workout_plan']

    def __init__(self, *args, **kwargs):
        gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)
        if gym:
            self.fields['workout_plan'].queryset = WorkoutPlan.objects.filter(gym=gym)