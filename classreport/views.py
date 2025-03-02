from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView,View,CreateView,ListView
from django.http import JsonResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from classmanager.models import TransGameScore,EnglishScore,EnglishWords,ParentCategory,Category,School,StudentPhone,Student, StudentSchool,Subject,SchoolSubject,Teacher,ClassSchedule,Period,Report
from accounts.models import ManagerClassroom
from accountsclassroom.models import ClassroomUser
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt

class ReportCreateView(TemplateView):
    template_name='reportcreate.html'


class TeacherSelectView(TemplateView):
    
    template_name='teacherselect.html'
    def get(self, request):
        classroom_user = request.session.get('class_room_user')
        if classroom_user is None:
            return redirect("accountsclassroom:login_classroom")
        return render(request, self.template_name)

 

class TypingPracticeView(TemplateView):
    template_name='typingpractice.html'
    def get(self, request):
        classroom_user = request.session.get('class_room_user')
        if classroom_user is None:
            return redirect("accountsclassroom:login_classroom_game")
        return render(request, self.template_name)
class TransPracticeView(TemplateView):
    template_name='transpractice.html'
    def get(self, request):
        classroom_user = request.session.get('class_room_user')
        if classroom_user is None:
            return redirect("accountsclassroom:login_classroom_game")
        return render(request, self.template_name)

class GameSelectView(TemplateView):
    template_name='gameselect.html'
    def get(self, request):
        classroom_user = request.session.get('class_room_user')
        if classroom_user is None:
            return redirect("accountsclassroom:login_classroom_game")
        return render(request, self.template_name)

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

    def get(self, request, teacher_id, period_id):
        classroom_user = request.session['class_room_user']
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id, classroomuser=classroom_user['id'])
            context = {'teacher_name': teacher.name,
                       'teacher_id': teacher.teacher_id,
                       'period_id': period_id
                       }
        except Teacher.DoesNotExist:
            context = {'teacher_name': '不明な教師'}

        return render(request, self.template_name, context)

def get_teacher_and_schedules(request):
    teacher_id = request.GET.get('teacher_id', None)
    period_id = request.GET.get('period_id', None)
    classroom_user = request.session['class_room_user']
    if teacher_id is None:
        return JsonResponse({'error': 'Teacher ID not provided'}, status=400)
    
    try:
        # Get the teacher
        teacher = Teacher.objects.get(teacher_id=teacher_id)
        
        # Get the current date
        today = timezone.now().date()
        period=Period.objects.get(id=period_id)
        print(today)
        # Filter schedules for the current day and related teacher
        schedules = ClassSchedule.objects.filter(date=today, teacher=teacher,period=period_id,classroomuser_id=classroom_user['id']).select_related('student')

        # Collect student and school data
        student_data = []
        for schedule in schedules:
            student = schedule.student
            latest_report = Report.objects.filter(student=student).order_by('-date').first()
            student_school = StudentSchool.objects.filter(student=student).first()
            schoolname=School.objects.get(id=student_school.school_id)
            student_dict = {
                'schedule_id':schedule.id,
                
                'student_id':student.id,
                'name': student.name,
                'school': schoolname.name,
                'stage': student_school.stage if student_school else '',
                'grade': student_school.grade if student_school else '',
                'schoolclass': student_school.schoolclass if student_school else '',

                'recent_teachermessage': latest_report.teachermessage if latest_report else "",
                'recent_managermessage': latest_report.managermessage if latest_report else "",
                'recent_homework': latest_report.homework if latest_report else "",
                'recent_nextlesson': latest_report.nextlesson if latest_report else "",
                'schedule_flag': schedule.flag 

            }
            student_data.append(student_dict)
        
        teacher_data = serializers.serialize('python', [teacher], fields=('name'))

        return JsonResponse({
            'teacher_name': teacher_data[0]['fields']['name'],
            'period_title': period.title,
            'students': student_data
        }, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Teacher not found'}, status=404)
    

def get_period_options(request):
    if request.session.get('class_room_user') is None:
        return JsonResponse({'success': False, 'message': 'ユーザーが認証されていません。'})
    
    classroom_user_id = request.session['class_room_user']['id']
    
    try:
        manager_classroom = ManagerClassroom.objects.get(classroom_id=classroom_user_id)
        periods = Period.objects.filter(manageruser=manager_classroom.manager)
        
        period_options = [
            {
                'id': period.id,
                'title': period.title,
                'start_time': period.start_time.strftime('%H:%M'),
                'end_time': period.end_time.strftime('%H:%M')
            }
            for period in periods
        ]
        
        return JsonResponse({'success': True, 'periods': period_options})
        
    except ManagerClassroom.DoesNotExist:
        return JsonResponse({'success': False, 'message': '管理クラスルームが見つかりません。'})
    


def save_report(request):
    if request.method == 'POST':
        
        try:
            student_id = request.POST.get('student_id')
            teacher_id = request.POST.get('teacher_id')
            classroomuser_id = request.session['class_room_user']['id']
            period_id = request.POST.get('period_id')

            student = Student.objects.get(id=student_id)
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            period = Period.objects.get(id=period_id)
            schedule_id = request.POST.get('schedule_id')
            print('fjdk')
            report, created = Report.objects.get_or_create(
                student=student,
                teacher=teacher,
                classroomuser_id=classroomuser_id,
                period=period,
                date=timezone.now().date(),
                defaults={
                    'behindtime': request.POST.get('behindtime'),
                    'earlytime': request.POST.get('earlytime'),
                    'managermessage': '',  # 必要なら追加のロジック
                    'teachermessage': request.POST.get('teachermessage'),
                    'nextlesson': request.POST.get('nextlesson'),
                    'homework': request.POST.get('homework'),
                    'poster': request.POST.get('poster'),
                    'understand': request.POST.get('understand'),
                    'achievement': request.POST.get('achievement'),
                    'attendance': request.POST.get('attendance'),
                    'parentsmessage': request.POST.get('parentsmessage')
                }
               
            )
            print(report.id)
            if not created:
                # Update existing report instead
                report.behindtime = request.POST.get('behindtime')
                report.earlytime = request.POST.get('earlytime')
                report.teachermessage = request.POST.get('teachermessage')
                report.nextlesson = request.POST.get('nextlesson')
                report.homework = request.POST.get('homework')
                report.poster = request.POST.get('poster')
                report.understand = request.POST.get('understand')
                report.achievement = request.POST.get('achievement')
                report.attendance = request.POST.get('attendance')
                report.parentsmessage = request.POST.get('parentsmessage')
                report.save()
                print()
            try:
                class_schedule = ClassSchedule.objects.get(id=schedule_id)
                class_schedule.flag = False
                class_schedule.save()
            except ClassSchedule.DoesNotExist:
                return JsonResponse({'error': 'Schedule not found'}, status=404)


            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_class_schedules(request):
    try:
        classroomuser_id = request.session['class_room_user']['id']
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

def get_student_subjects(request, student_id):
    print('get_student_subjects')
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

def ajax_get_printlist(request):
        classroomuser_id = request.session['class_room_user']['id']
        manager=ManagerClassroom.objects.get(classroom_id=classroomuser_id)
        print(manager.manager)
        categorys = request.GET.get('pk')
        english_id=list(EnglishWords.objects.filter(category=categorys,manageruser=manager.manager).values_list('id', flat=True))
        english_text=list(EnglishWords.objects.filter(category=categorys,manageruser=manager.manager).values_list('word', flat=True))
        trans_text=list(EnglishWords.objects.filter(category=categorys,manageruser=manager.manager).values_list('trans', flat=True))
        category_text=list(Category.objects.filter(parent=categorys,manageruser=manager.manager).values_list('title',flat=True))
        category_id=list(Category.objects.filter(parent=categorys,manageruser=manager.manager).values_list('id',flat=True))
        parentcategory_text=list(ParentCategory.objects.filter(manageruser=manager.manager).values_list('title',flat=True))
        parentcategory_id=list(ParentCategory.objects.filter(manageruser=manager.manager).values_list('id',flat=True))
       
      
    # [ {'name': 'サッカー', 'pk': '3'}, {...}, {...} ] という感じのリストになる
        data ={'message':english_text,'message2':trans_text,'message3':category_text,'message4':parentcategory_text,'message5':parentcategory_id,'message6':category_id,'message7':english_id,}
    # JSONで返す
        return JsonResponse(data)



class TypingView(TemplateView):
    template_name='typing.html'
    def get(self, request, **kwargs):
        name=Student.objects.values_list('name',flat=True).get(student_id=kwargs['pk'])
        context = {
            'pk': kwargs['pk'], 
            'name':name,        
        }
        return self.render_to_response(context)


class TransquizView(TemplateView):
    template_name='transquiz.html'
    def get(self, request, **kwargs):
        name=Student.objects.values_list('name',flat=True).get(student_id=kwargs['pk'])
        context = {
            'pk': kwargs['pk'], 
            'name':name,        
        }
        return self.render_to_response(context)
    
class MypageTypingView(TemplateView):
    template_name='mypagetyping.html'
    def get(self, request, **kwargs):
        name=Student.objects.values_list('name',flat=True).get(student_id=kwargs['pk'])
        context = {
            'pk': kwargs['pk'], 
            'name':name,        
        }
        return self.render_to_response(context)


class MypageTransView(TemplateView):
    template_name='mypagetrans.html'
    def get(self, request, **kwargs):
        name=Student.objects.values_list('name',flat=True).get(student_id=kwargs['pk'])
        context = {
            'pk': kwargs['pk'], 
            'name':name,        
        }
        return self.render_to_response(context)

@csrf_exempt 
def check_student_exists(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id', None)
        current_user = request.session['class_room_user']['id'] # Adjust based on your auth setup
        try:
            student = Student.objects.get(student_id=student_id, classroomuser_id=current_user)
            return JsonResponse({'exists': True})
        except Student.DoesNotExist:
            return JsonResponse({'exists': False})
    return HttpResponseBadRequest('Invalid Request')

    
@csrf_exempt
def game_clear(request):
    if request.method == "POST":
        try:
            category_id = request.POST.get("category_id")  # フロントエンドからカテゴリIDを受け取る
            clear_time = request.POST.get("clear_time") 
            studentid = request.POST.get("student_id")  # クリアタイムを受け取る

            print(category_id)
            print(clear_time)
            print(studentid)

            # Student の取得
            student = Student.objects.filter(student_id=studentid).first()
            if not student:
                return JsonResponse({"error": "Student not found"}, status=400)

            # Category の取得
            category = Category.objects.filter(pk=category_id).first()
            if not category:
                return JsonResponse({"error": "Category not found"}, status=400)

            # 既存のスコアデータがあるか確認
            score_entry = EnglishScore.objects.filter(student=student, category=category).first()
            clear_time_value = float(clear_time)
            current_cleartime_value = float(score_entry.cleartime)
            message = f"クリアおめでとう！クリアタイム: {clear_time}秒！"
            
            if score_entry:
                print('アップデート')
            
                # すでに存在する場合、score を +1 し、cleartime を更新
                print(score_entry.cleartime+'and'+clear_time)
                if current_cleartime_value > clear_time_value:
                    score_entry.cleartime = clear_time  # クリアタイムを更新
                    print('タイム更新')
                    score_entry.score += 1
                    score_entry.save()
                    message = f"おめでとう！自己ベスト更新！🎉 新しいクリアタイム: {clear_time}秒"
                else:
                    score_entry.score += 1
                    score_entry.save()
                
            else:
                # 存在しない場合は新規作成
                score_entry = EnglishScore.objects.create(
                    student=student,
                    category=category,
                    score=1,
                    cleartime=clear_time
                )
                message =f"初クリアおめでとう！🎉クリアタイム: {clear_time}秒"

            return JsonResponse({'success': True,"message": message, "score": score_entry.score, "cleartime": score_entry.cleartime}, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def get_parent_categories_game(request):
        classroomuser_id = request.session['class_room_user']['id']
        manager=ManagerClassroom.objects.get(classroom_id=classroomuser_id)
        parent_categories = ParentCategory.objects.filter(manageruser=manager.manager)
   
        data = [{"id": p.id, "title": p.title} for p in parent_categories]
        return JsonResponse({"parent_categories": data})


def get_categories_game(request):
        classroomuser_id = request.session['class_room_user']['id']
        manager=ManagerClassroom.objects.get(classroom_id=classroomuser_id)
        parent_id = request.GET.get("parent_id")
        categories = Category.objects.filter(parent_id=parent_id , manageruser=manager.manager)
    
        data = [{"id": c.id, "title": c.title} for c in categories]
        print(data)
        return JsonResponse({"categories": data})


def get_english_words_game(request):
    """ 選択された Category に紐づく EnglishWords を取得 """
    category_id = request.GET.get("category_id")
    words = EnglishWords.objects.filter(category_id=category_id)
    
    data = [{"word": w.word, "trans": w.trans} for w in words]
    return JsonResponse({"words": data})

def get_random_wrong_trans(request):
    """ Obtain three random incorrect translations. """
    category_id = request.GET.get("category_id")
    current_word_id = request.GET.get("current_word_id")

    # Exclude the current word and category to ensure wrong translations are incorrect
    wrong_translations = (
        EnglishWords.objects
        .exclude(category_id=category_id)
        .exclude(id=current_word_id)
        .order_by('?')[:3]  # Get three random incorrect translations
    )

    # If fewer than 3 wrong translations are available, add default option
    wrong_trans_list = [wt.trans for wt in wrong_translations]
    while len(wrong_trans_list) < 3:
        wrong_trans_list.append("誤訳")

    return JsonResponse({"trans": wrong_trans_list})

@csrf_exempt
def trans_game_clear(request):
    if request.method == "POST":
        try:
            student_id = request.POST.get("student_id")
            category_id = request.POST.get("category_id")
            new_cleartime = int(request.POST.get("cleartime"))

            # Student と Category の取得
            student = Student.objects.get(student_id=student_id)
            category = Category.objects.get(id=category_id)
            score_entry = TransGameScore.objects.filter(student=student, category=category).first()
            if score_entry:
                if int(score_entry.cleartime) > new_cleartime:
                    score_entry.cleartime=new_cleartime
                    score_entry.score += 1
                    score_entry.save()
                    message = "クリア回数が更新されました！"
                else:
                    score_entry.score += 1
                    score_entry.save()
                    message = "クリア回数が更新されました！"


            else:
                # 存在しない場合は新規作成
                TransGameScore.objects.create(
                    student=student,
                    category=category,
                    score=1,
                    cleartime=new_cleartime
                )
                message = "クリアデータが保存されました！"

            return JsonResponse({'success': True, 'message': message}, status=200)

        except Student.DoesNotExist:
            return JsonResponse({"error": "生徒が見つかりません"}, status=400)
        except Category.DoesNotExist:
            return JsonResponse({"error": "カテゴリが見つかりません"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "不正なリクエストです"}, status=400)

def student_scores_view(request, student_id):
    # EnglishScoreを取得
    english_scores = EnglishScore.objects.filter(student__student_id=student_id)
    
    # カテゴリごとにグループ化して辞書に整理
    english_data = {}
    for score in english_scores:
        parent_title = score.category.parent.title if score.category.parent else 'No Parent'
        if parent_title not in english_data:
            english_data[parent_title] = []
        english_data[parent_title].append({
            'category_title': score.category.title,
            'score': score.score,
            'cleartime': score.cleartime
        })

    return JsonResponse({'english_data': english_data})

def student_scores_trans_view(request, student_id):
    # EnglishScoreを取得
    english_scores = TransGameScore.objects.filter(student__student_id=student_id)
    
    # カテゴリごとにグループ化して辞書に整理
    english_data = {}
    for score in english_scores:
        parent_title = score.category.parent.title if score.category.parent else 'No Parent'
        if parent_title not in english_data:
            english_data[parent_title] = []
        english_data[parent_title].append({
            'category_title': score.category.title,
            'score': score.score,
            'cleartime': score.cleartime
        })

    return JsonResponse({'english_data': english_data})