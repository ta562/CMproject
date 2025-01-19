from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Exists, OuterRef, Q

from django.contrib.auth.backends import ModelBackend
from .models import ManagerUser
# UserModel = get_user_model()
UserModel = ManagerUser


class ManagerAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(request.path+'manager')
        if request.path != '/login':
            return
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password):
                return user