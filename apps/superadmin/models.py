from django.db import models
from django.contrib.auth.models import User

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()

    def __str__(self):
        return self.name

class Gym(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='gym_logos/', blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    domain_url = models.CharField(max_length=255, blank=True, null=True, unique=True)
    timezone = models.CharField(max_length=100, default='UTC')


    def __str__(self):
        return self.name

class Subscription(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.gym.name} - {self.plan}"