# my_project/urls.py (Main project folder)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from resume import views  # or your corresponding app's views
from .views import resume_builder, download_pdf

urlpatterns = [
    # Your other URL patterns...
    path('', views.landing_page, name='landing_page'),  # This is for the landing page
    path('resume-builder/', views.resume_builder, name='resume_builder'),  # Your existing resume builder path
    path('download_pdf/', views.download_pdf, name='download_pdf'),  # Existing download path
    path('job-search/', views.job_search, name='job_search'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
