from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path('submit/<int:exam_id>/', views.submit, name='submit'),
    path('show_exam_result/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),
]