from django.shortcuts import render
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name='index.html'
    
class LoginSelectView(TemplateView):
    template_name='loginselect.html'

class AssessmentListView(TemplateView):
    template_name='assessmentlist.html'

class StudentRegistrationView(TemplateView):
    template_name='studentregistration.html'

class StudentListView(TemplateView):
    template_name='studentlist.html' 

class TeacherRegistrationView(TemplateView):
    template_name='teacherregistration.html'

class TeacherListView(TemplateView):
    template_name='teacherlist.html' 

class ClassroomRegistrationView(TemplateView):
    template_name='classroomregistration.html'

class ClassroomListView(TemplateView):
    template_name='classroomlist.html' 

class LessonListView(TemplateView):
    template_name='lessonlist.html' 