from django import forms
from .models import EmailTemplate

class AgencyForm(forms.Form):
    agency_name = forms.CharField(max_length=100)

class UploadPolicyForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject_line', 'body']
        widgets = {
            'name': forms.Textarea(attrs={'id': 'template_name', 'rows': 1, 'cols': 80, 'class': 'form-control', 'style': 'resize:none;'}),
            'subject_line': forms.Textarea(attrs={'id': 'template_subject_line', 'rows': 1, 'cols': 80, 'class': 'form-control', 'style': 'resize:none;'}),
            'body': forms.Textarea(attrs={'id': 'template_body', 'rows': 20, 'cols': 80, 'class': 'form-control'}),
        }
