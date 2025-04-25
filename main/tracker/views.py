from django.shortcuts import render, redirect
from .forms import ApplicationForm
from django.contrib import messages
from django.db.models import Q
from .models import Application, Applicant, Job
from datetime import date
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractWeekDay
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Now

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
        name = request.POST.get('applicant_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        position = request.POST.get('position_applied')
        company = request.POST.get('company_name')
        website_link = request.POST.get('website_link') or "https://example.com"  # fallback if not provided
        source = request.POST.get('source') or "Not specified"

        date_applied = request.POST.get('date_applied') or timezone.now().date()
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')

        # 1. Get or create Applicant
        applicant, _ = Applicant.objects.get_or_create(
            name=name,
            email=email,
            phone=phone,
        )

        # 2. Get or create Job
        job, _ = Job.objects.get_or_create(
            title=position,
            company=company,
            website_link=website_link,
            source=source
        )

        # 3. Create Application
        Application.objects.create(
            applicant=applicant,
            job=job,
            date_applied=date_applied,
            status=status,
            notes=notes,
            cover_letter=cover_letter,
            resume=resume,
        )

        return redirect('dashboard')  # or wherever you want to redirect

    return render(request, 'add_application.html')

def application_stats(request):
    # Total applications
    total = Application.objects.count()
    
    # Status-based counts
    pending = Application.objects.filter(status='pending').count()
    applied = Application.objects.filter(status='applied').count()
    interview = Application.objects.filter(status='interview').count()
    offer = Application.objects.filter(status='offer').count()
    rejected = Application.objects.filter(status='rejected').count()
    joined = Application.objects.filter(status='joined').count()
    dropped = Application.objects.filter(status='dropped').count()

    # Monthly application trend (last 6 months)
    monthly_data = Application.objects.annotate(month=TruncMonth('date_applied')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')

    # Transform for chart
    months = []
    counts = []
    for entry in monthly_data:
        month = entry['month']
        months.append(month.strftime('%b'))  # Jan, Feb...
        counts.append(entry['count'])

    most_active_month = (
        Application.objects
        .annotate(month=ExtractMonth('date_applied'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    most_active_month_name = calendar.month_name[most_active_month['month']] if most_active_month else "N/A"

    # Total applications by job title
    total_by_title = (
        Application.objects
        .filter(job__isnull=False)
        .values('job__title')
        .annotate(total=Count('id'))
    )

    # Accepted applications by job title
    accepted_by_title = (
        Application.objects
        .filter(status='offer', job__isnull=False)
        .values('job__title')
        .annotate(accepted=Count('id'))
    )

    # Create a dictionary to calculate acceptance rate
    acceptance_data = {}
    for t in total_by_title:
        title = t['job__title']
        total = t['total']
        accepted = next((a['accepted'] for a in accepted_by_title if a['job__title'] == title), 0)
        if total > 0:
            acceptance_data[title] = accepted / total

    best_acceptance_title = max(acceptance_data, key=acceptance_data.get, default="N/A")

    weekday_interviews = (
        Application.objects
        .filter(status='interview')
        .annotate(weekday=ExtractWeekDay('date_applied'))
        .values('weekday')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    # Django's ExtractWeekDay: Sunday = 1, Monday = 2, ..., Saturday = 7
    weekday_map = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    interview_day = weekday_map[weekday_interviews['weekday'] - 1] if weekday_interviews else "N/A"


    # Calculate duration from application to current date (or actual response date if available)
    response_times = (
        Application.objects
        .filter(status__in=['offer', 'rejected'])
        .annotate(duration=ExpressionWrapper(
            Now() - F('date_applied'), output_field=fields.DurationField())
        )
    )

    # Compute average in days
    avg_response_time_days = response_times.aggregate(
        avg=Avg('duration')
    )['avg'].days if response_times.exists() else "N/A"

    context = {
        'total': total,
        'pending': pending,
        'interviewed': interview,
        'accepted': offer + joined,  # you can customize this logic
        'rejected': rejected,
        'labels': months,
        'counts': counts,
        'most_active_month': most_active_month_name,
        'best_acceptance_title': best_acceptance_title,
        'interview_day': interview_day,
        'avg_response_time': avg_response_time_days,
    }
    

    return render(request, 'application_stats.html', context)
