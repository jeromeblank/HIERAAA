# Resume Builder with Job Search and GitHub Login

## Overview

This is a Django-based web application that allows users to:

- Create a professional resume using a built-in resume builder.
- Search for jobs using the JSearch API.
- View detailed job information.
- Register and log in using their GitHub account with Django Allauth.

## Features

- Resume builder with clean UI
- Real-time job search by title, location, company, or keyword
- View detailed job descriptions and application links
- GitHub OAuth login using Django Allauth
- Session-based authentication and logout
- Only authenticated users can access job search functionality

## Setup Instructions

### Prerequisites

- Python 3.10+
- Django 5.2+
- Virtual environment (recommended)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/resume-jobsearch-app.git
    cd resume-jobsearch-app
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file and add your keys:

    ```ini
    JSEARCH_API_KEY=your_jsearch_api_key
    GITHUB_CLIENT_ID=your_github_client_id
    GITHUB_SECRET=your_github_client_secret
    ```

5. Apply migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Project Structure
```
resumebuilder/
├── templates/
│ ├── base.html
│ ├── landing_page.html
│ ├── job_search_results.html
│ └── job_detail.html
├── resume/
│ ├── views.py
│ ├── urls.py
│ └── forms.py
├── static/
│ └── css/
│ └── styles.css
├── .env
├── manage.py
└── README.md
```

## Authentication (Django Allauth)

- GitHub social login integrated via Allauth.
- Add your GitHub OAuth credentials in Django admin under Social Applications.
- Middleware and URL configurations are set in `settings.py`.

## Notes

- Users must be logged in to search or view jobs.
- Templates use `{% extends "base.html" %}` and require `base.html` in the `templates/` directory.

## Deployment

To deploy the application:

1. Set `DEBUG = False` in `settings.py`.
2. Use a production server like Gunicorn and reverse proxy with Nginx.
3. Set allowed hosts:

    ```python
    ALLOWED_HOSTS = ['yourdomain.com']
    ```

4. Set environment variables in production.
5. Configure static files with `collectstatic`.

## requirements.txt

Below are some commonly used dependencies. Your actual `requirements.txt` should be generated using:

```bash
pip freeze > requirements.txt
Django==5.2
python-decouple
django-allauth
requests
```
License
MIT License

Credits
Built using Django, Django Allauth, and the JSearch API.
