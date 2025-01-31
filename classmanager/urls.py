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
    path('timetable',views.TimetableView.as_view(),name='timetable'),
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
    path('ajax_get_printclassroomlist/', views.ajax_get_printclassroomlist, name='ajax_get_printclassroomlist'),
    path('ajax/create_teacher/', views.ajax_create_teacher, name='ajax_create_teacher'),
    path('ajax_get_teacherlist/', views.ajax_get_teacherlist, name='ajax_get_teacherlist'),
    path('ajax_get_update_teacher/', views.ajax_get_update_teacher, name='ajax_get_update_teacher'),
    path('ajax_get_deleteteacherlist/', views.ajax_get_deleteteacherlist, name='ajax_get_deleteteacherlist'),
    path('update-class-schedule/', views.update_class_schedule, name='update_class_schedule'),
    path('create-class-schedule/', views.create_class_schedule, name='create_class_schedule'),
    path('get-class-schedules/', views.get_class_schedules, name='get_class_schedules'),
    path('ajax_get_printtimetableoption/', views.ajax_get_printtimetableoption, name='ajax_get_printtimetableoption'),
    path('ajax/create/period/', views.ajax_create_period, name='ajax_create_period'),
    path('ajax/get/period_list/', views.ajax_get_printperiodlist, name='ajax_get_printperiodlist'),
    path('classroom_users_endpoint/', views.classroom_users_endpoint, name='classroom_users_endpoint'),
  
]
    



