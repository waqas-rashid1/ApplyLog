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
from .utils import fetch_job_details, detect_job_source


def add_application(request):
    form = ApplicationForm()
    applicant_data = None

    # Fetch existing applicant data for the logged-in user (if available)
    if request.user.is_authenticated:
        applicant_data = Applicant.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('application_success')  # Or wherever you want to redirect after success

    return render(request, 'add_application.html', {
        'form': form,
        'today_date': date.today().isoformat(),
        'applicant': applicant_data,
    })

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
        {"label": "Applied", "value": status_dict.get("applied", 0), "color": "#fd7e14"},
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
    recent_apps = applications.order_by('-date_applied')[:10]

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
    saved_job = get_object_or_404(SavedJob, id=job_id, user=request.user)

    saved_job.applied = True
    saved_job.save()

    job_obj, _ = Job.objects.get_or_create(
        title=saved_job.job_title,
        company=saved_job.company,
        website_link=saved_job.job_link,
        defaults={'source': 'wishlist'}
    )

    # Use .filter().first() to avoid MultipleObjectsReturned
    applicant = Applicant.objects.filter(user=request.user).first()
    if not applicant:
        applicant = Applicant.objects.create(
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            phone="N/A"
        )

    # Create Application
    Application.objects.get_or_create(
        applicant=applicant,
        job=job_obj,
        defaults={
            'date_applied': timezone.now().date(),
            'status': 'applied',
            'notes': saved_job.notes,
        }
    )

    return redirect('wishlist')

from django.shortcuts import get_object_or_404, redirect
from .models import Application

def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(Application, pk=application_id)
        new_status = request.POST.get('status')
        if new_status in dict(application.STATUS_CHOICES):  # Optional: Validate status
            application.status = new_status
            application.save()
    return redirect('application_history')  # or wherever your table view is


from django.http import JsonResponse
from .utils import detect_job_source, fetch_job_details

def fetch_job_info(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({"error": "Missing URL"}, status=400)

    details = fetch_job_details(url)
    details["source"] = detect_job_source(url)
    return JsonResponse(details)


#matching score view
import os
import re
import fitz  # PyMuPDF
from .models import SavedJob
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
MIN_SCORE_THRESHOLD = 35

# Extract a clean set of skill-related words from all job notes
def get_dynamic_skill_keywords():
    all_notes = " ".join(job.notes.lower() for job in SavedJob.objects.all() if job.notes)
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9.+#-]{1,}\b', all_notes)  # basic keyword filter
    common = Counter(words).most_common(100)
    return {word for word, freq in common if len(word) > 2}  # filter short/noise

def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as doc:
        return "\n".join(page.get_text() for page in doc)

def extract_skills(text, skill_keywords):
    text = text.lower()
    return {skill for skill in skill_keywords if skill in text}

def get_similarity(a, b):
    a_emb = model.encode(a, convert_to_tensor=True)
    b_emb = model.encode(b, convert_to_tensor=True)
    return util.cos_sim(a_emb, b_emb)[0][0].item()

def score_job(resume_text, resume_skills, job, skill_keywords):
    job_title = job.job_title.strip()
    job_desc = job.notes.strip() or job_title

    # 1. Title similarity (30%)
    title_score = get_similarity(job_title, resume_text) * 30

    # 2. Skills match (40%)
    job_keywords = extract_skills(job_desc, skill_keywords)
    common_skills = resume_skills.intersection(job_keywords)
    skill_score = (len(common_skills) / len(job_keywords) if job_keywords else 0) * 40

    # 3. Experience/desc match (15%)
    desc_score = get_similarity(job_desc, resume_text) * 15

    # 4. Keyword frequency match (15%)
    frequency_score = sum(resume_text.lower().count(skill) for skill in job_keywords)
    freq_score = min(frequency_score, 10) / 10 * 15

    total_score = title_score + skill_score + desc_score + freq_score
    return round(total_score, 2)

@csrf_exempt
def upload_resume_and_match(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume = request.FILES['resume']
        fs = FileSystemStorage()
        filename = fs.save(resume.name, resume)
        file_path = fs.path(filename)

        try:
            resume_text = extract_text_from_pdf(file_path)
            skill_keywords = get_dynamic_skill_keywords()
            resume_skills = extract_skills(resume_text, skill_keywords)

            results = []
            for job in SavedJob.objects.all():
                score = score_job(resume_text, resume_skills, job, skill_keywords)
                if score >= MIN_SCORE_THRESHOLD:
                    results.append({
                        'title': job.job_title,
                        'company': job.company,
                        'notes': job.notes,
                        'score': score
                    })

            results.sort(key=lambda x: x['score'], reverse=True)
            return JsonResponse({'matches': results})
        finally:
            os.remove(file_path)

    return JsonResponse({'error': 'No resume uploaded'}, status=400)


# live job feed views
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = "ac0fa29d81mshbb893cbbbbf1eb5p15b4abjsn486de655cb57"

@require_GET
def live_job_list(request):
    title = request.GET.get("title", "").strip()
    location = request.GET.get("location", "").strip()
    job_type = request.GET.get("type", "").strip()

    if not title:
        return JsonResponse({"error": "Please provide a job title"}, status=400)

    # Build query string
    query_parts = [title]
    if location:
        query_parts.append(location)
    if job_type:
        query_parts.append(job_type)

    query = " ".join(query_parts)

    try:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "page": "1",
            "num_pages": "1"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return JsonResponse({"error": "API request failed"}, status=response.status_code)

        data = response.json()
        jobs = []

        for job in data.get("data", [])[:10]:
            jobs.append({
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": job.get("job_city") or job.get("job_country", "Remote"),
                "type": job.get("job_offer_type", "N/A") or job.get("job_is_remote", "Remote"),
                "link": job.get("job_apply_link", "#")
            })

        return JsonResponse({"results": jobs})
    except Exception as e:
        logger.error(f"Job fetch error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Job API failed", "details": str(e)}, status=500)

def live_job_list_view(request):
    return render(request, 'jobs_list.html')


#smart suggestions according to job title of wishlist
import requests
from django.http import JsonResponse
from .models import SavedJob
from django.contrib.auth.decorators import login_required

@login_required
def smart_suggestions_all(request):
    user = request.user
    saved_titles = SavedJob.objects.filter(user=user).values_list('job_title', flat=True).distinct()

    suggestions = []
    headers = {
        "x-rapidapi-key": "ac0fa29d81mshbb893cbbbbf1eb5p15b4abjsn486de655cb57",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    for title in saved_titles:
        url = f"https://jsearch.p.rapidapi.com/search?query={title}&page=1&num_pages=1"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for job in data.get("data", []):
                    suggestions.append({
                        "title": job.get("job_title"),
                        "company": job.get("employer_name"),
                        "location": job.get("job_city") or job.get("job_country") or "N/A",
                        "link": job.get("job_apply_link"),
                        "source": "RapidAPI"
                    })
        except Exception as e:
            print(f"Error fetching jobs for title '{title}':", str(e))
            continue

    return JsonResponse({"suggestions": suggestions})


#resume matching view
@login_required
def resume_matching(request):
    #render the resume matching page
    return render(request, 'resume_match.html')