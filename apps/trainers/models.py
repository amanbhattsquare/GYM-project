from django.db import models
from django.utils import timezone
from apps.superadmin.models import Gym

class Trainer(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True)
    trainer_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    personal_training_monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    specialization = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='trainers/photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.trainer_id:
            current_year = timezone.now().strftime('%y')
            last_trainer = Trainer.objects.filter(trainer_id__startswith=f'TRN-{current_year}').order_by('-trainer_id').first()
            if last_trainer and last_trainer.trainer_id:
                last_id_int = int(last_trainer.trainer_id.split('-')[-1])
                new_id_int = last_id_int + 1
            else:
                new_id_int = 1
            self.trainer_id = f'TRN-{current_year}-{new_id_int:06d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name