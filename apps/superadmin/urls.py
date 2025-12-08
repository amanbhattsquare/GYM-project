from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('gyms/', views.gym_list, name='gym_list'),
    path('gyms/add/', views.add_gym, name='add_gym'),
    path('gyms/update/<int:gym_id>/', views.update_gym, name='update_gym'),
    path('gyms/delete/<int:gym_id>/', views.delete_gym, name='delete_gym'),
]