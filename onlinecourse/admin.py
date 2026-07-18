from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['choice_text', 'is_correct']
    verbose_name = 'Choice'
    verbose_name_plural = 'Choices'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['question_text', 'grade']
    show_change_link = True


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'lesson', 'grade']
    list_filter = ['lesson']


class LessonAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['title', 'course', 'order']


# Register your models here.
admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission)