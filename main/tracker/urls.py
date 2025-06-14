from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_application, name='add_application'),
    path('submit_application/', views.submit_application, name='submit_application'),
    path('history/', views.application_history, name='application_history'),
    # path('stats/', views.application_stats, name='application_stats'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('library/', views.document_library, name='document_library'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/delete/<int:job_id>/', views.delete_saved_job, name='delete_saved_job'),
    path('job/applied/<int:job_id>/', views.mark_job_applied, name='mark_job_applied'),
    path('update-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
] 
