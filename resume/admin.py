from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    # Update list_display to include fields that exist in the Resume model
    list_display = ('name', 'email', 'created_at', 'resume_pdf')  # Removed 'phone', 'degree', and 'university'
    
    # Update list_filter to use fields that exist in the Resume model
    list_filter = ('created_at',)
    
    # You can add search_fields if needed
    search_fields = ('name', 'email')
