from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
app_name = 'classreport'
urlpatterns = [
    path('reportcreate',views.ReportCreateView.as_view(),name='reportcreate'),
    path('teacherselect',views.TeacherSelectView.as_view(),name='teacherselect'),
]
