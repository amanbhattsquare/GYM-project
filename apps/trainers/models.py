from django.db import models
from django.utils import timezone

class Trainer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    joining_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    personal_training_monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    specialization = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='trainers/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name