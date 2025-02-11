from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from .models import Student
from .forms import StudentForm
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import Student, StudentSchool,Subject,SchoolSubject,Teacher,ClassSchedule,Period,Report
from accounts.models import ManagerClassroom

from accountsclassroom.models import ClassroomUser
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie


class IndexView(TemplateView):
    template_name='index.html'
    
class LoginSelectView(TemplateView):
    template_name='loginselect.html'

class AssessmentListView(TemplateView):
    template_name='assessmentlist.html'

class StudentRegistrationView(TemplateView):
    template_name='studentregistration.html'

class TimetableView(TemplateView):
    template_name = 'timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current logged-in ManagerUser
        manager_user = self.request.user

        # Find classrooms linked to this manager
        linked_classrooms = ManagerClassroom.objects.filter(manager=manager_user)

        # Get all ClassroomUsers linked through ManagerClassroom
        classroom_users = ClassroomUser.objects.filter(
            id__in=linked_classrooms.values_list('classroom_id', flat=True)
        )

        # Add classroom_users to the context
        context['classroom_users'] = classroom_users
        return context

from django.http import JsonResponse

class StudentListView(CreateView, ListView):
    def get(self, request, *args, **kwargs):
        object = Student.objects.all().order_by('-posted_at')  
        context = {'object': object}
        return render(request, 'studentlist.html', context)

    def post(self, request, *args, **kwargs):
        if 'delete_student_id' in request.POST:
            # 削除処理
            student_id = request.POST['delete_student_id']
            try:
                student = Student.objects.get(id=student_id)
                student.delete()
                return JsonResponse({'success': True, 'message': '学生が削除されました'})
            except Student.DoesNotExist:
                return JsonResponse({'success': False, 'message': '学生が存在しません'})
        else:
            # 作成処理
            obj = Student(
                manageruser_id=self.request.user.id,
                name=request.POST['form_student_name'],
                mail=request.POST['form_student_mail'],
                post=request.POST['form_student_post'],
                address=request.POST['form_student_address'],
                phone1=request.POST['form_student_tel1'],
                phone2=request.POST['form_student_tel2']
            )
            obj.save()
            return render(request, 'studentlist.html')

#生徒登録関連


def ajax_get_createstudentlist(request):
    if request.method == 'POST':
        print('test')
        body = json.loads(request.body)
        print(body)
        # Studentを作成
        new_student = Student.objects.create(
            manageruser=request.user,
            classroomuser_id=body['student_classroomuser'],
            name=body['student_name'],
            mail=body['student_mail'],
            post=body['student_post'],
            address=body['student_address'],
            phone1=body['student_tel1'],
            phone2=body['student_tel2']
        )
        
        # StudentSchoolを関連付けて作成
        new_school = StudentSchool.objects.create(
            student=new_student,
            school=body['student_school'],
            stage=body['student_stage'],
            grade=body['student_grade'],
            schoolclass=body['student_schoolclass'],
        )
        
        # 選択された科目を関連付け
        subject_ids = body['student_subjects']
        subject_objects = Subject.objects.filter(id__in=subject_ids)
        for subject in subject_objects:
            # SchoolSubjectインスタンスを作成して保存
            SchoolSubject.objects.create(
                subject=subject,
                school=new_school
            )

        return JsonResponse({'success': True, 'message': '学生と学校情報が保存されました'})
    else:
        return JsonResponse({'success': False, 'message': '無効なリクエストです'})

def ajax_get_updatastudentlist(request):
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        classroomuser_id = request.GET.get('student_classroomuser')
        
        
        try:
            student = Student.objects.get(pk=student_id)
            student.name = request.GET.get('student_name')
            student.classroomuser = ClassroomUser.objects.get(id=int(classroomuser_id))
            print(student.classroomuser)
            student.mail = request.GET.get('student_mail')
            student.post = request.GET.get('student_post')
            student.address = request.GET.get('student_address')
            student.phone1 = request.GET.get('student_tel1')
            student.phone2 = request.GET.get('student_tel2')
            student.save()
            return JsonResponse({'success': True, 'message': '学生が更新されました'})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': '学生が存在しません'})
    else:
        return JsonResponse({'success': False, 'message': '無効なリクエストです'})
def ajax_get_printstudentlist(request):
    students = Student.objects.filter(manageruser_id=request.user).order_by('-posted_at')
    schools = StudentSchool.objects.order_by('-posted_at')
    subjects = SchoolSubject.objects.select_related('subject', 'school').all()
    all_subjects = Subject.objects.all()  # すべての科目を取得

    manager_classrooms = ManagerClassroom.objects.filter(manager=request.user)
    classroom_users = ClassroomUser.objects.filter(
        id__in=manager_classrooms.values_list('classroom_id', flat=True)
    )

    studentlist = []
    for student in students:
        serialized_student = serializers.serialize('python', [student])[0]
        # classroomuserのusernameを安全に追加
        if student.classroomuser is not None:
            serialized_student['fields']['classroomusername'] = student.classroomuser.username
        else:
            serialized_student['fields']['classroomusername'] = None
        studentlist.append(serialized_student)

    schoollist = serializers.serialize('python', schools)

    subjectlist = [
        {
            'school_id': school_subject.school.id,
            'subject_title': school_subject.subject.title,
        }
        for school_subject in subjects
    ]

    all_subjectlist = [
        {'id': subject.id, 'title': subject.title}
        for subject in all_subjects
    ]

    classroom_user_list = [
        {'id': user.id, 'username': user.username} for user in classroom_users
    ]

    data = {
        'studentlist': studentlist,
        'schoollist': schoollist,
        'subjectlist': subjectlist,
        'all_subjectlist': all_subjectlist,
        'classroom_users': classroom_user_list
    }
    return JsonResponse(data)

def ajax_get_deletestudentlist(request):
    student_id = request.GET.get('student_id')
    try:
        deletestudent = Student.objects.get(id=student_id)
        deletestudent.delete()
        return JsonResponse({'success': True})
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': '学生が見つかりませんでした。'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': '削除中にエラーが発生しました。'})
    


def ajax_get_updatastudentschool(request):
    if request.method == 'GET':
        school_id = request.GET.get('school_id')
        stage = request.GET.get('student_stage')
        grade = request.GET.get('student_grade')
        schoolclass = request.GET.get('student_schoolclass')
        school = request.GET.get('student_school')
        subject_ids_json = request.GET.get('subjects', '[]')
        subject_ids = json.loads(subject_ids_json)

        try:
            school_instance = StudentSchool.objects.get(pk=school_id)
            school_instance.stage = stage
            school_instance.grade = grade
            school_instance.schoolclass = schoolclass
            school_instance.school = school
            school_instance.save()

            # 既存の科目をクリア
            SchoolSubject.objects.filter(school=school_instance).delete()

            # 新しい科目を追加
            for subject_id in subject_ids:
                subject_instance = Subject.objects.get(pk=subject_id)
                SchoolSubject.objects.create(school=school_instance, subject=subject_instance)

            return JsonResponse({'success': True})
        except StudentSchool.DoesNotExist:
            return JsonResponse({'success': False, 'error': '指定された学校が見つかりません'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '無効なリクエストメソッドです。'})

@require_GET
def ajax_delete_student_school(request):
    school_id = request.GET.get('school_id')
    
    try:
        # 該当する学校データを取得して削除
        school = StudentSchool.objects.get(pk=school_id)
        school.delete()
        return JsonResponse({'success': True})
    except StudentSchool.DoesNotExist:
        return JsonResponse({'success': False, 'error': '学校データが見つかりません。'})
    
def ajax_create_student_school(request):
    if request.method == 'GET':
        try:
            student_id = request.GET.get('student_id')
            stage = request.GET.get('student_stage')
            grade = request.GET.get('student_grade')
            schoolclass = request.GET.get('student_schoolclass')
            school = request.GET.get('student_school')
            subjects_data = request.GET.get('subjects', '[]')
            subjects_ids = json.loads(subjects_data)

            student = Student.objects.get(pk=student_id)

            # 新しいStudentSchoolインスタンスを作成
            student_school = StudentSchool.objects.create(
                student=student,
                stage=stage,
                grade=grade,
                schoolclass=schoolclass,
                school=school
            )

            # SchoolSubjectレコードを作成
            for subject_id in subjects_ids:
                subject = Subject.objects.get(pk=subject_id)
                SchoolSubject.objects.create(
                    subject=subject,
                    school=student_school
                )

            return JsonResponse({'success': True})

        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'})
        except Subject.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Subject not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



class TeacherRegistrationView(TemplateView):
    template_name='teacherregistration.html'

class TeacherListView(TemplateView):
    template_name='teacherlist.html' 

class ClassroomRegistrationView(TemplateView):
    template_name='classroomregistration.html'

class ClassroomListView(TemplateView):
    template_name='classroomlist.html' 

class LessonListView(TemplateView):
    template_name='lessonlist.html'


def ajax_create_subject(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        title = request.POST.get('subject_title')

        if title:
            Subject.objects.create(
                manageruser=request.user,
                title=title
            )
            return JsonResponse({'success': True, 'message': '科目が保存されました'})
        else:
            return JsonResponse({'success': False, 'message': '無効なデータです'})
    
    return JsonResponse({'success': False, 'message': '無効なリクエストです'})

def ajax_get_printsubjectlist(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # all subjects related to the logged-in user
        subjects = Subject.objects.filter(manageruser=request.user)
        subject_list = serializers.serialize('python', subjects)
        return JsonResponse({'subjectlist': subject_list}, safe=False)

    return JsonResponse({'success': False, 'message': '無効なリクエストです'})

def get_subjects(request):
    subjects = Subject.objects.all()  # 科目の全リストを取得
    subject_list = [{'id': subject.id, 'title': subject.title} for subject in subjects]
    return JsonResponse({'subjects': subject_list})

def classroom_users_endpoint(request):
    # Assuming `request.user` is the logged-in ManagerUser
    manager_user = request.user

    # Get classrooms linked to the ManagerUser
    manager_classrooms = ManagerClassroom.objects.filter(manager=manager_user)

    # Get ClassroomUser IDs from these manager classrooms
    classroom_users = ClassroomUser.objects.filter(
        id__in=manager_classrooms.values_list('classroom_id', flat=True)
    )  # .select_related('user') は削除

    # Prepare data for JSON response
    data = {
        'classroom_users': [
            {'id': user.id, 'username': user.username} for user in classroom_users
        ]
    }

    return JsonResponse(data)

@ensure_csrf_cookie
def ajax_create_period(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        title = request.POST.get('title')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if title and start_time and end_time:
            Period.objects.create(
                manageruser=request.user,  # 正しくリンクされていることを確認
                title=title,
                start_time=start_time,
                end_time=end_time
            )
            return JsonResponse({'success': True, 'message': '時限が保存されました'})
        else:
            return JsonResponse({'success': False, 'message': '無効なデータです'})

    return JsonResponse({'success': False, 'message': '無効なリクエストです'})

def ajax_get_printperiodlist(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # ログインしているユーザーに関連するすべての時限
        periods = Period.objects.filter(manageruser=request.user)
        period_list = serializers.serialize('python', periods)
        return JsonResponse({'periodlist': period_list})

    return JsonResponse({'success': False, 'message': '無効なリクエストです'})


def ajax_get_printclassroomlist(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 現在ログインしているManagerUserに紐づくClassroomUserを取得
        classrooms = ManagerClassroom.objects.filter(manager=request.user)
        classroom_list = [{
            'username': classroom.classroom.username,
            'email': classroom.classroom.email
        } for classroom in classrooms]
        
        return JsonResponse({'classroomlist': classroom_list}, safe=False)

    return JsonResponse({'success': False, 'message': '無効なリクエストです'})



def ajax_create_teacher(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        teacher_id = body.get('teacher_id')
        
        # teacher_idが重複していないか確認
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            return JsonResponse({'success': False, 'message': 'このIDは既に存在します'})

        # Teacherオブジェクトの作成
        new_teacher = Teacher.objects.create(
            manageruser=request.user,
            teacher_id=teacher_id,
            classroomuser_id=body.get('classroomuser'),
            name=body.get('name'),
            mail=body.get('mail'),
            post=body.get('post'),
            address=body.get('address'),
            phone1=body.get('phone1'),
            note=body.get('note')
        )
        return JsonResponse({'success': True, 'message': '教師情報が保存されました'})
    else:
        return JsonResponse({'success': False, 'message': '無効なリクエストです'})
    
def ajax_get_teacherlist(request):
    teachers = Teacher.objects.filter(manageruser_id=request.user).order_by('-posted_at')
    manager_classrooms = ManagerClassroom.objects.filter(manager=request.user)

    classroom_users = ClassroomUser.objects.filter(
        id__in=manager_classrooms.values_list('classroom_id', flat=True)
    )
    classroom_user_list = [
        {'id': user.id, 'username': user.username} for user in classroom_users
    ]
    teacherlist = []
    for teacher in teachers:
        serialized_teacher = serializers.serialize('python', [teacher])[0]
        # classroomuserのusernameを安全に追加
        if teacher.classroomuser is not None:
            serialized_teacher['fields']['classroomusername'] = teacher.classroomuser.username
        else:
            serialized_teacher['fields']['classroomusername'] = None
        teacherlist.append(serialized_teacher)
    

    
   
    data = {
        'teacherlist': teacherlist,
        'classroom_users': classroom_user_list
    }
    return JsonResponse(data)

@csrf_exempt  # ここではcsrf_exemptを使用するが、通常は推奨されない。適切にCSRFトークンを扱う必要がある。
def ajax_get_update_teacher(request):
    if request.method == 'POST':
        classroomuser_id = request.POST.get('teacher_classroomuser')
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher.classroomuser = ClassroomUser.objects.get(id=int(classroomuser_id))
            
            teacher.teacher_id=request.POST.get('teacher_teacher_id')
            teacher.name = request.POST.get('teacher_name')
            teacher.mail = request.POST.get('teacher_mail')
            teacher.post = request.POST.get('teacher_post')
            teacher.address = request.POST.get('teacher_address')
            teacher.phone1 = request.POST.get('teacher_phone')
            teacher.note = request.POST.get('teacher_note')
            teacher.save()
            return JsonResponse({'success': True})
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'error': '教師が見つかりませんでした。'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': '無効なリクエストです。'})
    
@csrf_exempt  # こちらも同様にCSRFを適切に扱うべき
def ajax_get_deleteteacherlist(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher.delete()
            return JsonResponse({'success': True})
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'error': '教師が見つかりませんでした。'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': '無効なリクエストです。'})
    
@csrf_exempt
def update_class_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            location = data.get('location')
            notes = data.get('notes')

            # `ClassSchedule`モデルのインスタンスを取得
            schedule = ClassSchedule.objects.get(id=schedule_id)
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.location = location
            schedule.notes = notes
            schedule.save()

            return JsonResponse({'success': True, 'message': 'スケジュールが更新されました。'})
        except ClassSchedule.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'スケジュールが見つかりません。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})


@csrf_exempt
def create_class_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
          
            teacher_id = data.get('teacher_id')
            classroomuser_id = data.get('classroomuser_id')
            period_id = data.get('period_id')
            date = data.get('date')  # 提出されたデータから日付を取得
           

            # ClassScheduleオブジェクトを新規作成
            schedule = ClassSchedule.objects.create(
                student=Student.objects.get(id=student_id),
                teacher=Teacher.objects.get(id=teacher_id),
                classroomuser=ClassroomUser.objects.get(id=classroomuser_id),
                period=Period.objects.get(id=period_id),
                date=date,  # 日付を保存
             
            )

            return JsonResponse({'success': True, 'message': '新しいスケジュールが作成されました。'})
        except (Student.DoesNotExist, Teacher.DoesNotExist, ClassroomUser.DoesNotExist, Period.DoesNotExist):
            return JsonResponse({'success': False, 'message': '関連するデータが見つかりません。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

def get_class_schedules(request):
    try:
        classroomuser_id = request.GET.get('classroomuser_id')
        date = request.GET.get('date')
        student_id = request.GET.get('student_id')
        teacher_id = request.GET.get('teacher_id')
        period_id = request.GET.get('period_id')

        # 指定された条件に従ってスケジュールをフィルタリング
        filters = {}
        if classroomuser_id:
            filters['classroomuser_id'] = classroomuser_id
        if date:
            filters['date'] = date
        if student_id:
            filters['student_id'] = student_id
        if teacher_id:
            filters['teacher_id'] = teacher_id
        if period_id:
            filters['period_id'] = period_id

        schedules = ClassSchedule.objects.filter(**filters)

        data = [{
            'id': schedule.id,
            'student_name': schedule.student.name,
            'teacher_name': schedule.teacher.name,
            'classroom_name': schedule.classroomuser.username if schedule.classroomuser else '',
            'period_title': schedule.period.title if schedule.period else '',
            'start_time': schedule.period.start_time.strftime('%H:%M') if schedule.period.start_time else '',
            'end_time': schedule.period.end_time.strftime('%H:%M') if schedule.period.end_time else '',
            'date': schedule.date.strftime('%Y-%m-%d') if schedule.date else '',
            'flag': schedule.flag ,
        } for schedule in schedules]

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def ajax_get_printtimetableoption(request):
    # classroomuser_idをリクエストから取得
    classroomuser_id = request.GET.get('classroomuser_id')
    
    # classroomuser_idが提供されていれば、それに基づいて生徒と教師をフィルタリング
    if classroomuser_id:
        student_list = Student.objects.filter(classroomuser_id=classroomuser_id)
        teacher_list = Teacher.objects.filter(classroomuser_id=classroomuser_id)
    else:
        student_list = Student.objects.none()
        teacher_list = Teacher.objects.none()

    # 既存のデータ取得コード
    manager_id = request.user.id
    classrooms = ManagerClassroom.objects.filter(manager_id=manager_id).select_related('classroom')
    periods = Period.objects.filter(manageruser_id=manager_id)

    data = {
        'classroom_list': [{'id': classroom.classroom.id, 'username': classroom.classroom.username} for classroom in classrooms],
        'period_list': [{'id': period.id, 'title': period.title} for period in periods],
        'student_list': [{'id': student.id, 'name': student.name} for student in student_list],
        'teacher_list': [{'id': teacher.id, 'name': teacher.name} for teacher in teacher_list],
    }

    return JsonResponse(data)

def get_reports(request):
    user = request.user
    manager_classrooms = user.managerclassroom_set.all()
    classroom_users = [mc.classroom for mc in manager_classrooms]

    reports = Report.objects.filter(classroomuser__in=classroom_users, student__manageruser=user).order_by('-posted_at')

    report_data = []
    for report in reports:
        report_data.append({
            'flag': '未処理' if report.flag else '処理済み',
            'date': report.date,
            'time': report.period.title,
            'classroom': f"{report.classroomuser.username}, {report.teacher.name}",
            'attendance': report.attendance,
            'behindtime': report.behindtime,
            'earlytime': report.earlytime,
            'poster': report.poster,
            'understand': report.understand,
            'achievement': report.achievement,
            'parentsmessage': report.parentsmessage,
            'teachermessage': report.teachermessage,
            'managermessage': report.managermessage,
            'id':report.id,
        })

    return JsonResponse({'reports': report_data})

def approve_report(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        managermessage = request.POST.get('manager_message')
        teachermessage = request.POST.get('teacher_message')

        try:
            report = Report.objects.get(id=report_id)
            if report.flag:
                report.managermessage = managermessage
                report.teachermessage = teachermessage
                report.flag = False
                report.save()
                return JsonResponse({'success': True})
        except Report.DoesNotExist:
            return JsonResponse({'success': False})

    return JsonResponse({'success': False})
