from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from .models import Student
from .forms import StudentForm
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import Student, StudentSchool
from django.views.decorators.http import require_GET
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



def ajax_get_createstudentlist(request):
    if request.method == 'GET':
        # Studentを作成
        new_student = Student.objects.create(
            manageruser=request.user,  # ForeignKeyに直接Userオブジェクトを渡す場合
            name=request.GET.get('student_name'),
            mail=request.GET.get('student_mail'),
            post=request.GET.get('student_post'),
            address=request.GET.get('student_address'),
            phone1=request.GET.get('student_tel1'),
            phone2=request.GET.get('student_tel2')
        )
        
        # StudentSchoolを関連付けて作成
        StudentSchool.objects.create(
            student=new_student,  # 先ほど作成したStudentをForeignKeyとして設定
            school=request.GET.get('student_school'),
            stage=request.GET.get('student_stage'),
            grade=request.GET.get('student_grade'),
            schoolclass=request.GET.get('student_schoolclass')
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
    students = Student.objects.all().order_by('-posted_at').filter(manageruser_id=request.user)
    schools = StudentSchool.objects.all().order_by('-posted_at')
    studentlist = serializers.serialize('python', students)
    schoollist=serializers.serialize('python', schools)

    data={'studentlist':studentlist,'schoollist':schoollist}
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
        School = StudentSchool.objects.get(pk=school_id)
            # 学校情報を更新または新規作成
        School.stage=stage
        School.grade=grade
        School.schoolclass=schoolclass
        School.school=school
        School.save()
        return JsonResponse({'success': True})
     

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})





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

            student = Student.objects.get(pk=student_id)

            # 新しいStudentSchoolインスタンスを作成
            StudentSchool.objects.create(
                student=student,
                stage=stage,
                grade=grade,
                schoolclass=schoolclass,
                school=school
            )

            return JsonResponse({'success': True})

        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
# class StudentListView(CreateView, ListView):
#     def get(self, request, *args, **kwargs):
#         object = Student.objects.all().order_by('-posted_at')  
#         context = {'object': object}
#         return render(request, 'studentlist.html', context)

#     def post(self, request, *args, **kwargs):
#         if 'delete_student_id' in request.POST:
#             # 削除処理
#             student_id = request.POST['delete_student_id']
#             try:
#                 student = Student.objects.get(id=student_id)
#                 student.delete()
#             except Student.DoesNotExist:
#                 # 学生が存在しない場合の処理
#                 pass
#         else:
#             # 作成処理
#             obj = Student(
#                 manageruser_id=self.request.user.id,
#                 name=request.POST['form_student_name'],
#                 mail=request.POST['form_student_mail'],
#                 post=request.POST['form_student_post'],
#                 address=request.POST['form_student_address'],
#                 phone1=request.POST['form_student_tel1'],
#                 phone2=request.POST['form_student_tel2']
#             )
#             obj.save()
        
#         # リストを更新
#         object = Student.objects.all().order_by('-posted_at') 
#         context = {'object': object}
#         return render(request, 'studentlist.html', context)

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