from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('superadmin/login/', views.superadmin_login, name='superadmin_login'),
    path('logout/', views.user_logout, name='logout'),
]