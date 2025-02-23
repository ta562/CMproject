from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from .models import Student
from .forms import StudentForm
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import StudentPhone,School,Student, StudentSchool,Subject,SchoolSubject,Teacher,ClassSchedule,Period,Report
from accounts.models import ManagerClassroom

from accountsclassroom.models import ClassroomUser
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

class IndexView(LoginRequiredMixin,TemplateView):
    template_name='index.html'
    login_url=reverse_lazy("accounts:login")
    
class LoginSelectView(TemplateView):
    template_name='loginselect.html'

class AssessmentListView(LoginRequiredMixin,TemplateView):
    template_name='assessmentlist.html'
    login_url=reverse_lazy("accounts:login")

class StudentRegistrationView(LoginRequiredMixin,TemplateView):
    template_name='studentregistration.html'
    login_url=reverse_lazy("accounts:login")

class SettingView(LoginRequiredMixin,TemplateView):
    template_name='setting.html'
    login_url=reverse_lazy("accounts:login")


class SchoollistView(LoginRequiredMixin,TemplateView):
    template_name='schoollist.html'
    login_url=reverse_lazy("accounts:login")

class SuperEnglishlistView(LoginRequiredMixin,TemplateView):
    template_name='superenglishlist.html'
    login_url=reverse_lazy("accounts:login")

class TimetableView(LoginRequiredMixin,TemplateView):
    template_name = 'timetable.html'
    login_url=reverse_lazy("accounts:login")
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

class StudentListView(LoginRequiredMixin,CreateView, ListView):
    login_url=reverse_lazy("accounts:login")
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
        school_id = School.objects.get(name=body['student_school'])

        # Studentを作成
        new_student = Student.objects.create(
            manageruser=request.user,
            classroomuser_id=body['student_classroomuser'],
            name=body['student_name'],
            mail=body['student_mail'],
            post=body['student_post'],
            address=body['student_address'],
        )

        # StudentSchoolを関連付けて作成
        new_school = StudentSchool.objects.create(
            student=new_student,
            school=school_id,
            stage=body['student_stage'],
            grade=body['student_grade'],
            schoolclass=body['student_schoolclass'],
        )
        
        # 選択された科目を関連付け
        subject_ids = body['student_subjects']
        subject_objects = Subject.objects.filter(id__in=subject_ids)
        for subject in subject_objects:
            SchoolSubject.objects.create(
                subject=subject,
                school=new_school
            )

        # StudentPhoneを関連付け
        student_phones = body['student_phones']
        for phone in student_phones:
            StudentPhone.objects.create(
                phone=phone['number'],
                text=phone['name'],
                manageruser=request.user,
                student=new_student
            )

        return JsonResponse({'success': True, 'message': '学生と学校情報が保存されました'})
    else:
        return JsonResponse({'success': False, 'message': '無効なリクエストです'})
    
@csrf_exempt  # Only for testing purposes in development. Use CSRF protection properly in production.
def delete_last_phone(request):
    if request.method == "POST":
        student_pk = request.POST.get('studentPk')
        
        # Retrieve the last phone entry for the student
        last_phone_entry = StudentPhone.objects.filter(student__pk=student_pk).last()
        
        if last_phone_entry:
            last_phone_entry.delete()
            return JsonResponse({'status': 'success'}, status=200)
        
        return JsonResponse({'error': 'No phone found for the student'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def ajax_get_updatastudentlist(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        phone_data_json = request.POST.get('phone_data', '[]')
        phone_data = json.loads(phone_data_json)
        
        try:
            student = Student.objects.get(pk=student_id)
            
            student.name = request.POST.get('student_name')
            student.classroomuser = ClassroomUser.objects.get(id=int(request.POST.get('student_classroomuser')))
            student.mail = request.POST.get('student_mail')
            student.post = request.POST.get('student_post')
            student.address = request.POST.get('student_address')
            student.save()
            
            # 以前の電話情報を削除
            StudentPhone.objects.filter(student=student).delete()

            # 新しい電話情報を保存
            for phone in phone_data:
                StudentPhone.objects.create(
                    student=student,
                    phone=phone['phoneNumber'],
                    text=phone['phoneName'],
                    manageruser=student.manageruser
                )

            return JsonResponse({'success': True, 'message': '学生が更新されました'})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': '学生が存在しません'})
    else:
        return JsonResponse({'success': False, 'message': '無効なリクエストです'})

def ajax_get_printstudentlist(request):
    students = Student.objects.filter(manageruser_id=request.user).order_by('-posted_at')
    schools = StudentSchool.objects.order_by('-posted_at')
    subjects = SchoolSubject.objects.select_related('subject', 'school').all()
    all_subjects = Subject.objects.all().filter(manageruser=request.user)  # すべての科目を取得

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
    school_map = {school.id: school.name for school in School.objects.all()}
    for school_data in schoollist:
        school_id = school_data['fields']['school']
        school_name = school_map.get(school_id, None)
        if school_name:
            school_data['fields']['school'] = school_name


    filtered_schools = School.objects.filter(manageruser=request.user)
    student_phone_list = StudentPhone.objects.filter(student__in=students, manageruser=request.user)
    student_phone_data = {}
    for phone in student_phone_list:
        if phone.student.id not in student_phone_data:
            student_phone_data[phone.student.id] = []
        student_phone_data[phone.student.id].append({
            'id': phone.id,
            'phone': phone.phone,
            'text': phone.text
        })
    # Serialize the schools with stage filtering
    school_options = serializers.serialize('python', filtered_schools)

    filtered_school_map = {}
    for school in filtered_schools:
        if school.stage not in filtered_school_map:
            filtered_school_map[school.stage] = []
        filtered_school_map[school.stage].append({'id': school.id, 'name': school.name})


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
        'classroom_users': classroom_user_list,
        'filtered_schools': filtered_school_map,
        'student_phone_data': student_phone_data,
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
    print('testhhhhhhhhhhhhhhhhh')
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
            school_instance.school = School.objects.get(pk=school)
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
    subjects = Subject.objects.all().filter(manageruser=request.user) # 科目の全リストを取得
    subject_list = [{'id': subject.id, 'title': subject.title} for subject in subjects]
    return JsonResponse({'subjects': subject_list})


@csrf_exempt
def ajax_update_subject(request):
    if request.method == 'POST':
        try:
            subject_id = request.POST.get('subject_id')
            subject_title = request.POST.get('subject_title')

            subject = Subject.objects.get(id=subject_id)
            subject.title = subject_title
            subject.save()
            return JsonResponse({'success': True})
        except Subject.DoesNotExist:
            return JsonResponse({'success': False, 'error': '科目が見つかりませんでした。'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': '無効なリクエストです。'})



@csrf_exempt
def update_period(request):
    if request.method == 'POST':
        try:
            period_id = request.POST.get('period_id')
            period_title = request.POST.get('period_title')
            start_time = request.POST.get('period_start_time')
            end_time = request.POST.get('period_end_time')

            period = Period.objects.get(id=period_id)
            period.title = period_title
            period.start_time = start_time
            period.end_time = end_time
            period.save()

            return JsonResponse({'success': True})
        except Period.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Period not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def delete_period(request):
    if request.method == 'POST':
        try:
            period_id = request.POST.get('period_id')
            period = Period.objects.get(pk=period_id)
            period.delete()
            return JsonResponse({'success': True})
        except Period.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Period not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@csrf_exempt
def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        try:
            subject = Subject.objects.get(pk=subject_id)
            subject.delete()
            return JsonResponse({'success': True})
        except Subject.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Subject not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

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
            'email': classroom.classroom.email,
            'id': classroom.classroom.id,
        } for classroom in classrooms]
        
        return JsonResponse({'classroomlist': classroom_list}, safe=False)

    return JsonResponse({'success': False, 'message': '無効なリクエストです'})

@csrf_exempt
def update_classroom(request):
    if request.method == 'POST':
        classroom_id= request.POST.get('classroom_id')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        print(classroom_id)
        print(new_username)
        print(new_email)
        try:
            classroom_user = ClassroomUser.objects.get(id=classroom_id)
            classroom_user.username = new_username
            classroom_user.email = new_email
            classroom_user.save()
            return JsonResponse({'success': True, 'message': '更新が成功しました。'})
        except ClassroomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': '教室が見つかりません。'})

    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

@csrf_exempt
def delete_classroom(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            classroom_user = ClassroomUser.objects.get(username=username)
            classroom_user.delete()
            return JsonResponse({'success': True, 'message': '削除しました。'})
        except ClassroomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': '教室が見つかりません。'})

    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

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
        current_manageruser= request.user

        # 指定された条件に従ってスケジュールをフィルタリング
        filters = {'student__manageruser': current_manageruser}
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
            'teacher_id': schedule.teacher.id,
            'student_id':schedule.student.id,
            'period_id':schedule.period.id,
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




@csrf_exempt
def update_class_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            student_id = data.get('student_id')
            teacher_id = data.get('teacher_id')
            
            period_id = data.get('period_id')
            date = data.get('date')

            # スケジュールを取得
            schedule = ClassSchedule.objects.get(id=schedule_id)

            # スケジュールデータを更新
            schedule.student = Student.objects.get(id=student_id)
            schedule.teacher = Teacher.objects.get(id=teacher_id)
            
            schedule.period = Period.objects.get(id=period_id)
            schedule.date = date
            schedule.save()

            return JsonResponse({'success': True, 'message': 'スケジュールが更新されました。'})
        except ClassSchedule.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'スケジュールが見つかりません。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

@csrf_exempt
def delete_class_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            ClassSchedule.objects.filter(id=schedule_id).delete()

            return JsonResponse({'success': True, 'message': 'スケジュールが削除されました。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})


def get_reports(request):
    user = request.user
    manager_classrooms = user.managerclassroom_set.all()
    classroom_users = [mc.classroom for mc in manager_classrooms]

    reports = Report.objects.filter(classroomuser__in=classroom_users, student__manageruser=user).order_by('-posted_at')

    report_data = []
    for report in reports:
        report_data.append({
            'name': report.student.name,
            'flag': '未承認' if report.flag else '承認済み',
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
            logged_in_user = request.user  # 現在のログインユーザーを取得
            
            # レポートを更新
            report.managermessage = managermessage
            report.teachermessage = teachermessage
            report.flag = False
            report.save()
            
            # メール送信の条件を確認
            if logged_in_user.email_setting:
                recipient_email = report.student.mail
                email_subject = "生徒の成績レポート"
                email_message = (
                    f"保護者様、\n\n"
                    f"{report.student.name}さんのレポートをご確認ください:\n"
                    f"出席状況: {report.attendance}\n"
                    f"遅刻: {report.behindtime}\n"
                    f"早退: {report.earlytime}\n"
                    f"姿勢: {report.poster}\n"
                    f"理解度: {report.understand}\n"
                    f"達成度: {report.achievement}\n"
                    f"教師からのメッセージ: {teachermessage}\n"
                    f"管理者からのメッセージ: {managermessage}\n"
                    f"次回の授業: {report.nextlesson}\n"
                    f"宿題: {report.homework}\n"
                    f"\nよろしくお願いします。\n"
                    f"{logged_in_user.get_full_name()}"
                )
                
                send_email_to_parent(logged_in_user.send_email_address, recipient_email, email_subject, email_message)
            
            return JsonResponse({'success': True})
        except Report.DoesNotExist:
            return JsonResponse({'success': False})
    
    return JsonResponse({'success': False})

def send_email_to_parent(sender_email, recipient_email, subject, message):
    try:
        print(sender_email)
        send_mail(
            subject,
            message,
            sender_email,
            [recipient_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"メール送信中にエラーが発生しました: {e}")

def update_report(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        try:
            # レポートを取得
            report = Report.objects.get(id=report_id)
            # フォームからのデータを使用して属性を更新
            report.attendance = request.POST.get('attendance', report.attendance)
            report.behindtime = request.POST.get('behindtime', report.behindtime)
            report.earlytime = request.POST.get('earlytime', report.earlytime)
            report.achievement = request.POST.get('achievement', report.achievement)
            report.poster = request.POST.get('poster', report.poster)
            report.understand = request.POST.get('understand', report.understand)
            report.parentsmessage = request.POST.get('parentsmessage', report.parentsmessage)
            report.nextlesson = request.POST.get('nextlesson', report.nextlesson)
            report.homework = request.POST.get('homework', report.homework)
            report.teachermessage = request.POST.get('teachermessage', report.teachermessage)
            # データベースに保存
            report.save()

            return JsonResponse({'success': True})
        except Report.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'レポートが存在しません。'})

    return JsonResponse({'success': False, 'error': '無効なリクエストです。'})

def get_report_detail(request):
    report_id = request.GET.get('report_id')
    try:
        report = Report.objects.select_related('student').get(id=report_id)  # studentをprefetch
        student = report.student  # 学生情報の取得
        student_school = StudentSchool.objects.filter(student=student).first()
        school_name=School.objects.get(id=student_school.school.id)
        report_data = {
            'attendance': report.attendance,
            'behindtime': report.behindtime,
            'earlytime': report.earlytime,
            'achievement': report.achievement,
            'poster': report.poster,
            'understand': report.understand,
            'parentsmessage': report.parentsmessage,
            'nextlesson': report.nextlesson,
            'homework': report.homework,
            'teachermessage': report.teachermessage,
            'student': {  # 学生情報の追加
                'name': student.name,
                'school': school_name.name if student_school else '',  # 仮にschoolプロパティがあると想定
                'stage': student_school.stage if student_school else '',  # 仮にstageプロパティがあると想定
                'grade': student_school.grade if student_school else '',  # 仮にgradeプロパティがあると想定
                'schoolclass': student_school.schoolclass if student_school else ''  # 仮にschoolclassプロパティがあると想定
            }
        }
        return JsonResponse({'success': True, 'report': report_data})
    except Report.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'レポートが存在しません。'})

def get_student_subjects(request, student_id):
    try:
        # 生徒に関連する最新のStudentSchoolを取得
        latest_school = StudentSchool.objects.filter(student_id=student_id).latest('posted_at')
        
        # SchoolSubjectを介して関連するSubjectのタイトルを取得
        subjects = SchoolSubject.objects.filter(school=latest_school).select_related('subject')
        
        # Subjectのタイトルリストを作成
        subject_titles = [subject.subject.title for subject in subjects if subject.subject]

        return JsonResponse({'subjects': subject_titles}, status=200)
    except StudentSchool.DoesNotExist:
        # StudentSchoolが存在しない場合は空のリストを返す
        return JsonResponse({'subjects': []}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@login_required
def update_settings(request):
    if request.method == 'POST':
        user = request.user
        email_address = request.POST.get('email_address', '')
        email_setting = request.POST.get('email_setting', 'false') == 'true'
        user.send_email_address = email_address
        user.email_setting = email_setting
        user.save()

        response_data = {
            'success': True,
            'message': 'Settings updated successfully!'
        }
        return JsonResponse(response_data)
    
    elif request.method == 'GET':
        user = request.user
        response_data = {
            'send_email_address': user.send_email_address,
            'email_setting': user.email_setting
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@csrf_exempt
def ajax_get_schoollist(request):
    # ログインしているマネージャーユーザーを取得
    manager_user = request.user
    
    # 対応する学校のリストを取得
    schools = School.objects.filter(manageruser=manager_user)
    
    school_list = [{
        'pk': school.pk,
        'fields': {
            'name': school.name,
            'stage': school.stage,
        }
    } for school in schools]
    
    return JsonResponse({'schools': school_list})

@csrf_exempt
def ajax_create_school(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        stage = data.get('stage')

        manager_user = request.user
        
        # 新しいSchoolインスタンスを作成
        school = School.objects.create(
            manageruser=manager_user,
            name=name,
            stage=stage
        )
        
        return JsonResponse({'success': True, 'message': '学校情報が保存されました。'})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

@csrf_exempt
def ajax_update_school(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        school_id = data.get('school_id')
        name = data.get('name')
        stage = data.get('stage')
        
        # 学校を取得または404エラーを返す
        school = get_object_or_404(School, pk=school_id, manageruser=request.user)
        
        # 学校情報を更新
        school.name = name
        school.stage = stage
        school.save()
        
        return JsonResponse({'success': True, 'message': '学校情報が更新されました。'})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

@csrf_exempt
def ajax_delete_school(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        school_id = data.get('school_id')
        
        # 学校を取得または404エラーを返す
        school = get_object_or_404(School, pk=school_id, manageruser=request.user)
        
        # 学校を削除
        school.delete()
        
        return JsonResponse({'success': True, 'message': '学校情報が削除されました。'})
    return JsonResponse({'success': False, 'message': '無効なリクエストです。'})

def get_schools_by_stage(request):
    selected_stage = request.GET.get('stage', '')
    manager_user = request.user  # Assuming ManagerUser is the logged-in user

    if request.user.is_authenticated:
        schools = School.objects.filter(stage=selected_stage, manageruser=manager_user)
        school_names = list(schools.values_list('name', flat=True))
        return JsonResponse({'schools': school_names})

    return JsonResponse({'schools': []})


from .models import ParentCategory, Category, EnglishWords
@csrf_exempt
def register_parent_category(request):
    if request.method == 'POST':
        title = request.POST.get('title', None)
        if title:
            ParentCategory.objects.create(title=title)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def register_category(request):
    if request.method == 'POST':
        title = request.POST.get('title', None)
        parent_id = request.POST.get('parent', None)
        parent = ParentCategory.objects.get(id=parent_id) if parent_id else None
        if title:
            Category.objects.create(title=title, parent=parent)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def register_english_word(request):
    if request.method == 'POST':
        word = request.POST.get('word', None)
        trans = request.POST.get('trans', None)
        category_id = request.POST.get('category', None)
        category = Category.objects.get(id=category_id) if category_id else None
        if word and trans:
            EnglishWords.objects.create(word=word, trans=trans, category=category)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def get_parent_categories(request):
    parent_categories = ParentCategory.objects.values()
    return JsonResponse(list(parent_categories), safe=False)

def get_categories(request):
    parent_id = request.GET.get('parent_id')
    
    if parent_id:
        categories = Category.objects.filter(parent_id=parent_id)
    else:
        categories = Category.objects.all()
        
    result = [{'id': c.id, 'title': c.title, 'parent_title': c.parent.title if c.parent else None} for c in categories]
    return JsonResponse(result, safe=False)

def get_english_words(request):
    category_id = request.GET.get('category_id')
    
    if category_id:
        english_words = EnglishWords.objects.filter(category_id=category_id)
    else:
        english_words = EnglishWords.objects.all()
        
    result = [{'word': w.word, 'trans': w.trans, 'category_title': w.category.title if w.category else None} for w in english_words]
    return JsonResponse(result, safe=False)
