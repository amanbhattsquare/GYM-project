from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from apps.superadmin.models import Gym
from .models import PaymentSetting
from .forms import PaymentSettingForm
from django.contrib import messages

# Create your views here.

class generalsetting(TemplateView):
    template_name = "settings/general_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gym = getattr(self.request, 'gym', None)
        context['gym'] = gym
        return context

class PaymentSettingView(View):
    template_name = 'settings/payment_setting.html'

    def get(self, request, *args, **kwargs):
        payment_settings = PaymentSetting.objects.first()
        form = PaymentSettingForm(instance=payment_settings)
        return render(request, self.template_name, {'form': form, 'payment_settings': payment_settings})

    def post(self, request, *args, **kwargs):
        payment_settings = PaymentSetting.objects.first()
        form = PaymentSettingForm(request.POST, request.FILES, instance=payment_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment settings saved successfully.')
            return redirect('settings:payment_setting')
        return render(request, self.template_name, {'form': form, 'payment_settings': payment_settings})