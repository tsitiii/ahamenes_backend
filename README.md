# Ahamenes Backend API

This is the backend API for the GDG Ahamenes project, built with Django and Django Rest Framework (DRF). It provides endpoints for managing user accounts, teams, projects, events, and blog posts.

## 🚀 Features

- **Authentication**: Secure user authentication using JSON Web Tokens (JWT).
- **Team Management**: Create and manage teams, including membership applications.
- **Project Showcase**: Display projects associated with teams, capable of handling media uploads (images and files via **Cloudinary**).
- **Events**: Manage event creation and user registrations.
- **Blog**: A blogging system with support for posts, comments, and featured images (via **Cloudinary**).
- **API Documentation**: Auto-generated interactive API documentation using **Swagger UI** and **ReDoc** (via **drf-spectacular**).
- **Deployment Ready**: Configured for deployment on **Render** (using **Gunicorn**, **Whitenoise**, and **build.sh**).

## 🛠 Tech Stack

- **Framework**: Django 5.2, Django Rest Framework 3.16
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Authentication**: djangorestframework-simplejwt (JWT)
- **Storage**: Cloudinary (Image/File Uploads)
- **Documentation**: drf-spectacular (Swagger/OpenAPI 3.0)
- **Server**: Gunicorn
- **Static Files**: Whitenoise

## 💻 Local Development Setup

Follow these steps to set up the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ahamenes_backend.git
cd ahamenes_backend
```

### 2. Create and activate a Virtual Environment

```bash
# Windows
python -m venv env
.\env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create and Configure Environment Variables

Create a `.env` file in the root directory (same level as `manage.py`) and add the following:

```env
# Application Settings
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=*

# Database (Optional for local, defaults to SQLite if not set)
# DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Cloudinary Config (Required for image uploads)
cloud_name=your_cloud_name
api_key=your_api_key
api_secret=your_api_secret
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## 📖 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)
- **Raw Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## 🚀 Deployment (Render)

This project is configured for deployment on [Render](https://render.com/).

1.  **Create a Web Service** on Render.
    - **Environment Variable**: `PYTHON_VERSION` = `3.11.0` (Avoid alpha versions like 3.14 to prevent build errors).
    - **Build Command**: `./build.sh`
    - **Start Command**: `gunicorn ahamenes_backend.wsgi:application`
2.  **Environment Variables**:
    - `SECRET_KEY`, `cloud_name`, `api_key`, `api_secret` must be set in the Render dashboard.
    - Set `DEBUG` to `False`.
