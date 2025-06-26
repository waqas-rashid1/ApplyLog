# Elevatr 🚀

Elevatr is a Django-based web application that helps users track, discover, and manage job applications in one place.  
From saving job opportunities to tracking application statuses, Elevatr helps users stay organized and proactive in their job search journey.

---

## 🎯 Core Features

- ✅ **User Authentication** (Signup / Login)
- 📌 **Add and Manage Job Applications**
- 🗂️ **Status Tracking:** Applied, Interviewing, Offered, Rejected, etc.
- 🕒 **Date-based Tracking and Sorting**
- 📊 **User Dashboard:** View progress and job status breakdown
- ⭐ **Wishlist:** Save jobs for later
- ✅ **Applied Jobs Tracker:** Keep record of applied positions
- 🔍 **Live Job Feed:** Search for real-time job listings (using RapidAPI Job Search API) with filters (title, location, remote/on-site)
- 💡 **Smart Job Suggestions:** Personalized job recommendations based on user wishlist
- 🌐 **Google Analytics Integrated:** Track user activity and website traffic
- ⚡ **MySQL Database Support:** Production-ready backend with MySQL (migrated from SQLite)
- 🔐 **Secure with Django Authentication**

---

## 🛠️ Built With

- [Python 3.11](https://www.python.org/)
- [Django 5.2](https://www.djangoproject.com/)
- [MySQL](https://www.mysql.com/) for production database
- [Bootstrap 5 (via crispy-bootstrap5)](https://github.com/django-crispy-forms/crispy-bootstrap5)
- [django-allauth](https://github.com/pennersr/django-allauth) for user authentication
- [Sentence Transformers (NLP)](https://www.sbert.net/) for smart suggestions feature
- [RapidAPI - JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/) for Live Job Feed

---

## 🚀 Getting Started

### 🔑 Prerequisites

- Python 3.10+
- pip
- MySQL Server (8.x or higher)
- Virtual environment (recommended)

---

### ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/waqas-rashid1/applylog.git
cd applylog

# Set up virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update your MySQL DATABASES config in settings.py
# (Use your MySQL credentials)

# Run migrations
python manage.py migrate

# Load initial data if needed
python manage.py loaddata data_backup.json  # Optional

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 🌍 Deployment
Currently live at: [https://elevatr.codehub.pk/](https://elevatr.codehub.pk/)

### Supported Deployment Options:
✅ VPS (Ubuntu with Apache/Nginx + Gunicorn)

✅ MySQL Production Database

✅ GitHub → VPS CI/CD Pipeline (Webhook or GitHub Actions-based deployment flow)

✅ Google Analytics Integrated

---

## ⚙️ CI/CD Workflow
Latest production deployments are auto-triggered from GitHub → VPS using Webhooks.
Every push to the main branch auto-updates the live site.

✅ Folder Structure
```
Elevatr/
│
├── main/                  # Main Django project
├── tracker/               # Django app (jobs, wishlist, etc.)
├── templates/             # HTML templates
├── static/                # Static files (after collectstatic)
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

---

## 📈 Analytics
Google Analytics (GA4) tracking code is embedded in base.html.
You can view site traffic and user engagement on your Google Analytics Dashboard.

---

## 🤝 Contributing
Contributions are welcome!
```
Fork the repository

Create your feature branch:
git checkout -b feature/YourFeature

Commit your changes:
git commit -m "Add new feature"

Push to your branch:
git push origin feature/YourFeature

Open a Pull Request
```

---

## 🛡️ License
Distributed under the MIT License. See LICENSE for details.

---

## 📫 Contact
Built with ❤️ by [Waqas Rashid](https://www.linkedin.com/in/waqas-rashid1)
For queries or collaborations:
LinkedIn → [waqas-rashid1](https://www.linkedin.com/in/waqas-rashid1)
