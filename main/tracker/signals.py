# tracker/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Applicant

@receiver(post_save, sender=User)
def create_applicant_profile(sender, instance, created, **kwargs):
    if created:
        Applicant.objects.create(
            user=instance,
            name=instance.get_full_name() or instance.username,
            email=instance.email,
            phone="0000000000"
        )
