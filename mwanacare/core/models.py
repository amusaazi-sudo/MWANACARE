from django.db import models
from django.contrib.auth.models import User


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username

class Child(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M','Male'),('F','Female')])

    def __str__(self):
        return f"{self.name} ({self.parent.user.username})"

class Facility(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

class ImmunizationRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    date_given = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.child.name} - {self.vaccine_name}"

class Referral(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    referral_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled')
    ], default='Pending')
    visit_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Referral for {self.child.name} to {self.facility.name}"

class Reminder(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    message = models.TextField()
    due_date = models.DateField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.child.name} on {self.due_date}"
