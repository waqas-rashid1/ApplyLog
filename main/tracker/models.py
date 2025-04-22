from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('joined', 'Joined'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    date_applied = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"
