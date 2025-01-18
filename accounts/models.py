from django.db import models
from django.contrib.auth.models import AbstractUser
from accountsclassroom.models import ClassroomUser

class ManagerUser(AbstractUser):
    post=models.CharField(max_length=200,blank=True,null=True)


# Create your models here.


class ManagerClassroom(models.Model):

    manager=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE, blank=True, null=True,
    )
    classroom=models.ForeignKey(
        ClassroomUser,
        verbose_name='教室',
        on_delete=models.CASCADE, blank=True, null=True,
    )