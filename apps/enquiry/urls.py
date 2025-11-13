from django.urls import path
from . import views

urlpatterns = [
    path('add-enquiry/', views.add_new_enquiry, name='add_new_enquiry'),
    path('enquiry-list/', views.enquiry_list, name='enquiry_list'),
    path('enquiry/<int:enquiry_id>/edit/', views.edit_enquiry, name='edit_enquiry'),
    path('enquiry/<int:enquiry_id>/delete/', views.delete_enquiry, name='delete_enquiry'),
]