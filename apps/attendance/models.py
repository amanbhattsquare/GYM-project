from django.db import models
from apps.members.models import Member
from apps.trainers.models import Trainer

class MemberAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=False)  # False for absent, True for present

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} - {self.date}"

class TrainerAttendance(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=False)  # False for absent, True for present

    def __str__(self):
        return f"{self.trainer.name} - {self.date}"