from django.db import models

# Create your models here.
class PaymentSetting(models.Model):
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    ifsc_code = models.CharField(max_length=255, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    def __str__(self):
        return self.bank_name or "Payment Settings"