from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
app_name = 'accountsclassroom'
urlpatterns = [
    path('signup_classroom/',views.SignUpClassroomView.as_view(),name='signup_classroom'),
    path('signup_success_classroom/',views.SignUpSuccessClassroomView.as_view(),name='signup_success_classroom'),
    path('login_classroom',views.LoginClassroomView.as_view(),name='login_classroom'),
    path('logout_classroom/',views.LogoutClassroomView.as_view(),name='logout_classroom'),
]
