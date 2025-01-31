from django.db import models
from accounts.models import ManagerUser
from accountsclassroom.models import ClassroomUser
from datetime import datetime



class Student(models.Model):
    manageruser=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE,blank=True,null=True
    )
    classroomuser=models.ForeignKey(
        ClassroomUser,
        verbose_name='教室',
        on_delete=models.CASCADE,blank=True,null=True
    )
    name=models.CharField(
        verbose_name='名前',
        max_length=200,blank=True,null=True
    )
    mail=models.CharField(
        verbose_name='配信用メールアドレス',
        max_length=200,blank=True,null=True
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
        on_delete=models.CASCADE,blank=True,null=True
    )
    
    school=models.CharField(
        verbose_name='学校名',
        max_length=200,blank=True,null=True
    )
    stage=models.CharField(
        verbose_name='教育段階',
        max_length=200,blank=True,null=True
    )
    grade=models.CharField(
        verbose_name='学年',
        max_length=200,blank=True,null=True
    )
    schoolclass=models.CharField(
        verbose_name='組',
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

class SchoolSubject(models.Model):
    subject=models.ForeignKey(
        Subject,
        verbose_name='科目',
        on_delete=models.CASCADE, blank=True, null=True
    )
    school=models.ForeignKey(
        StudentSchool,
        verbose_name='科目',
        on_delete=models.CASCADE, blank=True, null=True
    )


class Teacher(models.Model):
    manageruser=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE,blank=True,null=True
    )
    classroomuser=models.ForeignKey(
        ClassroomUser,
        verbose_name='教室',
        on_delete=models.CASCADE,blank=True,null=True
    )
    teacher_id=models.CharField(
        verbose_name='ID',
        max_length=200,blank=True,null=True
    )
    name=models.CharField(
        verbose_name='名前',
        max_length=200,blank=True,null=True
    )
    mail=models.CharField(
        verbose_name='メールアドレス',
        max_length=200,blank=True,null=True
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
    note=models.CharField(
        verbose_name='メモ',
        max_length=200,blank=True,null=True
    )
    posted_at=models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True,blank=True,null=True
        )

class Period(models.Model):
    manageruser=models.ForeignKey(
        ManagerUser,
        verbose_name='マネージャー',
        on_delete=models.CASCADE,blank=True,null=True
    )
    title=models.CharField(
        verbose_name='タイトル',
        max_length=200,blank=True,null=True
    )
    start_time = models.TimeField(
        verbose_name='開始時間',blank=True,null=True
    )
    end_time = models.TimeField(
        verbose_name='終了時間',blank=True,null=True
    )

class ClassSchedule(models.Model):
    student = models.ForeignKey(
        Student,
        verbose_name='生徒',
        on_delete=models.CASCADE
    )
  
    teacher = models.ForeignKey(
        Teacher,
        verbose_name='教師',
        on_delete=models.CASCADE
    )
  
    classroomuser=models.ForeignKey(
        ClassroomUser,
        verbose_name='教室',
        on_delete=models.CASCADE,blank=True,null=True
    )
    period=models.ForeignKey(
        Period,
        verbose_name='時限',
        on_delete=models.CASCADE,blank=True,null=True
    )
    date = models.DateField(
        verbose_name='日付',blank=True,null=True
    )
    
   