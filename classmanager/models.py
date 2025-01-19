from django.db import models
from accounts.models import ManagerUser
from accountsclassroom.models import ClassroomUser


class Student(models.Model):
    manageruser=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE,
    )
    name=models.CharField(
        verbose_name='名前',
        max_length=200,
    )
    mail=models.CharField(
        verbose_name='配信用メールアドレス',
        max_length=200,
    )
    post=models.CharField(
        verbose_name='郵便番号',
        max_length=200,blank=True,null=True
    )
    address=models.CharField(
        verbose_name='住所',
        max_length=200,blank=True,null=True
    )
    phone1=models.CharField(
        verbose_name='電話番号',
        max_length=200,blank=True,null=True
    )
    phone2=models.CharField(
        verbose_name='保護者の電話番号',
        max_length=200,blank=True,null=True
    )
    posted_at=models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True,blank=True,null=True
        )



class StudentSchool(models.Model):
    student=models.ForeignKey(
        Student,
        verbose_name='生徒',
        on_delete=models.CASCADE,
    )
    
    school=models.CharField(
        verbose_name='学校名',
        max_length=200,blank=True,null=True
    )
    stage=models.IntegerField(
        verbose_name='教育段階',
        blank=True,null=True
    )
    grade=models.IntegerField(
        verbose_name='学年',
        blank=True,null=True
    )
    schoolclass=models.CharField(
        verbose_name='組',
        max_length=200,blank=True,null=True
    )
    school=models.CharField(
        verbose_name='学校名',
        max_length=200,blank=True,null=True
    )
    posted_at=models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True,blank=True,null=True
        )

class Subject(models.Model):
    manageruser=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE, blank=True, null=True
    )
    title=models.CharField(
        verbose_name='科目名',
        max_length=200,blank=True,null=True
    )
    posted_at=models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True,blank=True,null=True
        )

class StudentSubject(models.Model):
    student=models.ForeignKey(
        Student,
        verbose_name='生徒',
        on_delete=models.CASCADE, blank=True, null=True
    )

    subject=models.ForeignKey(
        Subject,
        verbose_name='科目',
        on_delete=models.CASCADE, blank=True, null=True
    )

    posted_at=models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True,blank=True,null=True
        )

