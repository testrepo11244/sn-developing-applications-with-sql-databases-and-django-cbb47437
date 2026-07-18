from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
import logging
from datetime import datetime
from .models import Course, Enrollment, Question, Choice, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    submission = Submission.objects.create(enrollment=enrollment)
    
    selected_choices = request.POST.getlist('choice')
    
    for choice_id in selected_choices:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)
    
    submission.save()
    
    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', 
                                       args=(course_id, submission.id,)))


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_choices = submission.choices.all()
    
    total_score = 0
    max_score = 0
    
    question_results = []
    
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            max_score += question.grade
            
            correct_choices = question.choice_set.filter(is_correct=True)
            user_choices = selected_choices.filter(question=question)
            
            is_correct = set(correct_choices) == set(user_choices) and len(user_choices) > 0
            
            if is_correct:
                total_score += question.grade
            
            question_results.append({
                'question': question,
                'correct_choices': correct_choices,
                'user_choices': user_choices,
                'is_correct': is_correct
            })
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
        'question_results': question_results,
        'selected_choices': selected_choices
    }
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)