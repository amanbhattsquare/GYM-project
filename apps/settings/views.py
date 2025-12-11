from django.shortcuts import render
from django.views.generic import TemplateView
from apps.superadmin.models import Gym

# Create your views here.

class generalsetting(TemplateView):
    template_name = "settings/general_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gym = getattr(self.request, 'gym', None)
        context['gym'] = gym
        return context