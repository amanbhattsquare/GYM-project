from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_new_member, name='add_new_member'),
    path('list/', views.member_list, name='member_list'),
    path('profile/<int:member_id>/', views.member_profile, name='member_profile'),
    path('edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('toggle-status/<int:member_id>/', views.toggle_member_status, name='toggle_member_status'),
    path('assign-membership/<int:member_id>/', views.assign_membership_plan, name='assign_membership_plan'),
    path('assign-pt-trainer/<int:member_id>/', views.assign_pt_trainer, name='assign_pt_trainer'),
    path('membership/freeze/<int:membership_id>/', views.freeze_membership, name='freeze_membership'),
    path('membership/unfreeze/<int:membership_id>/', views.unfreeze_membership, name='unfreeze_membership'),
    path('assign-diet-plan/<int:member_id>/', views.assign_diet_plan, name='assign_diet_plan'),
    path('assign-workout-plan/<int:member_id>/', views.assign_workout_plan, name='assign_workout_plan'),
]