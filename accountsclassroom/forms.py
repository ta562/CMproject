from django.contrib.auth.forms import UserCreationForm
from .models import ClassroomUser

class ClassroomUserCreationForm(UserCreationForm):
    class Meta:
        model = ClassroomUser
        fields = ('username','email','password1','password2')


