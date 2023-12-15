# Project Setup: backend_sob3

## Step 1: Prerequisites

- Python 3.x (Install from [Python Official Website](https://www.python.org/downloads/))
- Pip (Python package manager)
- Virtualenv (optional, but recommended for managing project dependencies)

## Step 2: Create a Virtual Environment (Optional)

```bash
# Create a directory for your project
mkdir backend_sob3
cd backend_sob3

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS and Linux:
source venv/bin/activate

```
## Step 3: Install Django
# Install Django
pip install django


## Step 4: Create Django Project
# Create a new Django project
django-admin startproject backend_sob3
cd backend_sob3


## Step 5: Create a Django App
# Create a new Django app
python manage.py startapp myapp


## Step 6: Configure Project Settings
- Open backend_sob3/settings.py to configure project settings including database settings, installed apps, and other project-specific configurations.

## Step 7: Define Models
- In myapp/models.py, define your database models using Django's Object-Relational Mapping (ORM) system.

## Step 8: Create Database Tables
# Create database tables based on your models
python manage.py makemigrations
python manage.py migrate

## Step 8: Create Database Tables
# Create a superuser account to access the Django admin interface
python manage.py createsuperuser

## Step 9: Create a Superuser (Admin User)
# Create a superuser account to access the Django admin interface
python manage.py createsuperuser

## Step 10: Create Views and Templates
- Define views to handle HTTP requests and create templates for rendering HTML pages. Organize these in the myapp directory.


## Step 11: Define URLs
- Configure URL routing by defining URL patterns in myapp/urls.py. Include these patterns in backend_sob3/urls.py.

## Step 12: Run the Development Server
# Start the Django development server
python manage.py runserver

Your Django project should now be running, and you can access it in your web browser at http://localhost:8000.

## Step 13: Migrate DB
```
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head

```



## Additional Resources
- Django Documentation: Refer to the official Django documentation for more details and guidance on Django development.

