from django.db import models
from apps.members.models import Member
from apps.trainers.models import Trainer
from apps.superadmin.models import Gym

from django.utils import timezone

class MemberAttendance(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_records')
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('inside', 'Inside'), ('outside', 'Outside')], default='inside')

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} - {self.check_in_time.date()}"

    @property
    def duration(self):
        if self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f'{hours}h {minutes}m'
        return None

class TrainerAttendance(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='attendance_records')
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('inside', 'Inside'), ('outside', 'Outside')], default='inside')

    def __str__(self):
        return f"{self.trainer.name} - {self.check_in_time.date()}"

    @property
    def duration(self):
        if self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f'{hours}h {minutes}m'
        return None