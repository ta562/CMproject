from django.urls import path
from .import views

app_name='classmanager'
urlpatterns = [
    path('manager',views.IndexView.as_view(),name='manager'),
    path('',views.LoginSelectView.as_view(),name='loginselect'),
    path('assessmentlist',views.AssessmentListView.as_view(),name='assessmentlist'),
    path('setting',views.SettingView.as_view(),name='setting'),
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
    path('api/get-reports/', views.get_reports, name='get_reports'),
    path('approve_report/', views.approve_report, name='approve_report'),
    path('update_class_schedule/', views.update_class_schedule, name='update_class_schedule'),
    path('delete_class_schedule/', views.delete_class_schedule, name='delete_class_schedule'),
    path('ajax/update-classroom/', views.update_classroom, name='update_classroom'),
    path('ajax/delete-classroom/', views.delete_classroom, name='delete_classroom'),
    path('ajax/ajax_update_subject/', views.ajax_update_subject, name='ajax_update_subject'),
    path('ajax/delete-subject/', views.delete_subject, name='ajax_delete_subject'),
    path('ajax/update_period/', views.update_period, name='update_period'),
    path('ajax/delete_period/', views.delete_period, name='delete_period'),
    path('get_student_subjects/<int:student_id>/', views.get_student_subjects, name='get_student_subjects'),
    path('get-report-detail/', views.get_report_detail, name='get_report_detail'),
    path('get-update_report/', views.update_report, name='update_report'),
    path('update_settings/', views.update_settings, name='update_settings'),
    path('schoollist/', views.SchoollistView.as_view(), name='schoollist'),
    path('ajax_delete_school/', views.ajax_delete_school, name='ajax_delete_school'),
    path('ajax_update_school/', views.ajax_update_school, name='ajax_update_school'),
    path('ajax_create_school/', views.ajax_create_school, name='ajax_create_school'),
    path('ajax_get_schoollist/', views.ajax_get_schoollist, name='ajax_get_schoollist'),
    path('ajax/get-schools/', views.get_schools_by_stage, name='get_schools'),
    path('delete_last_phone/', views.delete_last_phone, name='delete_last_phone'),
   

    
  
]
    



