from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class generalsetting(TemplateView):
    template_name = "settings/general_settings.html"