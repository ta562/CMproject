from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from classmanager.models import Student, StudentSchool,Subject,SchoolSubject,Teacher,ClassSchedule,Period
from accounts.models import ManagerClassroom
from accountsclassroom.models import ClassroomUser
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
class ReportCreateView(TemplateView):
    template_name='reportcreate.html'

class TeacherSelectView(TemplateView):
    template_name='teacherselect.html'

@csrf_exempt
def check_teacher_id(request):
    if request.method == 'POST':
        if request.session.get('class_room_user') == None:
            print('test')
            return JsonResponse({'success': False, 'message': 'ユーザーが認証されていません。'})
        
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id', None)
        
        if teacher_id:
            
            print('test2')
            # ログインユーザーのクラスルームを取得
            classroom_user = request.session['class_room_user']
            print(classroom_user)
            try:
                teacher = Teacher.objects.get(teacher_id=teacher_id, classroomuser=classroom_user['id'])
                return JsonResponse({'success': True, 'teacher_id': teacher_id})
            except Teacher.DoesNotExist:
                return JsonResponse({'success': False, 'message': '教師IDが見つかりません。'})
    
    return JsonResponse({'success': False, 'message': '不正なリクエストです。'})
class ReportCreateView(View):
    template_name = 'reportcreate.html'

    def get(self, request, teacher_id):
        classroom_user = request.session['class_room_user']
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id, classroomuser=classroom_user['id'])
            context = {'teacher_name': teacher.name,
                       'teacher_id': teacher.teacher_id
                       }
        except Teacher.DoesNotExist:
            context = {'teacher_name': '不明な教師'}

        return render(request, self.template_name, context)

def get_teacher_and_schedules(request):
    teacher_id = request.GET.get('teacher_id', None)
    if teacher_id is None:
        return JsonResponse({'error': 'Teacher ID not provided'}, status=400)
    
    try:
        # Get the teacher
        teacher = Teacher.objects.get(teacher_id=teacher_id)
        
        # Get the current date
        today = timezone.now().date()
        
        # Filter schedules for the current day and related teacher
        schedules = ClassSchedule.objects.filter(date=today, teacher=teacher).select_related('student')

        # Collect student and school data
        student_data = []
        for schedule in schedules:
            student = schedule.student
            student_school = StudentSchool.objects.filter(student=student).first()
            student_dict = {
                'name': student.name,
                'school': student_school.school if student_school else '',
                'stage': student_school.stage if student_school else '',
                'grade': student_school.grade if student_school else '',
                'schoolclass': student_school.schoolclass if student_school else '',
            }
            student_data.append(student_dict)
        
        teacher_data = serializers.serialize('python', [teacher], fields=('name'))

        return JsonResponse({
            'teacher_name': teacher_data[0]['fields']['name'],
            'students': student_data
        }, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Teacher not found'}, status=404)