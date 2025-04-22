# forms.py
from django import forms
from .models import Application

# forms.py
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position_applied': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
