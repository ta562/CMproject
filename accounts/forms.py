from django.contrib.auth.forms import UserCreationForm
from .models import ManagerUser

class ManagerUserCreationForm(UserCreationForm):
    class Meta:
        model = ManagerUser
        fields = ('username','email','password1','password2')


