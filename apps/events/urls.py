from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('<int:event_id>/cancel/', views.cancel_event, name='cancel_event'),
    path('<int:event_id>/duplicate/', views.duplicate_event, name='duplicate_event'),
    path('<int:event_id>/export/', views.export_attendees, name='export_attendees'),
    path('<int:event_id>/notify/', views.notify_members, name='notify_members'),
]