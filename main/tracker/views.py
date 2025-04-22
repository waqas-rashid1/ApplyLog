from django.shortcuts import render, redirect
from .forms import ApplicationForm
from django.contrib import messages
from django.db.models import Q
from .models import Application
from datetime import date

def add_application(request):
    form = ApplicationForm()
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('application_success')  # Define this view/template
    return render(request, 'add_application.html', {'form': form, 'today_date': date.today().isoformat()})

def application_history(request):
    # Get search query and filter value from GET request
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # Filter applications based on search query and status
    applications = Application.objects.all()

    if search_query:
        applications = applications.filter(
            Q(applicant_name__icontains=search_query) |
            Q(position_applied__icontains=search_query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications
    }

    return render(request, 'application_history.html', context)

def application_stats(request):
    total = Application.objects.count()
    pending = Application.objects.filter(status='Pending').count()
    interviewed = Application.objects.filter(status='Interviewed').count()
    accepted = Application.objects.filter(status='Accepted').count()
    rejected = Application.objects.filter(status='Rejected').count()

    context = {
        'total': total,
        'pending': pending,
        'interviewed': interviewed,
        'accepted': accepted,
        'rejected': rejected,
    }

    return render(request, 'application_stats.html', context)


def stats_view(request):
    # Replace with actual values from DB later
    funnel_steps = ["Applied", "Shortlisted", "Interviewed", "Offered", "Joined", "Dropped"]
    context = {
        'funnel_steps': funnel_steps,
        # optionally pass dummy values too
    }
    return render(request, 'application_stats.html', context)

def dashboard(request):
    applications = Application.objects.all().order_by('-date_applied')
    context = {
        'total': applications.count(),
        'pending': applications.filter(status='Pending').count(),
        'accepted': applications.filter(status='Accepted').count(),
        'rejected': applications.filter(status='Rejected').count(),
        'recent_apps': applications[:5],  # latest 5 entries
    }
    return render(request, 'dashboard.html', context)

def submit_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('dashboard')  # Redirect after successful submission
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'today_date': date.today().isoformat(), 
    }
    return render(request, 'add_application.html', context)