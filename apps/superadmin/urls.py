from django.urls import path
from . import views

urlpatterns = [
    path('add_gym/', views.add_gym, name='add_gym'),
    path('', views.gym_list, name='dashboard'),
    path('gym_list', views.gym_list, name='gym_list'),
    path('update/<int:gym_id>/', views.update_gym, name='update_gym'),
    path('delete/<int:gym_id>/', views.delete_gym, name='delete_gym'),
    path('create_admin/<int:gym_id>/', views.create_gym_admin, name='create_gym_admin'),
    path('gym_profile/<int:gym_id>/', views.gym_profile, name='gym_profile'),
    path('reset_admin_password/<int:admin_id>/', views.reset_admin_password, name='reset_admin_password'),
    path('subscription_plans/', views.subscription_plan_list, name='subscription_plan_list'),
    path('subscription_plans/add/', views.add_subscription_plan, name='add_subscription_plan'),
    path('subscription_plans/update/<int:plan_id>/', views.update_subscription_plan, name='update_subscription_plan'),
    path('subscription_plans/delete/<int:plan_id>/', views.delete_subscription_plan, name='delete_subscription_plan'),
]