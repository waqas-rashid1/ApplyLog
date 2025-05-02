from django.shortcuts import get_object_or_404, render, redirect
from .forms import ApplicationForm, DocumentForm
from django.contrib import messages
from django.db.models import Q
from .models import Application, Applicant, Document, Job
from datetime import date
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractWeekDay
from django.db.models import F, ExpressionWrapper, fields, Avg
from django.db.models.functions import Now
from django.contrib.auth.decorators import login_required
from .models import SavedJob
from .forms import SavedJobForm

def add_application(request):
    form = ApplicationForm()
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('application_success')  # Define this view/template
    return render(request, 'add_application.html', {'form': form, 'today_date': date.today().isoformat()})

@login_required
def application_history(request):
    user = request.user
    applications = Application.objects.filter(applicant__user=user).select_related('applicant', 'job')

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

@login_required
def dashboard(request):
    # applications = Application.objects.select_related('job', 'applicant').all()

    # Get the current logged-in user's applicant record
    applicants = Applicant.objects.filter(user=request.user)
    applications = Application.objects.select_related('job', 'applicant').filter(applicant__in=applicants)

    # --- KPIs ---
    total_apps = applications.count()
    status_counts = applications.values('status').annotate(count=Count('id'))

    # Mapping statuses to easily fetch counts
    status_dict = {entry['status']: entry['count'] for entry in status_counts}

    kpis = [
        {"label": "Total Applications", "value": total_apps, "color": "#ffc107"},
        {"label": "Pending", "value": status_dict.get("pending", 0), "color": "#0dcaf0"},
        {"label": "Interview", "value": status_dict.get("interview", 0), "color": "#0d6efd"},
        {"label": "Offer", "value": status_dict.get("offer", 0), "color": "#6610f2"},
        {"label": "Joined", "value": status_dict.get("joined", 0), "color": "#198754"},
        {"label": "Rejected", "value": status_dict.get("rejected", 0), "color": "#dc3545"},
        {"label": "Dropped", "value": status_dict.get("dropped", 0), "color": "#6c757d"},
    ]

    # --- Insights ---
    monthly_counts = (
        applications
        .values_list('date_applied__month')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    active_month_num = monthly_counts[0][0] if monthly_counts else None
    active_month = calendar.month_name[active_month_num] if active_month_num else "N/A"

    insights = {
        "active_month": active_month,
        "avg_response_time": 5.2,  # Replace with actual logic if needed
        "best_category": "LinkedIn",  # Replace with logic if available
        "goal_completion": round((total_apps / 100) * 100)  # If 100 is your goal
    }

    # --- Recent Applications ---
    recent_apps = applications.order_by('-date_applied')[:5]

    status_badge = {
        'pending': 'warning',
        'applied': 'primary',
        'interview': 'info',
        'offer': 'success',
        'joined': 'success',
        'rejected': 'danger',
        'dropped': 'secondary',
    }

    recent_applications = []
    for app in recent_apps:
        recent_applications.append({
            "company": app.job.company if app.job else "N/A",
            "position": app.job.title if app.job else "N/A",
            "status": app.status.title(),
            "status_class": status_badge.get(app.status, 'secondary'),
            "date": app.date_applied.strftime("%Y-%m-%d")
        })

    # --- Pie Chart Data ---
    pie_data = applications.values('status').annotate(count=Count('id'))
    pie_labels = [f'"{entry["status"].title()}"' for entry in pie_data]
    pie_counts = [entry["count"] for entry in pie_data]

    # --- Line Chart Data ---
    months = range(1, 13)
    month_labels = [f'"{calendar.month_abbr[m]}"' for m in months]
    month_counts = [
        applications.filter(date_applied__month=m).count() for m in months
    ]

    context = {
        "kpis": kpis,
        "insights": insights,
        "recent_applications": recent_applications,
        "pie_chart": {
            "labels": f"[{', '.join(pie_labels)}]",
            "data": pie_counts
        },
        "line_chart": {
            "labels": f"[{', '.join(month_labels)}]",
            "data": month_counts
        },
        'applications': applications,
    }

    return render(request, 'dashboard.html', context)

@login_required
def submit_application(request):
    if request.method == 'POST':
        name = request.POST.get('applicant_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        position = request.POST.get('position_applied')
        company = request.POST.get('company_name')
        website_link = request.POST.get('website_link') or "https://example.com"
        source = request.POST.get('source') or "Not specified"

        date_applied = request.POST.get('date_applied') or timezone.now().date()
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')

        # 1. Get or create Applicant — also link to logged-in user
        applicant, _ = Applicant.objects.get_or_create(
            name=name,
            email=email,
            phone=phone,
            user=request.user
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

        return redirect('dashboard')

    return render(request, 'add_application.html')

# def application_stats(request):
#     # Total applications
#     total = Application.objects.count()
    
#     # Status-based counts
#     pending = Application.objects.filter(status='pending').count()
#     applied = Application.objects.filter(status='applied').count()
#     interview = Application.objects.filter(status='interview').count()
#     offer = Application.objects.filter(status='offer').count()
#     rejected = Application.objects.filter(status='rejected').count()
#     joined = Application.objects.filter(status='joined').count()
#     dropped = Application.objects.filter(status='dropped').count()

#     # Monthly application trend (last 6 months)
#     monthly_data = Application.objects.annotate(month=TruncMonth('date_applied')) \
#         .values('month') \
#         .annotate(count=Count('id')) \
#         .order_by('month')

#     # Transform for chart
#     months = []
#     counts = []
#     for entry in monthly_data:
#         month = entry['month']
#         months.append(month.strftime('%b'))  # Jan, Feb...
#         counts.append(entry['count'])

#     most_active_month = (
#         Application.objects
#         .annotate(month=ExtractMonth('date_applied'))
#         .values('month')
#         .annotate(count=Count('id'))
#         .order_by('-count')
#         .first()
#     )

#     most_active_month_name = calendar.month_name[most_active_month['month']] if most_active_month else "N/A"

#     # Total applications by job title
#     total_by_title = (
#         Application.objects
#         .filter(job__isnull=False)
#         .values('job__title')
#         .annotate(total=Count('id'))
#     )

#     # Accepted applications by job title
#     accepted_by_title = (
#         Application.objects
#         .filter(status='offer', job__isnull=False)
#         .values('job__title')
#         .annotate(accepted=Count('id'))
#     )

#     # Create a dictionary to calculate acceptance rate
#     acceptance_data = {}
#     for t in total_by_title:
#         title = t['job__title']
#         total = t['total']
#         accepted = next((a['accepted'] for a in accepted_by_title if a['job__title'] == title), 0)
#         if total > 0:
#             acceptance_data[title] = accepted / total

#     best_acceptance_title = max(acceptance_data, key=acceptance_data.get, default="N/A")

#     weekday_interviews = (
#         Application.objects
#         .filter(status='interview')
#         .annotate(weekday=ExtractWeekDay('date_applied'))
#         .values('weekday')
#         .annotate(count=Count('id'))
#         .order_by('-count')
#         .first()
#     )

#     # Django's ExtractWeekDay: Sunday = 1, Monday = 2, ..., Saturday = 7
#     weekday_map = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
#     interview_day = weekday_map[weekday_interviews['weekday'] - 1] if weekday_interviews else "N/A"


#     # Calculate duration from application to current date (or actual response date if available)
#     response_times = (
#         Application.objects
#         .filter(status__in=['offer', 'rejected'])
#         .annotate(duration=ExpressionWrapper(
#             Now() - F('date_applied'), output_field=fields.DurationField())
#         )
#     )

#     # Compute average in days
#     avg_response_time_days = response_times.aggregate(
#         avg=Avg('duration')
#     )['avg'].days if response_times.exists() else "N/A"

#     context = {
#         'total': total,
#         'pending': pending,
#         'interviewed': interview,
#         'accepted': offer + joined,  # you can customize this logic
#         'rejected': rejected,
#         'labels': months,
#         'counts': counts,
#         'most_active_month': most_active_month_name,
#         'best_acceptance_title': best_acceptance_title,
#         'interview_day': interview_day,
#         'avg_response_time': avg_response_time_days,
#     }
    

#     return render(request, 'application_stats.html', context)

@login_required
def document_library(request):
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            return redirect('document_library')
    else:
        form = DocumentForm()

    return render(request, 'document_library.html', {'form': form, 'documents': documents})

@login_required
def wishlist_view(request):
    saved_jobs = SavedJob.objects.filter(user=request.user).order_by('-saved_at')
    form = SavedJobForm()

    if request.method == 'POST':
        form = SavedJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            return redirect('wishlist')

    return render(request, 'wishlist.html', {'form': form, 'saved_jobs': saved_jobs})

@login_required
def delete_saved_job(request, job_id):
    job = get_object_or_404(SavedJob, id=job_id, user=request.user)
    job.delete()
    return redirect('wishlist')

@login_required
def mark_job_applied(request, job_id):
    job = get_object_or_404(SavedJob, pk=job_id)
    job.applied = True
    job.save()
    return redirect('wishlist')