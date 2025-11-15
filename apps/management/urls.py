from django.urls import path
from . import views

urlpatterns = [
    path('package-plans/', views.package_plans, name='package_plans'),
    path('package-plans/edit/<int:pk>/', views.edit_package_plan, name='edit_package_plan'),
    path('package-plans/delete/<int:pk>/', views.delete_package_plan, name='delete_package_plan'),
    path('diet-plans/', views.diet_plans, name='diet_plans'),
    path('diet-plans/edit/<int:pk>/', views.edit_diet_plan, name='edit_diet_plan'),
    path('diet-plans/delete/<int:pk>/', views.delete_diet_plan, name='delete_diet_plan'),
    path('workout-plans/', views.workout_plans, name='workout_plans'),
]