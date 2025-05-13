import os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ResumeForm
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from django.contrib.auth.decorators import login_required
import uuid
import re
import requests
import google.generativeai as genai
from django.core.files.base import ContentFile
from .models import Resume
from django.utils import timezone
import html
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import escape
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Configure Gemini API using the API key from the environment
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
JSEARCH_API_KEY = settings.JSEARCH_API_KEY

def sanitize_input(input_string):
    # Escape special characters in HTML
    sanitized = escape(input_string)
    # Further sanitization to remove potentially harmful characters
    sanitized = re.sub(r'[^\w\s,.-]', '', sanitized)
    return sanitized

def validate_image(image):
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if image.content_type not in allowed_types:
        raise ValidationError("Invalid image format")
    file_size = image.file.size
    if file_size > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("File size too large")
    return image

class Profile(models.Model):
    image = models.ImageField(upload_to='profile_pics/', validators=[validate_image])

def generate_resume_content(form_data):
    def safe_get(field, default="N/A"):
        return form_data.get(field) or default

    prompt = f"""
    Generate a professional resume using clear headings and bullet points.

    Full Name: {safe_get('name')}
    Contact Information:
    - Address: {safe_get('contact_info')}
    - Email: {safe_get('email')}
    - Phone: {safe_get('phone')}

    Professional Summary:
    - Write a 5 sentence summary showcasing the candidate’s strengths.

    Skills:
    - Highlight 5 relevant skills (technical and soft).

    Education:
    - Degree: {safe_get('degree')}
    - University: {safe_get('university')}
    - Dates of Attendance: {safe_get('education_dates')}
    - GPA: {safe_get('gpa', 'Not specified')}
    - Relevant Coursework: {safe_get('relevant_coursework', 'Not provided')}

    Experience:
    - Job Title: {safe_get('job_title')}
    - Company: {safe_get('company_name')}
    - Location: {safe_get('job_location')}
    - Dates: {safe_get('job_dates')}
    - Responsibilities:
    - {safe_get('responsibility_1', 'N/A')}
    - {safe_get('responsibility_2', '')}
    - {safe_get('responsibility_3', '')}

    Projects:
    - Title: {safe_get('project_title')}
    - Description: {safe_get('project_description')}
    - Technologies: {safe_get('project_tech')}

    Certifications & Awards:
    - Certification: {safe_get('certification_name')}
    - Organization: {safe_get('certification_org')}
    - Date: {safe_get('certification_date')}
    - Award: {safe_get('award_name')}

    Extracurricular:
    - Activity: {safe_get('extracurricular')}
    - Description: {safe_get('extracurricular_description')}
    """

    model = genai.GenerativeModel('models/gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def resume_builder(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            resume_text = generate_resume_content(form_data)
            request.session['resume_text'] = resume_text
            request.session['name'] = form_data.get('name', 'resume')

            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                request.session['profile_picture_path'] = save_temp_image(profile_picture)
            else:
                request.session['profile_picture_path'] = None

            return render(request, 'resume/result.html', {
                'resume_text': resume_text,
                'form_data': form_data
            })
    else:
        form = ResumeForm()
    return render(request, 'resume/form.html', {'form': form})

def save_temp_image(file):
    import uuid
    ext = os.path.splitext(file.name)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    path = os.path.join("/tmp", unique_name)
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path

def download_pdf(request):
    email = request.session.get('email') or request.user.email
    name = request.session.get('name', 'resume')
    resume_text = request.session.get('resume_text', '')
    profile_picture_path = request.session.get('profile_picture_path')

    # Remove unwanted introductory and important considerations text
    intro_text = """Okay, here's a professional resume based on the information you provided..."""
    considerations_text = """Important Considerations for a *Real* Resume: ..."""
    
    # Remove the introductory text and considerations
    resume_text = resume_text.replace(intro_text, "").replace(considerations_text, "")
    resume_text = re.split(r"(?i)key improvements and considerations", resume_text)[0].strip()
    match = re.search(r'(.*?Extracurricular Activities.*?)($|\n[A-Z].*)', resume_text, re.DOTALL)
    if match:
        resume_text = match.group(1).strip()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(595.27, 841.89), rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, leading=16, spaceAfter=10, spaceBefore=12, textColor=colors.darkblue, alignment=TA_LEFT, fontName="Helvetica-Bold"))

    elements = []

    # Add profile picture if exists and is valid
    if profile_picture_path and os.path.exists(profile_picture_path):
        try:
            img = Image(profile_picture_path, width=80, height=80)
            img.hAlign = 'RIGHT'
            elements.insert(0, img)  # Insert at the top
            elements.insert(1, Spacer(1, 12))
        except Exception as e:
            print("Image load error:", e)

    elements.append(Paragraph(f"{name}'s Resume", styles['Title']))
    elements.append(Spacer(1, 12))

    lines = resume_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif re.match(r"\*\*.+\*\*", line):
            section_title = line.replace("**", "")
            elements.append(Paragraph(section_title, styles['SectionHeader']))
        elif re.match(r"\* ", line) or line.startswith("*"):
            bullet = u"\u2022 " + line.replace("*", "").strip()
            elements.append(Paragraph(bullet, styles['BodyText']))
        else:
            elements.append(Paragraph(line, styles['BodyText']))

    doc.build(elements)
    buffer.seek(0)

    # Clean up temp file
    if profile_picture_path and os.path.exists(profile_picture_path):
        os.remove(profile_picture_path)

    # Save PDF to database
    pdf_file = ContentFile(buffer.read())
    pdf_file.name = f"{name}_resume.pdf"

    # Save to Resume model
    Resume.objects.create(
        user=request.user,
        name=name,
        email=email,
        created_at=timezone.now(),
        resume_pdf=pdf_file
    )

    # Clean up temp file
    if profile_picture_path and os.path.exists(profile_picture_path):
        os.remove(profile_picture_path)

    # Return the file as a downloadable response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_file.name}"'
    return response


def landing_page(request):
    return render(request, 'landing_page.html')


@login_required
def job_search(request):
    query = request.GET.get('query')
    location = request.GET.get('location', '')

    url = "https://jsearch.p.rapidapi.com/search"

    params = {
        "query": f"{query} {location}",
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": "8d3d20b8d2msh948c786dceb6e64p1bfe2ajsn9a656d9483a9",  # replace with your actual key
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    jobs = response.json().get("data", []) if response.status_code == 200 else []

    return render(request, 'job_results.html', {"jobs": jobs, "query": query})


