from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from .models import Student
from .forms import StudentForm
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
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
    objects = Student(
                manageruser_id=request.user.id,
                name=request.GET.get('student_id'),
                mail=request.GET.get('student_id'),
                post=request.GET.get('student_id'),
                address=request.GET.get('student_id'),
                phone1=request.GET.get('student_id'),
                phone2=request.GET.get('student_id')
            )
    objects.save()
    return JsonResponse({'success': True, 'message': '学生が保存されました'})

def ajax_get_printstudentlist(request):
    objects = Student.objects.all().order_by('-posted_at')
    studentlist = serializers.serialize('python', objects)
    print(studentlist)
    data={'studentlist':studentlist}
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