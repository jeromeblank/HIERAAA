# my_project/urls.py (Main project folder)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from resume import views  
from resume.views import resume_builder, download_pdf

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Allauth login
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('job-search/', views.job_search, name='job_search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

