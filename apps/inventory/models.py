from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateField()
    warranty_expiry_date = models.DateField()

    def __str__(self):
        return self.name

class Maintenance(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Maintenance for {self.equipment.name} on {self.maintenance_date}"