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

]