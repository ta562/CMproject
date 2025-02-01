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


class ReportCreateView(TemplateView):
    template_name='reportcreate.html'

class TeacherSelectView(TemplateView):
    template_name='teacherselect.html'

@csrf_exempt
def check_teacher_id(request):
    if request.method == 'POST':
        
        # if not request.user.is_authenticated:
        #     print('test')
        #     return JsonResponse({'success': False, 'message': 'ユーザーが認証されていません。'})
        
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id', None)
        
        if teacher_id:
            print('test2')
            # ログインユーザーのクラスルームを取得
            classroom_user = request.user
            print(classroom_user+'test')
            try:
                teacher = Teacher.objects.get(teacher_id=teacher_id, classroomuser=classroom_user)
                return JsonResponse({'success': True, 'teacher_id': teacher_id})
            except Teacher.DoesNotExist:
                return JsonResponse({'success': False, 'message': '教師IDが見つかりません。'})
    
    return JsonResponse({'success': False, 'message': '不正なリクエストです。'})

class ReportCreateView(View):
    template_name = 'reportcreate.html'

    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id, classroomuser=request.user.classroomuser)
            context = {'teacher_name': teacher.name}
        except Teacher.DoesNotExist:
            context = {'teacher_name': '不明な教師'}

        return render(request, self.template_name, context)