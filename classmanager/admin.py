from django.contrib import admin
from .models import Student, StudentSchool,Subject,SchoolSubject,Teacher,ClassSchedule,Period,Report

# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail', 'posted_at')  # 管理画面で表示するフィールド
    search_fields = ('name', 'mail')  # 検索バーで使用するフィールド

@admin.register(StudentSchool)
class StudentSchoolAdmin(admin.ModelAdmin):
    list_display = ('student', 'stage', 'grade', 'schoolclass', 'posted_at')
    search_fields = ('student__name', 'school')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_at')
    search_fields = ('title',)

@admin.register(SchoolSubject)
class SchoolSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'school')
    search_fields = ('subject__title', 'school__school')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail', 'phone1', 'posted_at')
    search_fields = ('name', 'mail')

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')
    search_fields = ('title',)

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'period', 'flag')
    search_fields = ('student__name', 'teacher__name')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'attendance', 'posted_at')
    search_fields = ('student__name', 'teacher__name')
