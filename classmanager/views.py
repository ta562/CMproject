from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from .models import Student
from .forms import StudentForm
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import Student, StudentSchool,Subject,SchoolSubject
from accounts.models import ManagerClassroom
from django.views.decorators.http import require_GET
import json
from django.views.decorators.csrf import csrf_protect
class IndexView(TemplateView):
    template_name='index.html'
    
class LoginSelectView(TemplateView):
    template_name='loginselect.html'

class AssessmentListView(TemplateView):
    template_name='assessmentlist.html'

class StudentRegistrationView(TemplateView):
    template_name='studentregistration.html'


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


@csrf_protect   
def ajax_get_createstudentlist(request):
    if request.method == 'POST':
        print('test')
        json_body = request.body.decode("utf-8")
        print(json_body)
        body = json.loads(json_body)
        # Studentを作成
        new_student = Student.objects.create(
            manageruser=request.user,
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
        subject_ids = request.GET.get('student_subjects', '').split(',')
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
        try:
            student = Student.objects.get(pk=student_id)
            student.name = request.GET.get('student_name')
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

    studentlist = serializers.serialize('python', students)
    schoollist = serializers.serialize('python', schools)

    subjectlist = [
        {
            'school_id': school_subject.school.id,
            'subject_title': school_subject.subject.title,
        }
        for school_subject in subjects
    ]

    # すべての科目情報を整形
    all_subjectlist = [
        {'id': subject.id, 'title': subject.title}
        for subject in all_subjects
    ]

    data = {
        'studentlist': studentlist,
        'schoollist': schoollist,
        'subjectlist': subjectlist,
        'all_subjectlist': all_subjectlist  # すべての科目を追加
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
    
@csrf_protect    
def ajax_create_student_school(request):
    if request.method == 'POST':

        # try:
            print('test')
            json_body = request.body.decode("utf-8")
            print('test2')
            body = json.loads(json_body)
            student_id = body['student_id']
            print('test3')
            stage = body['student_stage']
            grade = body['student_grade']
            schoolclass = body['student_schoolclass']
            school = body['student_school']
            subjects_data = body['subjects', '[]']
            subjects_ids = body['subjects_data']

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

    #     except Student.DoesNotExist:
    #         return JsonResponse({'success': False, 'error': 'Student not found'})
    #     except Subject.DoesNotExist:
    #         return JsonResponse({'success': False, 'error': 'Subject not found'})
    #     except Exception as e:
    #         return JsonResponse({'success': False, 'error': str(e)})

    # return JsonResponse({'success': False, 'error': 'Invalid request method'})



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