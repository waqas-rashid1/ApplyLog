# admin.py
from django.contrib import admin
from .models import Application
from .models import Applicant, Job

admin.site.register(Application)
admin.site.register(Job)
admin.site.register(Applicant)