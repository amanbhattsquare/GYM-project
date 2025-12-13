import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
# apps/tenants/models.py
from django.db import models

class Gym(models.Model):
    gym_id = models.CharField(max_length=100, unique=True, editable=False)
    gym_id_prefix = models.CharField(max_length=10, unique=True, null=True)  # Allow null temporarily
    name = models.CharField(max_length=200)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="gym_logos/", null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    landline = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(pre_save, sender=Gym)
def create_gym_id(sender, instance, **kwargs):
    if not instance.gym_id:
        instance.gym_id = f"GYM-{uuid.uuid4().hex[:8].upper()}"

class GymAdmin(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    Phone_number = models.CharField(max_length=15, blank=True, null=True)
    photo = models.ImageField(upload_to="gym_admin_photos/", null=True, blank=True)
    Department = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.gym.name}'

class SubscriptionPlan(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='subscription_plans', null=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField(help_text="Duration in months", default=1)
    features = models.TextField()

    def __str__(self):
        return self.name