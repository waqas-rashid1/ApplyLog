# forms.py
from django import forms
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
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file', 'company_tag', 'job_role_tag']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'document_type': forms.Select(choices=Document.DOCUMENT_TYPES, attrs={'class': 'form-select', 'required': 'required'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'required': 'required'}),
            'company_tag': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'job_role_tag': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class SavedJobForm(forms.ModelForm):
    class Meta:
        model = SavedJob
        fields = ['job_title', 'company', 'job_link', 'deadline', 'notes']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
