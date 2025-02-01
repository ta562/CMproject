from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
app_name = 'classreport'
urlpatterns = [
    path('reportcreate',views.ReportCreateView.as_view(),name='reportcreate'),
    path('teacherselect',views.TeacherSelectView.as_view(),name='teacherselect'),
    path('check_teacher_id/', views.check_teacher_id, name='check_teacher_id'),
    path('report_create/<str:teacher_id>/', views.ReportCreateView.as_view(), name='report_create'),

]
