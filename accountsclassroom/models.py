from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission

class ClassroomUser(AbstractUser):
    post=models.CharField(max_length=200,blank=True,null=True)
    groups = models.ManyToManyField(
        Group,  # Groupモデルを指定
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="classroom_users",
        related_query_name="user"
        
    )
    user_permissions = models.ManyToManyField(
        Permission,  # Permissionモデルを指定
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="classroom_users",
        related_query_name="user"
        
    )
# Create your models here.


