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
    path('typingpractice',views.TypingPracticeView.as_view(),name='typingpractice'),
    path('transpractice',views.TransPracticeView.as_view(),name='transpractice'),
    path('gameselect',views.GameSelectView.as_view(),name='gameselect'),
    path('api/printlist/get/', views.ajax_get_printlist, name='ajax_get_printlist'),
    path('typing/<str:pk>',views.TypingView.as_view(), name='typing'),
    path('check_student/', views.check_student_exists, name='check_student_exists'),
    path('game_clear/', views.game_clear, name='game_clear'),
    path("get_parent_categories_game/", views.get_parent_categories_game, name="get_parent_categories_game"),
    path("get_categories_game/", views.get_categories_game, name="get_categories_game"),
    path("get_english_words_game/", views.get_english_words_game, name="get_english_words_game"),
    path("get_random_wrong_trans/", views.get_random_wrong_trans, name="get_random_wrong_trans"),
    path('transquiz/<str:pk>',views.TransquizView.as_view(), name='transquiz'),
    path('trans_game_clear/', views.trans_game_clear, name='trans_game_clear'),
    path('mypagetyping/<str:pk>',views.MypageTypingView.as_view(), name='mypagetyping'),
    path('mypagetrans/<str:pk>',views.MypageTransView.as_view(), name='mypagetrans'),
    path('student_scores_view/<str:student_id>/', views.student_scores_view, name='student_scores_view'),
    path('student_scores_trans_view/<str:student_id>/', views.student_scores_trans_view, name='student_scores_trans_viewview'),

    


    

]
