from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_gym, name='add_gym'),
    path('', views.gym_list, name='dashboard'),
    path('gym_list', views.gym_list, name='gym_list'),
    path('update/<int:gym_id>/', views.update_gym, name='update_gym'),
    path('delete/<int:gym_id>/', views.delete_gym, name='delete_gym'),
    path('create_admin/<int:gym_id>/', views.create_gym_admin, name='create_gym_admin'),
]