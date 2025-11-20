from django.db import models
from apps.members.models import Member

class Payment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES)

    def __str__(self):
        return f'Payment of {self.amount} for {self.member} on {self.payment_date.strftime("%Y-%m-%d")}'