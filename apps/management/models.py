from django.db import models

class PackagePlan(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_months = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    

class DietPlan(models.Model):
    TARGET_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('fat_loss', 'Fat Loss'),
    ]

    name = models.CharField(max_length=100)
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='weight_loss')
    daily_calories = models.PositiveIntegerField(default=0)
    duration_weeks = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name