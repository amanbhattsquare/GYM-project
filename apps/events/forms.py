from django import forms
from .models import Event, EventParticipant

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EventParticipantForm(forms.ModelForm):
    class Meta:
        model = EventParticipant
        exclude = ['event', 'registered_at', 'ip_address', 'status', 'payment_status', 'registration_source']