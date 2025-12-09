# apps/tenants/models.py
from django.db import models

class Gym(models.Model):
    name = models.CharField(max_length=200)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="gym_logos/", null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    landline = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GymAdmin(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.gym.name}'