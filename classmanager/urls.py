from django.urls import path
from .import views

app_name='classmanager'
urlpatterns = [
    path('manager',views.IndexView.as_view(),name='manager'),
    path('',views.LoginSelectView.as_view(),name='loginselect'),
    path('assessmentlist',views.AssessmentListView.as_view(),name='assessmentlist'),
    path('studentregistration',views.StudentRegistrationView.as_view(),name='studentregistration'),
    path('studentlist',views.StudentListView.as_view(),name='studentlist'),
    path('teacherregistration',views.TeacherRegistrationView.as_view(),name='teacherregistration'),
    path('teacherlist',views.TeacherListView.as_view(),name='teacherlist'),
    path('classroomregistration',views.ClassroomRegistrationView.as_view(),name='classroomregistration'),
    path('classroomlist',views.ClassroomListView.as_view(),name='classroomlist'),
    path('lessonlist',views.LessonListView.as_view(),name='lessonlist'),
]