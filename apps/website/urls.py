from django.urls import path
from . import views

urlpatterns = [
    path('', views.website_index, name='index'),
]