from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.trainers.models import Trainer


class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    sign = models.ImageField(upload_to='signs/', blank=True, null=True)
    identity_type = models.CharField(max_length=50, null=True, blank=True)
    identity_no = models.CharField(max_length=50, null=True, blank=True)
    identity_document_image = models.ImageField(upload_to='identity_docs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def latest_membership(self):
        return self.membership_history.order_by('-membership_start_date').first()

    @property
    def is_active(self):
        latest = self.latest_membership
        if not latest:
            return False
        return latest.get_end_date() >= timezone.now().date()

class MedicalHistory(models.Model):
    member = models.ForeignKey(Member, related_name='medical_history', on_delete=models.CASCADE)
    condition = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    since = models.DateField()

    def __str__(self):
        return f'{self.member} - {self.condition}'

class EmergencyContact(models.Model):
    member = models.OneToOneField(Member, related_name='emergency_contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    relation = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.member} - {self.name}'

class MembershipHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='membership_history')
    plan = models.ForeignKey('management.MembershipPlan', on_delete=models.CASCADE)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    membership_start_date = models.DateField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.plan}"

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount

    def get_end_date(self):
        duration_parts = self.plan.duration.split('_')
        duration_value = int(duration_parts[0])
        duration_unit = duration_parts[1]

        if duration_unit == 'day' or duration_unit == 'days':
            return self.membership_start_date + timedelta(days=duration_value)
        elif duration_unit == 'week' or duration_unit == 'weeks':
            return self.membership_start_date + timedelta(weeks=duration_value)
        elif duration_unit == 'month' or duration_unit == 'months':
            # This is an approximation, for more accurate calculations, consider using dateutil.relativedelta
            return self.membership_start_date + timedelta(days=30 * duration_value)
        elif duration_unit == 'year' or duration_unit == 'years':
            return self.membership_start_date + timedelta(days=365 * duration_value)
        return None

class PersonalTrainer(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='personal_trainer')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    months = models.PositiveIntegerField()
    trainer_fee = models.DecimalField(max_digits=10, decimal_places=2)
    gym_charges = models.DecimalField(max_digits=10, decimal_places=2)
    pt_start_date = models.DateField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.trainer}"

    def get_end_date(self):
        return self.pt_start_date + timedelta(days=30 * self.months)

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount