from django.urls import path
from . import views

urlpatterns = [
    path('member-registration/', views.add_new_member, name='add_new_member'),
    path('member-list/', views.member_list, name='member_list'),
    path('member/<int:member_id>/', views.member_profile, name='member_profile'),
    path('member/<int:member_id>/edit/', views.edit_member, name='edit_member'),
    path('member/<int:member_id>/delete/', views.delete_member, name='delete_member'),
    path('member/<int:member_id>/assign-plan/', views.assign_membership_plan, name='assign_membership_plan'),

]