# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Application
from .models import Document
from .models import SavedJob

# forms.py
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(choices=Application.STATUS_CHOICES, attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position_applied': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
    
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file', 'company_tag', 'job_role_tag']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'document_type': forms.Select(choices=Document.DOCUMENT_TYPES, attrs={'class': 'form-select', 'required': 'required'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'required': 'required', 'accept': '.pdf,.doc,.docx'}),
            'company_tag': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'job_role_tag': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise ValidationError("Please upload a file.")

        # ✅ File size check (5MB max)
        max_size = 5 * 1024 * 1024  # 5 MB
        if file.size > max_size:
            raise ValidationError("File size must be less than 5 MB.")

        # ✅ MIME type check
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if file.content_type not in allowed_types:
            raise ValidationError("Only PDF, DOC, or DOCX files are allowed.")

        return file

class SavedJobForm(forms.ModelForm):
    class Meta:
        model = SavedJob
        fields = ['job_title', 'company', 'job_link', 'deadline', 'notes']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
