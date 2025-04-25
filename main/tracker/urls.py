from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_application, name='add_application'),
    path('submit_application/', views.submit_application, name='submit_application'),
    path('history/', views.application_history, name='application_history'),
    path('stats/', views.application_stats, name='application_stats'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
