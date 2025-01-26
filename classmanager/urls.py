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
    path('api/printstudentlist/get/', views.ajax_get_printstudentlist, name='ajax_get_printstudentlist'),
    path('api/deletestudentlist/get/', views.ajax_get_deletestudentlist, name='ajax_get_deletestudentlist'),
    path('api/createstudentlist/get/', views.ajax_get_createstudentlist, name='ajax_get_createstudentlist'),
    path('api/updatastudentlist/get/', views.ajax_get_updatastudentlist, name='ajax_get_updatastudentlist'),
    path('api/updatastudentschool/get/', views.ajax_get_updatastudentschool, name='ajax_get_updatastudentschool'),
    path('ajax/delete_student_school/', views.ajax_delete_student_school, name='ajax_delete_student_school'),
    path('ajax/create_student_school/', views.ajax_create_student_school, name='ajax_create_student_school'),
    path('create_subject/', views.ajax_create_subject, name='ajax_create_subject'),
    path('ajax_get_printsubjectlist/', views.ajax_get_printsubjectlist, name='ajax_get_printsubjectlist'),
    path('ajax/get_subjects/', views.get_subjects, name='get_subjects'),
]


