from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    sign = models.ImageField(upload_to='signs/', blank=True, null=True)
    identity_type = models.CharField(max_length=50, null=True, blank=True)
    identity_no = models.CharField(max_length=50, null=True, blank=True)
    identity_document_image = models.ImageField(upload_to='identity_docs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class MedicalHistory(models.Model):
    member = models.ForeignKey(Member, related_name='medical_history', on_delete=models.CASCADE)
    condition = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    since = models.DateField()

    def __str__(self):
        return f'{self.member} - {self.condition}'

class EmergencyContact(models.Model):
    member = models.OneToOneField(Member, related_name='emergency_contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    relation = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.member} - {self.name}'

class MembershipHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='membership_history')
    plan = models.ForeignKey('management.MembershipPlan', on_delete=models.CASCADE)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    joining_date = models.DateField()
    membership_start_date = models.DateField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.plan}"