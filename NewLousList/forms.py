from django.forms import ModelForm
from django import forms
from .models import Review

class NewReview(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    grad_year = forms.IntegerField()
    major = forms.CharField(max_length=50)