from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
app_name = 'classreport'
urlpatterns = [
    path('reportcreate',views.ReportCreateView.as_view(),name='reportcreate'),
    path('teacherselect',views.TeacherSelectView.as_view(),name='teacherselect'),
    path('check_teacher_id/', views.check_teacher_id, name='check_teacher_id'),
    path('report_create/<str:teacher_id>/<str:period_id>/', views.ReportCreateView.as_view(), name='report_create'),
    path('api/teacher-schedules/', views.get_teacher_and_schedules, name='get_teacher_and_schedules'),
    path('get_period_options/', views.get_period_options, name='get_period_options'),
    path('save_report/', views.save_report, name='save_report'),
    path('get-class-schedules-report/', views.get_class_schedules, name='get_class_schedules'),
    path('get_student_subjects/<int:student_id>/', views.get_student_subjects, name='get_student_subjects'),
    path('typingpractice',views.TypingPractceView.as_view(),name='typingpractie'),

    

]
