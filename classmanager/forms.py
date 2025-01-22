from django.forms import ModelForm
from .models import Student
from django import forms

class StudentForm(ModelForm):
    class Meta:
        model=Student
        fields=['name','mail','post','address','phone1','phone2']