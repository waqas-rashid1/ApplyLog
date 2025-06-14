# ApplyLog 📝

ApplyLog is a simple Django-based web application designed to help users track and manage their job applications efficiently. Whether you're applying to internships or full-time positions, ApplyLog helps keep everything organized in one place.

---

## 🔧 Features

- ✅ User authentication (Login/Signup)
- 📌 Add and manage job applications
- 📁 Track job status: Applied, Interviewing, Offered, Rejected, etc.
- 🕒 Date-based tracking and sorting
- 📊 Dashboard to see overall progress
- 🔐 Secure user data with Django’s authentication system

---

## 🛠️ Built With

- [Python 3.11](https://www.python.org/)
- [Django 5.2](https://www.djangoproject.com/)
- [Bootstrap 5 (via crispy-bootstrap5)](https://github.com/django-crispy-forms/crispy-bootstrap5)
- [django-allauth](https://github.com/pennersr/django-allauth) for authentication

---

## 🚀 Getting Started

### 🔑 Prerequisites

- Python 3.10+
- pip
- Virtual environment (optional but recommended)

### ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/WaqasAly/ApplyLog.git
cd ApplyLog

# Set up virtual environment
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Run the server
python manage.py runserver
````

---

## 🖼️ Screenshots

(Add screenshots here: dashboard, form page, status tracking, etc.)

---

## 📁 Folder Structure

```bash
ApplyLog/
│
├── main/                  # Main Django app
├── templates/             # HTML templates
├── static/                # Static files (collected after collectstatic)
├── db.sqlite3             # SQLite database (dev)
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

---

## 📦 Deployment

The app can be deployed on:

* 🐘 cPanel (Python App Setup)
* 🐳 Docker (future-ready)
* ☁️ Platforms like Heroku, Railway, or Render

You can follow the [deployment guide here](#) *(link to Wiki or add steps in README later).*

---

## 🤝 Contributing

Contributions are welcome! If you find bugs or have suggestions, feel free to:

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/yourFeature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/yourFeature`)
5. Open a Pull Request

---

## 🛡 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📫 Contact

Created by [Waqas Rashid](https://github.com/WaqasAly)
For queries, reach out via [LinkedIn](https://www.linkedin.com/in/waqas-rashid1/)

---

```

Let me know if you'd like to add a deployment guide (like for cPanel), contribution guidelines, or screenshots section.
```
