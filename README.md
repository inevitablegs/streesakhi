# Streesakhi 🌸
**AI-Driven Maternal Health Risk Assessment and Support Platform**

Streesakhi is a Django-based web application designed to empower maternal healthcare through accessible, intelligent tools tailored for women—especially in North-East India. It provides features like nutrition tracking, pregnancy video guidance, ultrasound image analysis, and personalized profiles.

---

## 🌟 Features

### 👩‍⚕️ User Accounts
- Custom `WomanUser` model with detailed fields (age, gender, emergency contact, etc.)
- Profile picture support
- User authentication (register, login, logout, password change)

### 🧠 AI Tools
- **Pregnancy Video Assistant**: Search and view pregnancy-related videos using AI.
- **Ultrasound Image Analysis**: Upload or capture ultrasound images, view analysis reports.
- **Medicine Analysis** *(in progress)*

### 🍽️ Nutrition Tracker
- Track meals for Morning, Noon, Evening, Night
- Dropdown and manual entry for each slot
- View 7-day summary and generate nutrition reports

### 📸 Camera & Upload Support
- Capture images from camera (mobile/web)
- Upload multiple files with preview and hidden form submission
- Live preview using `<canvas>` and `<video>` with graceful fallbacks

---

## 🛠️ Tech Stack

- **Backend**: Django 4.2
- **Frontend**: Tailwind CSS, HTML5, JavaScript
- **Database**: SQLite (default)
- **Media Handling**: `MEDIA_ROOT` + `MEDIA_URL` for image storage
- **Email**: SMTP via Gmail

---

## 📂 Project Structure

```
streesakhi/
├── maa/                 # Main Django app for maternal care tools
│   ├── templates/maa/   # HTML templates
│   ├── views.py         # View logic
│   ├── models.py        # Custom user model and form handling
├── home/                # Landing/Home app
├── templates/           # Base template directory
├── static/              # Static files (Tailwind CSS via CDN)
├── media/               # User-uploaded images
├── streesakhi/          # Project settings, URLs, WSGI/ASGI
└── db.sqlite3           # Database (for development)
```

---

## 🚀 Installation Guide

### 1. Clone this repo

```bash
git clone https://github.com/your-username/streesakhi.git
cd streesakhi
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser

```bash
python manage.py createsuperuser
```

### 5. Start the server

```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📧 Email Configuration

Set environment variables or modify `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🔒 Custom User Model

In `settings.py`:

```python
AUTH_USER_MODEL = 'maa.WomanUser'
```

---

## 🖼️ Media and Static

Make sure media folders exist:

```bash
mkdir media static
```

In `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

In `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📸 Camera Handling

Used in **Ultrasound Analysis** page:

- `getUserMedia` for accessing camera
- Captures frames to `<canvas>`
- Converts to base64 JPEG for form submission

---

## 📜 License

This project is intended for educational, health, and humanitarian purposes. You may use or modify it with proper credit.

---

## 🙌 Credits

Made by **Ganesh Sonawane (GS)** and team Hackathon-Gcoeara at Hackathon Club.

> “Empowering motherhood with intelligent care.”
