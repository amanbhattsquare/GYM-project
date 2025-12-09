from django.db import models
from apps.members.models import Member
from apps.superadmin.models import Gym

class Payment(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True)
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('other', 'Other'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'Payment of {self.amount} for {self.member} on {self.payment_date.strftime("%Y-%m-%d")}'