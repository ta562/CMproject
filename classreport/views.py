from django.shortcuts import render
from django.views.generic import TemplateView

class ReportCreateView(TemplateView):
    template_name='reportcreate.html'

class TeacherSelectView(TemplateView):
    template_name='teacherselect.html'