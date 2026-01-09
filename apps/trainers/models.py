from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
import random
from apps.superadmin.models import Gym

class Trainer(models.Model):
    SPECIALIZATION_CHOICES = [
    ('CROSSFIT', 'CrossFit'),
    ('PT', 'Personal Trainer'),
    ('ST', 'Strength Training'),
    ('WL', 'Weight Loss'),
    ('MB', 'Muscle Building'),
    ('FT', 'Functional Training'),
    ('HIIT', 'HIIT'),
    ('YOGA', 'Yoga'),
    ('ZUMBA', 'Zumba'),
    ('CARDIO', 'Cardio Training'),
    ('REHAB', 'Rehabilitation'),
    ('NUTRITION', 'Nutrition Coach'),
    ('SENIOR', 'Senior Fitness Trainer'),
    ('OTHER', 'Other'),
]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True)
    trainer_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    personal_training_monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, )
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, default='CROSSFIT')
    photo = models.ImageField(upload_to='trainers/photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        unique_together = [['gym', 'phone'], ['gym', 'email']]

@receiver(pre_save, sender=Trainer)
def create_trainer_id(sender, instance, **kwargs):
    if not instance.trainer_id:
        gym_id_part = "GD"  # Default value
        if instance.gym and instance.gym.gym_id_prefix:
            gym_id_part = instance.gym.gym_id_prefix

        present_year = timezone.now().strftime('%y')
        random_number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        instance.trainer_id = f"{gym_id_part}-TRN-{present_year}-{random_number}"