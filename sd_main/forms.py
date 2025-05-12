from django import forms

class AgencyForm(forms.Form):
    agency_name = forms.CharField(max_length=100)

class UploadPolicyForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)
