from django.db import models
from django.contrib.auth.models import User


# Applicant Model
class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.phone}" 


# Job Model
class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    website_link = models.URLField(max_length=200)
    source = models.CharField(max_length=255)  # From where the job was applied (e.g., LinkedIn, Indeed, etc.)

    def __str__(self):
        return f"{self.title} at {self.company} ({self.source}) - {self.website_link})" 


# Application Model
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

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    date_applied = models.DateField()  # Application Date
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)  # Additional Notes
    cover_letter = models.TextField(blank=True)  # Cover Letter
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # Resume file upload
    deadline = models.DateField(null=True, blank=True)  # Application Deadline

    def __str__(self):
        applicant_name = self.applicant.name if self.applicant else "No Applicant"
        job_title = self.job.title if self.job else "No Job"
        job_company = self.job.company if self.job else "No Company"
        return f"{applicant_name} - {job_title} at {job_company}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('Resume', 'Resume'),
        ('Cover Letter', 'Cover Letter'),
        ('Portfolio', 'Portfolio'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='Resume')
    file = models.FileField(upload_to='documents/')
    company_tag = models.CharField(max_length=100, blank=True)
    job_role_tag = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.document_type})"

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    job_link = models.URLField()
    deadline = models.DateField()
    notes = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    applied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job_title} at {self.company}"
