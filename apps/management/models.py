from django.db import models

class PackagePlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_months = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name