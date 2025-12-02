from django.urls import path
from . import views

urlpatterns = [
    path('member-attendance/', views.member_attendance, name='member_attendance'),
    path('trainer-attendance/', views.trainer_attendance, name='trainer_attendance'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
]