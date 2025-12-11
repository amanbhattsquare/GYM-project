from django.urls import path
from . import views

# app_name = 'settings' 

urlpatterns = [
    path('general/', views.generalsetting.as_view(), name='general_settings'),
]